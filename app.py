# %%
import streamlit as st
import pandas as pd
from io import BytesIO


#%%

st.set_page_config(
    page_title="Guia das Federais - Encontre seu curso numa universidade federal",
    layout="wide",
 )
# %%
# Função para carregar os dados do CSV
@st.cache_data  # Cache para melhorar a performance
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    colunas_novas = {
    'Sigla da Instituição de Ensino Superior do programa de pós-graduação': 'Sigla_IES',
    'Nome do programa de pós-graduação': 'Nome_Programa',
    'Área de conhecimento do programa de pós-graduação': 'Area_Conhecimento',
    'Sigla da Unidade da Federação do programa': 'UF',
    'Município sede do programa de pós-graduação': 'Municipio',
    'Modalidade do programa de pós-graduação': 'Modalidade',
    'Nível do programa de pós-graduação': 'Nivel_Programa',
    'Nota/Conceito do programa de pós-graduação': 'Nota_Conceito',
    'Instituição de Ensino Superior do programa de pós-graduação': 'Nome_IES'
    }
    df.rename(columns=colunas_novas, inplace=True)
    df['Nota_Conceito'].fillna("Não informado", inplace=True)
    df['Nota_Conceito'] = df['Nota_Conceito'].astype(str)
    

    return df
#%%
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# %%
# Carregar os dados
data = load_data('mestrado_doutorado_univ_publicas.csv')


#%%

