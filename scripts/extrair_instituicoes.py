#!/usr/bin/env python3
"""
Extrai nomes de instituições únicos do banco SQLite e grava em CSV em uma pasta temporária.
Cria/usa a pasta tmp_instituicoes na raiz do projeto.
"""
from __future__ import annotations

import csv
import gzip
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus
from typing import Tuple


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "docs" / "public" / "data"
TMP_DIR = ROOT / "tmp_instituicoes"


def find_db() -> Tuple[Path, bool]:
  """Retorna o caminho do banco e se está compactado."""
  gz_path = DATA_DIR / "guia.sqlite.gz"
  plain_path = DATA_DIR / "guia.sqlite"
  if gz_path.exists():
    return gz_path, True
  if plain_path.exists():
    return plain_path, False
  raise FileNotFoundError("Nenhum guia.sqlite(.gz) encontrado em docs/public/data")


def prepare_db_file(src: Path, compressed: bool) -> Path:
  """Copia/descompacta o banco para a pasta temporária e retorna o caminho resultante."""
  TMP_DIR.mkdir(parents=True, exist_ok=True)
  target = TMP_DIR / "guia.sqlite"
  if compressed:
    with gzip.open(src, "rb") as f_in, target.open("wb") as f_out:
      f_out.write(f_in.read())
  else:
    data = src.read_bytes()
    target.write_bytes(data)
  return target


def extract_institutions(db_path: Path, output_csv: Path) -> int:
  """
  Extrai combinações únicas (instituição, curso, município) e grava no CSV com link de busca.
  Retorna quantidade de linhas gravadas.
  """
  query = """
    SELECT DISTINCT nome_ies AS nome_ies, nome_curso AS curso, municipio
    FROM graduacao
    WHERE nome_ies IS NOT NULL AND nome_curso IS NOT NULL AND municipio IS NOT NULL
    UNION
    SELECT DISTINCT nome_ies AS nome_ies, nome_especializacao AS curso, municipio
    FROM especializacao
    WHERE nome_ies IS NOT NULL AND nome_especializacao IS NOT NULL AND municipio IS NOT NULL
    UNION
    SELECT DISTINCT nome_ies AS nome_ies, nome_programa AS curso, municipio
    FROM pos
    WHERE nome_ies IS NOT NULL AND nome_programa IS NOT NULL AND municipio IS NOT NULL
    ORDER BY nome_ies COLLATE NOCASE, curso COLLATE NOCASE, municipio COLLATE NOCASE;
  """
  conn = sqlite3.connect(db_path)
  try:
    cur = conn.cursor()
    rows = cur.execute(query).fetchall()
  finally:
    conn.close()

  output_csv.parent.mkdir(parents=True, exist_ok=True)
  with output_csv.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["nome_ies", "curso", "municipio", "google_im_feeling_lucky"])
    for nome_ies, curso, municipio in rows:
      terms = " ".join([nome_ies, curso, municipio])
      lucky_url = f"https://www.google.com/search?q={quote_plus(terms)}&btnI=I"
      writer.writerow([nome_ies, curso, municipio, lucky_url])
  return len(rows)


def main():
  src, compressed = find_db()
  db_file = prepare_db_file(src, compressed)
  output_csv = TMP_DIR / "instituicoes_unicas.csv"
  count = extract_institutions(db_file, output_csv)
  print(f"Instituições únicas gravadas: {count}")
  print(f"Arquivo gerado em: {output_csv}")
  if compressed:
    print(f"Banco descompactado para uso temporário em: {db_file}")
  else:
    print(f"Banco copiado para uso temporário em: {db_file}")


if __name__ == "__main__":
  main()
