#!/usr/bin/env python3
"""
Resolve URLs finais para cada curso diretamente do banco SQLite.

Funciona em cima de um banco temporário (ex.: tmp_instituicoes/guia.sqlite), adiciona
as colunas se não existirem (link_resolvido, processado_resolver) em graduacao,
especializacao e pos, e preenche a URL final resolvida a partir de uma busca
"I'm Feeling Lucky" no Google combinando instituição + curso + município.

Uso básico:
  python scripts/resolver_instituicoes.py --db tmp_instituicoes/guia.sqlite --tables all --start 1 --end 500 --sleep 1.5

Observação: o Google pode impor limites; aumente o intervalo base (--sleep),
deixe o jitter automático trabalhar, ou processe em lotes menores se notar bloqueios.
"""
from __future__ import annotations

import argparse
import random
import sqlite3
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, quote_plus, urlparse

import requests
from requests import Response

TABLE_CONFIG = {
  "graduacao": {"curso_col": "nome_curso", "municipio_col": "municipio"},
  "especializacao": {"curso_col": "nome_especializacao", "municipio_col": "municipio"},
  "pos": {"curso_col": "nome_programa", "municipio_col": "municipio"},
}

LINK_COL = "link_resolvido"
FLAG_COL = "processado_resolver"


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Resolve URLs finais via Google Lucky direto do SQLite.")
  parser.add_argument("--db", type=Path, default=Path("tmp_instituicoes/guia.sqlite"), help="Caminho do banco SQLite temporário.")
  parser.add_argument(
    "--tables",
    type=str,
    default="all",
    help="Tabelas para processar: graduacao,especializacao,pos ou all.",
  )
  parser.add_argument("--start", type=int, default=1, help="Primeira linha (1-based) de cada tabela.")
  parser.add_argument("--end", type=int, default=None, help="Última linha (1-based) de cada tabela (inclusive).")
  parser.add_argument("--sleep", type=float, default=1.0, help="Segundos de espera entre requisições.")
  parser.add_argument("--retries", type=int, default=3, help="Tentativas por URL.")
  parser.add_argument(
    "--include-processed",
    action="store_true",
    help="Se definido, processa também registros já marcados como processados.",
  )
  return parser.parse_args()


def jitter_sleep(base: float) -> float:
  """Retorna um intervalo aleatório baseado no valor base (±50%)."""
  return random.uniform(base * 0.5, base * 1.5)


def ensure_columns(conn: sqlite3.Connection, table: str) -> None:
  cur = conn.execute(f"PRAGMA table_info({table})")
  cols = {row[1] for row in cur.fetchall()}
  if LINK_COL not in cols:
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {LINK_COL} TEXT")
  if FLAG_COL not in cols:
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {FLAG_COL} INTEGER DEFAULT 0")
  conn.commit()


def select_rows(
  conn: sqlite3.Connection,
  table: str,
  curso_col: str,
  municipio_col: str,
  start: int,
  end: Optional[int],
  include_processed: bool,
) -> List[Tuple[int, str, str, str]]:
  where = f"WHERE {FLAG_COL} = 0 OR {FLAG_COL} IS NULL" if not include_processed else ""
  limit_clause = ""
  params: List[int] = []
  # 1-based to offset
  offset = max(start - 1, 0)
  if end is not None and end >= start:
    limit = end - start + 1
    limit_clause = "LIMIT ? OFFSET ?"
    params.extend([limit, offset])
  else:
    limit_clause = "LIMIT -1 OFFSET ?"
    params.append(offset)

  query = f"""
    SELECT rowid, nome_ies, {curso_col}, {municipio_col}
    FROM {table}
    {where}
    ORDER BY rowid
    {limit_clause};
  """
  cur = conn.execute(query, params)
  return [(row[0], row[1], row[2], row[3]) for row in cur.fetchall()]


def resolve_url(url: str, session: requests.Session, retries: int = 3, sleep: float = 1.0) -> str:
  headers = {
    "User-Agent": random_user_agent(),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
  }
  for attempt in range(1, retries + 1):
    try:
      resp: Response = session.get(url, allow_redirects=True, timeout=8, headers=headers)
      if resp.history:
        return clean_redirect(resp.url)
      if 300 <= resp.status_code < 400:
        return clean_redirect(resp.headers.get("Location", ""))
      if resp.status_code == 200:
        return clean_redirect(resp.url)
    except requests.RequestException:
      pass
    time.sleep(jitter_sleep(sleep))
  return ""


def clean_redirect(url: Optional[str]) -> str:
  if not url:
    return ""
  parsed = urlparse(url)
  if "google.com" in parsed.netloc and parsed.path.startswith("/url"):
    qs = parse_qs(parsed.query)
    if "q" in qs:
      return qs["q"][0]
  return url


def random_user_agent() -> str:
  agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
  ]
  return random.choice(agents)


def update_row(conn: sqlite3.Connection, table: str, rowid: int, final_url: str) -> None:
  conn.execute(
    f"UPDATE {table} SET {LINK_COL} = ?, {FLAG_COL} = 1 WHERE rowid = ?",
    (final_url, rowid),
  )
  conn.commit()


def table_list(arg_tables: str) -> Iterable[str]:
  if arg_tables.strip().lower() == "all":
    return TABLE_CONFIG.keys()
  parts = [t.strip() for t in arg_tables.split(",") if t.strip()]
  return [p for p in parts if p in TABLE_CONFIG]


def main():
  args = parse_args()
  db_path = args.db
  if not db_path.exists():
    raise SystemExit(f"Banco não encontrado: {db_path}")

  conn = sqlite3.connect(db_path)
  session = requests.Session()

  for table in table_list(args.tables):
    cfg = TABLE_CONFIG[table]
    ensure_columns(conn, table)
    rows = select_rows(
      conn,
      table,
      cfg["curso_col"],
      cfg["municipio_col"],
      start=args.start,
      end=args.end,
      include_processed=args.include_processed,
    )
    total = len(rows)
    print(f"[{table}] Registros a processar: {total}")
    for idx, (rowid, nome_ies, curso, municipio) in enumerate(rows, start=1):
      terms = " ".join([nome_ies, curso, municipio])
      lucky_url = f"https://www.google.com/search?q={quote_plus(terms)}&btnI=I"
      final_url = resolve_url(lucky_url, session, retries=args.retries, sleep=args.sleep)
      update_row(conn, table, rowid, final_url)
      print(f"[{table}] {idx}/{total} -> {final_url or 'falha'}")
      time.sleep(jitter_sleep(args.sleep))

  conn.close()
  print("Processamento concluído.")


if __name__ == "__main__":
  main()
