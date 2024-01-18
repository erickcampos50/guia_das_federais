# %%
# Esta seção importa e trata os dados obtidos via Capes https://dadosabertos.capes.gov.br/dataset/2017-a-2020-programas-da-pos-graduacao-stricto-sensu-no-brasil
# São referentes exclusivamente ao Mestrado e Doutorado
import pandas as pd

def filtrar_dados_capes_csv(arquivo_dados_pos, arquivo_codigos_pos):
    try:
        # Carregar o arquivo que contém o glossário/dicionário das colunas
        glossario = pd.read_csv(arquivo_codigos_pos, header=None, sep='\t', usecols=[1, 2])
        glossario_dict = dict(zip(glossario[1], glossario[2]))

        # Carregar o arquivo com os dados dos programas (separador de tabulação, sem índice e sem cabeçalho)
        dados_pos = pd.read_csv(arquivo_dados_pos, sep='\t', index_col=False)

        # Filtrar os dados para selecionar somente os programas em funcionamento, de instituições públicas ou em rede (na maioria das vezes os programas em rede tem participação das IES públicas)
        dados_filtrados = dados_pos.loc[(dados_pos['DS_SITUACAO_PROGRAMA'] == 'EM FUNCIONAMENTO') & 
                               ((dados_pos['DS_DEPENDENCIA_ADMINISTRATIVA'] == 'PÚBLICA') | 
                                (dados_pos['SG_ENTIDADE_ENSINO_REDE'] == 'SIM')),
                               dados_pos.columns[:-3]] #Dispensando as ultimas colunas porque não tem informação útil

        # Substituir os cabeçalhos das colunas pelo conteúdo do glossário
        dados_filtrados.columns = [glossario_dict.get(col, col) for col in dados_filtrados.columns]

        # Adicionar a coluna "Link" com o link completo para acessar os detalhes do programa diretamente na plataforma sucupira
        dados_filtrados['Link'] = dados_filtrados['Código do programa de pós-graduação'].apply(
            lambda x: "https://sucupira.capes.gov.br/sucupira/public/consultas/coleta/programa/viewPrograma.jsf?cd_programa=" + str(x)
        )


        return dados_filtrados

    except Exception as e:
        return f"Ocorreu um erro: {e}"

# É necessário ajustar os nomes dos arquivos se novas versões da base de dados forem disponibilizadas
arquivo_codigos_pos = 'CAPES_originais/codigos_capes.csv'
arquivo_dados_pos = 'CAPES_originais/br-capes-colsucup-prog-2021-2022-11-30.csv'
dados_resultantes_pos = filtrar_dados_capes_csv(arquivo_dados_pos, arquivo_codigos_pos)
dados_resultantes_pos.to_csv("../mestrado_doutorado_univ_publicas.csv", index=None, sep='\t')
#%%
# Esta seção importa e trata os dados obtidos via MEC https://dadosabertos.mec.gov.br/indicadores-sobre-ensino-superior
# São referentes exclusivamente à Graduação
import pandas as pd

def filtrar_dados_mec_csv(arquivo_dados_graduacao, arquivo_codigos_graduacao):
    try:
        # Carregar o arquivo B.csv que contém o glossário/dicionário
        glossario = pd.read_csv(arquivo_codigos_graduacao,  sep='\t', usecols=[0, 1])
        glossario_dict = dict(zip(glossario['Código'], glossario['Nome']))

        # Preparar um DataFrame vazio para armazenar os dados filtrados
        dados_filtrados = pd.DataFrame()

        categorias_publicas = ["Pública Federal", "Pública Estadual"]

        # Processar o arquivo A.csv em pedaços para evitar carregar tudo na memória
        chunksize = 10000  # Ajuste este valor conforme a necessidade
        for chunk in pd.read_csv(arquivo_dados_graduacao, sep=',', chunksize=chunksize):
            # Filtrar os dados conforme as condições
            chunk_filtrado = chunk.loc[(chunk['CATEGORIA_ADMINISTRATIVA'].isin(categorias_publicas)) & (chunk['SITUACAO_CURSO'] == 'Em atividade')]

            # Descartar as colunas especificadas
            colunas_para_descartar = ['CODIGO_IES', 'CODIGO_AREA_OCDE_CINE', 'AREA_OCDE_CINE','CODIGO_MUNICIPIO', 'CARGA_HORARIA']
            chunk_filtrado = chunk_filtrado.drop(columns=colunas_para_descartar)

            # Adicionar o chunk filtrado ao DataFrame final
            dados_filtrados = pd.concat([dados_filtrados, chunk_filtrado], ignore_index=True)

        # Substituir os cabeçalhos das colunas do arquivo A.csv pelos valores correspondentes do arquivo B.csv
        dados_filtrados.columns = [glossario_dict.get(col, col) for col in dados_filtrados.columns]

        return dados_filtrados

    except Exception as e:
        return f"Ocorreu um erro: {e}"


