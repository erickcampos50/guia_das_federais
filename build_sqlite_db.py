"""
Gera um banco SQLite único com as três bases (graduação, especialização e pós).

Uso:
    python3 build_sqlite_db.py

O arquivo resultante é salvo em webapp/public/data/guia.sqlite e pode ser
publicado diretamente no GitHub Pages.
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "webapp" / "public" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "guia.sqlite"


def load_graduacao():
    df = pd.read_csv(ROOT / "graduacao_univ_publicas.csv", sep="\t")
    df = df.rename(
        columns={
            "Nome da IES": "nome_ies",
            "Categoria da IES": "categoria_ies",
            "Organização acadêmica": "organizacao_academica",
            "Código do curso": "codigo_curso",
            "Nome do curso": "nome_curso",
            "Grau": "grau",
            "Área OCDE": "area_conhecimento",
            "Modalidade de ensino (presencial ou EaD)": "modalidade",
            "Situação do curso (ativo ou inativo)": "situacao",
            "Vagas autorizadas": "vagas_autorizadas",
            "Município": "municipio",
            "UF": "uf",
            "Região": "regiao",
        }
    )
    return df


def load_pos():
    df = pd.read_csv(ROOT / "mestrado_doutorado_univ_publicas.csv", sep="\t")
    df = df.rename(
        columns={
            "Ano de referência do Coleta": "ano_referencia",
            "Grande área do conhecimento do programa de pós-graduação": "grande_area",
            "Área de conhecimento do programa de pós-graduação": "area_conhecimento",
            "Área básica do conhecimento do programa de pós-graduação": "area_basica",
            "Subárea do conhecimento do programa de pós-graduação": "subarea",
            "Especialidade do conhecimento programa de pós-graduação": "especialidade",
            "Código identificador da área de avaliação do programa de pós-graduação": "codigo_area_avaliacao",
            "Área de avaliação do programa de pós-graduação": "area_avaliacao",
            "Código da Instituição de Ensino Superior na CAPES": "codigo_capes_ies",
            "Código e-Mec da Instituição de Ensino Superior": "codigo_emec_ies",
            "Sigla da Instituição de Ensino Superior do programa de pós-graduação": "sigla_ies",
            "Instituição de Ensino Superior do programa de pós-graduação": "nome_ies",
            "Indicador de programa de pós-graduação em rede": "indicador_rede",
            "Siglas das Instituições que compõem o programa em rede, quando for o caso": "siglas_rede",
            "Status Jurídico da Instituição de Ensino Superior": "status_juridico",
            "Dependência administrativa da Instituição de Ensino Superior": "dependencia",
            "Organização acadêmica da Instituição de Ensino Superior": "organizacao_academica",
            "Grande Região onde está localizado o programa": "regiao",
            "Sigla da Unidade da Federação do programa": "uf",
            "Município sede do programa de pós-graduação": "municipio",
            "Modalidade do programa de pós-graduação": "modalidade",
            "Código do programa de pós-graduação": "codigo_programa",
            "Nome do programa de pós-graduação": "nome_programa",
            "Nome do programa de pós-graduação em inglês": "nome_programa_en",
            "Nível do programa de pós-graduação": "nivel_programa",
            "Nota/Conceito do programa de pós-graduação": "nota_conceito",
            "Ano de início do programa de pós-graduação": "ano_inicio_programa",
            "Ano de início de cada curso que compõe o programa": "ano_inicio_curso",
            "Situação do programa no ano de referência": "situacao_programa",
            "Link": "link",
        }
    )
    df["nota_conceito"] = df["nota_conceito"].astype(str)
    return df


def load_especializacao():
    df = pd.read_csv(ROOT / "especializacao_univ_publicas.csv", sep="\t")
    df = df.rename(
        columns={
            "NOME_IES": "nome_ies",
            "NOME_ESPECIALIZACAO": "nome_especializacao",
            "Area_Conhecimento": "area_conhecimento",
            "CARGA_HORARIA": "carga_horaria",
            "DURACAO_MESES": "duracao_meses",
            "MODALIDADE": "modalidade",
            "VAGAS": "vagas",
            "MUNICIPIO": "municipio",
            "UF": "uf",
            "REGIAO": "regiao",
            "SITUACAO": "situacao",
            "Categoria_IES": "categoria_ies",
        }
    )
    return df


def write_table(conn, name, df, indexes):
    df.to_sql(name, conn, if_exists="replace", index=False)
    for idx_name, cols in indexes.items():
        joined = ",".join(cols)
        conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {name}({joined});")


def build():
    conn = sqlite3.connect(DB_PATH)

    graduacao = load_graduacao()
    pos = load_pos()
    especializacao = load_especializacao()

    write_table(
        conn,
        "graduacao",
        graduacao,
        {
            "idx_graduacao_uf": ["uf"],
            "idx_graduacao_municipio": ["municipio"],
            "idx_graduacao_area": ["area_conhecimento"],
            "idx_graduacao_nome_ies": ["nome_ies"],
            "idx_graduacao_nome_curso": ["nome_curso"],
        },
    )
    write_table(
        conn,
        "pos",
        pos,
        {
            "idx_pos_uf": ["uf"],
            "idx_pos_municipio": ["municipio"],
            "idx_pos_area": ["area_conhecimento"],
            "idx_pos_sigla": ["sigla_ies"],
            "idx_pos_nivel": ["nivel_programa"],
        },
    )
    write_table(
        conn,
        "especializacao",
        especializacao,
        {
            "idx_especializacao_uf": ["uf"],
            "idx_especializacao_municipio": ["municipio"],
            "idx_especializacao_area": ["area_conhecimento"],
            "idx_especializacao_modalidade": ["modalidade"],
        },
    )

    conn.commit()
    conn.close()
    print(f"Base SQLite gerada em {DB_PATH}")


if __name__ == "__main__":
    build()
