# %%
import pandas as pd

def filtrar_dados_capes_csv(arquivo_dados_pos, arquivo_codigos_pos):
    try:
        # Carregar o arquivo B.csv que contém o glossário/dicionário
        glossario = pd.read_csv(arquivo_codigos_pos, header=None, sep='\t', usecols=[1, 2])
        glossario_dict = dict(zip(glossario[1], glossario[2]))

        # Carregar o arquivo A.csv com os parâmetros específicos: separador de tabulação, sem índice e sem cabeçalho
        dados_pos = pd.read_csv(arquivo_dados_pos, sep='\t', index_col=False)

        # Filtrar os dados
        dados_filtrados = dados_pos.loc[(dados_pos['DS_SITUACAO_PROGRAMA'] == 'EM FUNCIONAMENTO') & 
                               ((dados_pos['DS_DEPENDENCIA_ADMINISTRATIVA'] == 'PÚBLICA') | 
                                (dados_pos['SG_ENTIDADE_ENSINO_REDE'] == 'SIM')),
                               dados_pos.columns[:-3]]

        # Substituir os cabeçalhos das colunas do arquivo A.csv pelos valores correspondentes do arquivo B.csv
        dados_filtrados.columns = [glossario_dict.get(col, col) for col in dados_filtrados.columns]

        return dados_filtrados

    except Exception as e:
        return f"Ocorreu um erro: {e}"

#%%
# Exemplo de como usar a função
arquivo_codigos_pos = 'CAPES_originais/codigos_capes.csv'
arquivo_dados_pos = 'CAPES_originais/br-capes-colsucup-prog-2021-2022-11-30.csv'
dados_resultantes_pos = filtrar_dados_capes_csv(arquivo_dados_pos, arquivo_codigos_pos)
#%%
dados_resultantes_pos.to_csv("../mestrado_doutorado_univ_publicas.csv", index=None, sep='\t')
#%%
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

#%%
# Exemplo de como usar a função
arquivo_codigos_graduacao = 'MEC_originais/dicionario_codigos.csv'
arquivo_dados_graduacao = 'MEC_originais/PDA_Dados_Cursos_Graduacao_Brasil.csv'
dados_resultantes_graduacao = filtrar_dados_mec_csv(arquivo_dados_graduacao, arquivo_codigos_graduacao)

#%%
dados_resultantes_graduacao.to_csv("../graduacao_univ_publicas.csv", index=None, sep='\t')

# %%