arquivo_codigos_graduacao = 'MEC_originais/dicionario_codigos.csv'
arquivo_dados_graduacao = 'MEC_originais/PDA_Dados_Cursos_Graduacao_Brasil.csv'
dados_resultantes_graduacao = filtrar_dados_mec_csv(arquivo_dados_graduacao, arquivo_codigos_graduacao)
dados_resultantes_graduacao.to_csv("../graduacao_univ_publicas.csv", index=None, sep='\t')
# %%
# Esta seção importa e trata os dados obtidos via MEC https://dadosabertos.mec.gov.br/indicadores-sobre-ensino-superior/item/182-cursos-de-especializacao-do-brasil
# São referentes exclusivamente à Pós-graduação lato senso (a especializacao)
# Como não exisitia uma informação sobre a Categoria da IES nesta base de dados, foi necessário utilizar o resultado da seção anterior como referência pra conseguir filtrar 
import pandas as pd

# Script para ler e processar os dados dos CSVs

# Função para ler o arquivo CSV e criar o dataframe "IES_publicas"
def criar_dataframe_ies_publicas(dados_resultantes_graduacao):
    # Ler o arquivo CSV
    df_graduacao = pd.read_csv(dados_resultantes_graduacao,sep='\t')

    # Selecionar valores únicos da coluna "Nome da IES" e os valores correspondentes da coluna "Categoria da IES"
    df_ies_publicas = df_graduacao.drop_duplicates(subset=["Nome da IES"])[["Nome da IES", "Categoria da IES"]]
    
    # Renomear o dataframe
    df_ies_publicas.rename(columns={"Nome da IES": "NOME_IES", "Categoria da IES": "Categoria_IES"}, inplace=True)

    return df_ies_publicas

# Função para ler o arquivo CSV "PDA_Cursos_Especializacao_Brasil.csv" e filtrar as linhas com correspondência no dataframe "IES_publicas"
def filtrar_cursos_especializacao(df_ies_publicas,arquivo_dados_especializacao):
    # Ler o arquivo CSV
    df_especializacao = pd.read_csv(arquivo_dados_especializacao,sep=',')

    # Filtrar as linhas onde a coluna "Nome da IES" tenha correspondência no dataframe "IES_publicas"
    df_especializacao_filtrado = df_especializacao[df_especializacao["NOME_IES"].isin(df_ies_publicas["NOME_IES"])]

    # Filtrar os dados conforme as condições
    df_especializacao_filtrado = df_especializacao_filtrado.loc[(df_especializacao_filtrado['SITUACAO'] == 'Ativo')]

    # Descartar as colunas especificadas
    colunas_para_descartar = ['CODIGO_IES','CODIGO_ESPECIALIZACAO', 'CODIGO_OCDE_CINE', 'CODIGO_MUNICIPIO']
    df_especializacao_filtrado = df_especializacao_filtrado.drop(columns=colunas_para_descartar)

    # Como existem muitos dados de duração que são absurdos (como 480 meses) eu estou modificando qualquer coisa acima de 48 meses para 48
    df_especializacao_filtrado.loc[df_especializacao_filtrado['DURACAO_MESES'] > 48, 'DURACAO_MESES'] = 48

    # Como existem muitos dados de carga horária que não condizem com a realidade, estou definindo como 30hrs/mes para qualquer curso que extrapole um valor razoavel
    df_especializacao_filtrado.loc[df_especializacao_filtrado['CARGA_HORARIA'] > 720, 'CARGA_HORARIA'] = df_especializacao_filtrado['DURACAO_MESES']*30


    df_especializacao_filtrado.rename(columns={"OCDE_CINE": "Area_Conhecimento"}, inplace=True)

    # Junção dos dataframes baseada na coluna "Nome da IES" / "Nome_IES"
    df_especializacao_filtrado_unificado = df_especializacao_filtrado.merge(df_ies_publicas,left_on="NOME_IES", right_on="NOME_IES",how="left")


    return df_especializacao_filtrado_unificado
#%%
# Executando as funções
arquivo_dados_resultantes_graduacao = "../graduacao_univ_publicas.csv"
df_ies_publicas = criar_dataframe_ies_publicas(arquivo_dados_resultantes_graduacao)
#%%
df_ies_publicas.head()
#%%
arquivo_dados_especializacao = "MEC_originais/PDA_Cursos_Especializacao_Brasil.csv"
dados_resultantes_especializacao = filtrar_cursos_especializacao(df_ies_publicas,arquivo_dados_especializacao)
dados_resultantes_especializacao.to_csv("../especializacao_univ_publicas.csv", index=None, sep='\t')
# Exibir os dataframes resultantes
dados_resultantes_especializacao.head()