# %%
# Interface do Streamlit
def main():
    
    st.title('Guia das Federais')
    st.subheader('Explore cursos de graduação, mestrado e doutorado das universidades públicas do Brasil')
    if st.checkbox("Mostrar instruções detalhadas"):  # Checkbox para mostrar/ocultar instruções
        st.subheader(" Instruções Detalhadas para Utilizar o Guia das Federais:")
        st.markdown("""
        #### 1. **Seleção de Nível do Programa**
        - **Descrição:** Escolha o nível de pós-graduação que você está procurando (por exemplo, Mestrado, Doutorado).
        - **Como Fazer:** Clique na caixa de seleção rotulada "Nível do programa de pós-graduação". Uma lista será exibida. Selecione os níveis desejados clicando nos nomes.
        - **Dica:** Você pode selecionar mais de um nível.

        #### 2. **Escolha de Notas/Conceitos CAPES**
        - **Descrição:** Filtrar programas pela nota ou conceito atribuído pela CAPES.
        - **Como Fazer:** Clique na caixa de seleção "Nota/Conceito do programa de pós-graduação". Escolha as notas que são do seu interesse.
        - **Dica:** Se não tiver uma preferência específica, você pode pular este passo.

        #### 3. **Seleção de Estado**
        - **Descrição:** Se você está buscando programas em estados específicos, este é o filtro a ser usado.
        - **Como Fazer:** Clique na caixa de seleção "Sigla da Unidade da Federação do programa" e marque os estados desejados.
        - **Dica:** Esta opção é útil se você tem uma localização preferencial.

        #### 4. **Filtrar por Município**
        - **Descrição:** Se desejar buscar programas em cidades específicas, use este filtro.
        - **Como Fazer:** Selecione o município na caixa correspondente.
        - **Dica:** Pode ser combinado com o filtro de estado para maior precisão.

        #### 5. **Escolher Área de Conhecimento**
        - **Descrição:** Filtra os programas pela área de conhecimento (por exemplo, Engenharia, Medicina).
        - **Como Fazer:** Abra a caixa de seleção "Área de conhecimento do programa de pós-graduação" e escolha as áreas de seu interesse.
        - **Dica:** Útil para encontrar programas específicos da sua área de interesse.

        #### 6. **Seleção de Instituição (Nome da IES)**
        - **Descrição:** Se você tem preferência por certas instituições, use este filtro.
        - **Como Fazer:** Clique na caixa de seleção e marque as instituições de sua escolha.
        - **Dica:** Ideal para quem deseja estudar em uma universidade específica.

        #### 7. **Visualização dos Resultados**
        - **Descrição:** Após aplicar os filtros, os resultados serão exibidos em uma tabela.
        - **Como Fazer:** Role a página para baixo para ver a tabela com os programas que correspondem aos seus filtros.
        - **Dica:** Você pode reajustar os filtros a qualquer momento para refinar sua busca. """)
        # st.image("caminho_para_imagem_instrucoes_nivel.jpg")
        # [demais instruções e imagens]

    
    st.markdown("* **Atenção:** Todos os filtros são opcionais, selecione somente aqueles que desejar e veja os resultados na tabela abaixo. Se nenhum for selecionado, todos os dados estarão disponíveis")

    col_niveis, col_area = st.columns(2)
    with col_niveis:
        # Seleção múltipla para os níveis de curso
        niveis = st.multiselect('Selecione os tipos de programa de pós-graduação que deseja', 
                                sorted(data['Nivel_Programa'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de níveis
        data_niveis = data if not niveis else data[data['Nivel_Programa'].isin(niveis)]

    with col_area:
        # Multiselect para Área de Conhecimento
        areas_conhecimento = st.multiselect('Área de conhecimento do programa de pós-graduação', 
                                            sorted(data['Area_Conhecimento'].unique()), 
                                            default=[])
        st.caption('__Atenção:__ Se você está buscando promoção na carreira na sua IFES, observe se esta informação está alinhada com seu ambiente organizacional')
        # Filtrando dados com base na seleção de áreas de conhecimento
        data_areas = data_niveis if not areas_conhecimento else data_niveis[data_niveis['Area_Conhecimento'].isin(areas_conhecimento)]



    # Multiselect para as notas CAPES
    notas_capes = st.multiselect('Nota/Conceito do programa de pós-graduação segundo a CAPES', 
                                sorted(data_areas['Nota_Conceito'].unique()), 
                                default=[])
    data_notas = data_areas if not notas_capes else data_areas[data_areas['Nota_Conceito'].isin(notas_capes)]


    data_atual = data_notas

    col_estado, col_municipio = st.columns(2)
    with col_estado:
        # Multiselect para estados
        estados = st.multiselect('Estado', 
                                sorted(data_atual['UF'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de estados
        data_estados = data_atual if not estados else data_atual[data_atual['UF'].isin(estados)]


    with col_municipio:
        # Condicionando a exibição de municípios com base nos estados selecionados
        if estados:
            municipios_opcoes = sorted(data_estados['Municipio'].unique())
        else:
            municipios_opcoes = sorted(data_atual['Municipio'].unique())

        # Multiselect para Município
        municipios = st.multiselect('Município sede do programa de pós-graduação', 
                                    municipios_opcoes, 
                                    default=[])
        # Filtrando dados com base na seleção de municípios
        data_municipios = data_estados if not municipios else data_estados[data_estados['Municipio'].isin(municipios)]
    st.caption('Se você tiver selecionado alguum :blue[estado] somente serão exibidos os municípios pertencentes àquele estado. Se nenhum :blue[estado] estiver marcado, serão exibidos todos os municípios')


    # Usando 'data_municipios' como base para os próximos filtros
    data_atual = data_municipios

    col_sigla_ies, col_nome_ies = st.columns(2)
    with col_sigla_ies:
        # Multiselect para siglas das instituições
        instituicoes = st.multiselect('Sigla da Instituição', 
                                    sorted(data_atual['Sigla_IES'].unique()), 
                                    default=[])
        # Filtrando dados com base na seleção de siglas
        data_sigla_ies = data_atual if not instituicoes else data_atual[data_atual['Sigla_IES'].isin(instituicoes)]

    with col_nome_ies:
        # Multiselect para nomes das instituições
        nomes_ies = st.multiselect('Nome da Instituição', 
                                sorted(data_atual['Nome_IES'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de nomes
        data_nome_ies = data_atual if not nomes_ies else data_atual[data_atual['Nome_IES'].isin(nomes_ies)]
    st.caption('Você pode selecionar as instituições de seu interesse pela :blue[*_Sigla_*] pelo :red[*_Nome da Instituição_*] ou pelos dois ao mesmo tempo.')

    # Combinando os filtros de Sigla e Nome da IES
    # Isso permite que ambos os filtros sejam aplicados em conjunto
    filtered_data = data_sigla_ies.merge(data_nome_ies, how='inner')

    # Ordenando os dados primeiro por Nome_Programa e depois por Sigla_IES, UF, Município e Modalidade
    filtered_data_sorted = filtered_data.sort_values(by=['Nome_Programa', 'Sigla_IES', 'UF', 'Municipio', 'Modalidade'])

    # Resetando os índices para não exibi-los
    filtered_data_sorted.reset_index(drop=True, inplace=True)

    # Exibindo a tabela com os resultados filtrados
    st.dataframe(filtered_data_sorted[['Nome_Programa', 'Sigla_IES', 'UF', 
                                    'Municipio', 'Area_Conhecimento', 'Nota_Conceito', 'Nivel_Programa',
                                    'Modalidade']])
    

    st.markdown("Utilize os botões abaixo se desejar baixar os dados da tabela acima :red[(primeiro botão)] ou baixar a base de dados orignal com todos os programas de mestrado e doutorado das universidades públicas do Brasil :blue[(segundo botão)]")
    col_download1, col_download2 = st.columns(2)
    with col_download1:
        # Botão para baixar dados filtrados
        if st.button('Planilha CSV de todos os dados da tabela acima', type="primary"):
            csv = convert_df_to_csv(filtered_data_sorted)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Dados_filtrados.csv', 
                            mime='text/csv')
    with col_download2:
        # Botão para baixar todos os dados
        if st.button('Planilha CSV com todos os programas do Brasil', type="secondary"):
            csv = convert_df_to_csv(data)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Todos_os_dados.csv', 
                            mime='text/csv')


# %%
if __name__ == '__main__':
    main()
