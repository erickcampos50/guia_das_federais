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
# Função para carregar os dados do CSV da pos-graduacao
@st.cache_data  # Cache para melhorar a performance
def load_data_mestrado_doutorado(csv_file):
    df = pd.read_csv(csv_file,sep='\t',index_col=None)
    
    
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

# Função para carregar os dados do CSV da pos-graduacao
@st.cache_data  # Cache para melhorar a performance
def load_data_graduacao(csv_file):
    df = pd.read_csv(csv_file, sep='\t', index_col=None)
    
    # Novo mapeamento de colunas
    colunas_novas = {
        'Nome da IES': 'Nome_IES',
        'Nome do curso': 'Nome_Curso',
        'Grau': 'Grau',
        'Área OCDE': 'Area_Conhecimento',
        'Modalidade de ensino (presencial ou EaD)': 'Modalidade_Ensino',
        'Município': 'Municipio',
        'UF': 'UF',
        }
    
    df.rename(columns=colunas_novas, inplace=True)

    # Você pode adicionar aqui qualquer outra operação que deseje realizar no DataFrame
    # Por exemplo, tratar colunas com valores nulos, converter tipos de dados, etc.

    return df

@st.cache_data  # Cache para melhorar a performance
def load_data_especializacao(csv_file):
    df = pd.read_csv(csv_file, sep='\t', index_col=None)
    return df


#%%
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# %%
# Carregar os dados
data_mestrado_doutorado = load_data_mestrado_doutorado('mestrado_doutorado_univ_publicas.csv')
data_graduacao = load_data_graduacao('graduacao_univ_publicas.csv')
data_especializacao = load_data_especializacao('especializacao_univ_publicas.csv')



# %%
def show_especializacao():
    st.caption("""🔍 **Escolha os filtros que preferir** e veja os resultados na tabela no final da página.    
    💡 **Dica:** Você pode deixar todos os filtros em branco se quiser ver todos os dados 🌐
""")

    col_area, col_modalidade = st.columns(2)
    with col_area:
        # Primeira camada de filtro: Área de Conhecimento
        areas_conhecimento = st.multiselect('Área de conhecimento especializacao', 
                                            sorted(data_especializacao['Area_Conhecimento'].unique()), 
                                            default=[])
        df_filtrado = data_especializacao[data_especializacao['Area_Conhecimento'].isin(areas_conhecimento)] if areas_conhecimento else data_especializacao
    with col_modalidade:
        # Segunda camada de filtro: Modalidade de Ensino
        modalidade = st.multiselect('Modalidade de ensino', 
                                sorted(df_filtrado['MODALIDADE'].unique()), 
                                default=[])
        df_filtrado = df_filtrado[df_filtrado['MODALIDADE'].isin(modalidade)] if modalidade else df_filtrado

    col_nome_ies, col_nome_especializacao = st.columns(2)
    with col_nome_ies:
        # Terceira camada de filtro: Nome da Instituição
        nome_ies = st.multiselect('Nome da Instituição', 
                                sorted(df_filtrado['NOME_IES'].unique()), 
                                default=[])
        df_filtrado = df_filtrado[df_filtrado['NOME_IES'].isin(nome_ies)] if nome_ies else df_filtrado
    with col_nome_especializacao:
        # Quarta camada de filtro: Nome do Curso de Especialização
        nome_especializacao = st.multiselect('Nome do Curso de Especialização', 
                                            sorted(df_filtrado['NOME_ESPECIALIZACAO'].unique()), 
                                            default=[])
        df_filtrado = df_filtrado[df_filtrado['NOME_ESPECIALIZACAO'].isin(nome_especializacao)] if nome_especializacao else df_filtrado

    col_carga_horaria, col_duracao = st.columns(2)
    
    with col_carga_horaria:
        # Quinta camada de filtro: Carga Horária
        if not df_filtrado.empty:
            min_carga_horaria, max_carga_horaria = min(df_filtrado['CARGA_HORARIA']), max(df_filtrado['CARGA_HORARIA'])
            carga_horaria = st.slider('Carga Horária', 
                                    min_carga_horaria, max_carga_horaria, 
                                    (min_carga_horaria, max_carga_horaria), step=30)
            df_filtrado = df_filtrado[(df_filtrado['CARGA_HORARIA'] >= carga_horaria[0]) & (df_filtrado['CARGA_HORARIA'] <= carga_horaria[1])]
    with col_duracao:
        # Sexta camada de filtro: Duração em Meses
        if not df_filtrado.empty:
            min_duracao_meses, max_duracao_meses = min(df_filtrado['DURACAO_MESES']), max(df_filtrado['DURACAO_MESES'])
            duracao_meses = st.slider('Duração em Meses', 
                                    min_duracao_meses, max_duracao_meses, 
                                    (min_duracao_meses, max_duracao_meses),step=6)
            df_filtrado = df_filtrado[(df_filtrado['DURACAO_MESES'] >= duracao_meses[0]) & (df_filtrado['DURACAO_MESES'] <= duracao_meses[1])]

    col_municipio,col_estado = st.columns(2)
    with col_municipio:
        # Sétima camada de filtro: Município
        municipio_especializacao = st.multiselect('Município', 
                                sorted(df_filtrado['MUNICIPIO'].unique()), 
                                default=[])
        df_filtrado = df_filtrado[df_filtrado['MUNICIPIO'].isin(municipio_especializacao)] if municipio_especializacao else df_filtrado

    with col_estado:
        # Oitava camada de filtro: Estado (UF)
        estado_especializacao = st.multiselect('Estado', 
                            sorted(df_filtrado['UF'].unique()), 
                            default=[])
        df_filtrado = df_filtrado[df_filtrado['UF'].isin(estado_especializacao)] if estado_especializacao else df_filtrado

    df_filtrado.reset_index(drop=True, inplace=True)

    st.caption(""" ---
    __Atenção__: Se a tabela estiver muito pequena, você pode clicar no botão de ampliar no canto superior ou baixar a tabela nos botões abaixo""")
    # Aqui você pode adicionar a lógica para exibir a tabela com base nas seleções feitas.
    st.dataframe(df_filtrado[['NOME_ESPECIALIZACAO','NOME_IES','MUNICIPIO','UF','MODALIDADE','DURACAO_MESES','CARGA_HORARIA']])



    st.markdown(""" ---
    Utilize os botões abaixo se desejar baixar os dados da tabela acima :red[(primeiro botão)] ou baixar a base de dados orignal com todos os cursos de especialização das universidades públicas do Brasil :blue[(segundo botão)]""")
    col_download1, col_download2 = st.columns(2)
    with col_download1:
        # Botão para baixar dados filtrados
        if st.button('Planilha CSV dos dados dos cursos de especializacao', type="primary"):
            csv = convert_df_to_csv(df_filtrado)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Dados_filtrados_graduacao.csv', 
                            mime='text/csv')    
    with col_download2:
        # Botão para baixar todos os dados
        if st.button('Planilha CSV com todas as especializações do Brasil', type="secondary"):
            csv = convert_df_to_csv(data_especializacao)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Todos_os_dados_graduacao.csv', 
                            mime='text/csv')

# Interface Mestrado e Doutorado
def show_mestrado_doutorado():
    
    st.caption("""🔍 **Escolha os filtros que preferir** e veja os resultados na tabela no final da página.    
    💡 **Dica:** Você pode deixar todos os filtros em branco se quiser ver todos os dados 🌐
""")
    col_niveis, col_area = st.columns(2)
    with col_niveis:
        # Seleção múltipla para os níveis de curso
        niveis = st.multiselect('Nível (Mestrado, Doutorado, etc.)', 
                                sorted(data_mestrado_doutorado['Nivel_Programa'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de níveis
        data_niveis = data_mestrado_doutorado if not niveis else data_mestrado_doutorado[data_mestrado_doutorado['Nivel_Programa'].isin(niveis)]

    with col_area:
        # Multiselect para Área de Conhecimento
        areas_conhecimento = st.multiselect('Área de conhecimento', 
                                            sorted(data_mestrado_doutorado['Area_Conhecimento'].unique()), 
                                            default=[])
        st.caption('__Atenção aos servidores públicos:__ Observe se esta informação está alinhada com seu ambiente organizacional')
        # Filtrando dados com base na seleção de áreas de conhecimento
        data_areas = data_niveis if not areas_conhecimento else data_niveis[data_niveis['Area_Conhecimento'].isin(areas_conhecimento)]



    # Multiselect para as notas CAPES
    notas_capes = st.multiselect('Avaliação CAPES', 
                                sorted(data_areas['Nota_Conceito'].unique()), 
                                default=[])
    data_notas = data_areas if not notas_capes else data_areas[data_areas['Nota_Conceito'].isin(notas_capes)]


    data_atual = data_notas

    col_estado, col_municipio = st.columns(2)
    with col_estado:
        # Multiselect para estados
        estados = st.multiselect('Estado da instituição', 
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
        municipios = st.multiselect('Município', 
                                    municipios_opcoes, 
                                    default=[])
        # Filtrando dados com base na seleção de municípios
        data_municipios = data_estados if not municipios else data_estados[data_estados['Municipio'].isin(municipios)]
   


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
    filtered_data_sorted.reset_index(drop=True, inplace=True)


    
    st.caption(""" ---
    __Atenção__: Se a tabela estiver muito pequena, você pode clicar no botão de ampliar no canto superior ou baixar a tabela nos botões abaixo""")
    # Exibindo a tabela com os resultados filtrados
    st.dataframe(filtered_data_sorted[['Nome_Programa', 'Sigla_IES', 'UF', 
                                    'Municipio', 'Area_Conhecimento', 'Nota_Conceito', 'Nivel_Programa',
                                    'Modalidade']])
    

    st.markdown(""" ---
    Utilize os botões abaixo se desejar baixar os dados da tabela acima :red[(primeiro botão)] ou baixar a base de dados orignal com todos os programas de mestrado e doutorado das universidades públicas do Brasil :blue[(segundo botão)]""")
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
            csv = convert_df_to_csv(data_mestrado_doutorado)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Todos_os_dados.csv', 
                            mime='text/csv')
    
    


# Função para exibir a mensagem de "Em Construção"
def show_graduacao():
    
    st.caption("""🔍 **Escolha os filtros que preferir** e veja os resultados na tabela no final da página.    
    💡 **Dica:** Você pode deixar todos os filtros em branco se quiser ver todos os dados 🌐
""")

    col_graus, col_modalidade = st.columns(2)
    with col_graus:
        # Seleção múltipla para os níveis de curso
        graus = st.multiselect('Tipos de graduação (Licenciatura, Bacharelado, etc.)', 
                                sorted(data_graduacao['Grau'].unique()), 
                                default=["Bacharelado","Licenciatura"])
        # Filtrando dados com base na seleção de níveis
        data_graus = data_graduacao if not graus else data_graduacao[data_graduacao['Grau'].isin(graus)]

    with col_modalidade:
        # Multiselect para Modalidade de ensino
        modalidade_ensino = st.multiselect('Modalidade de Ensino (Presencial ou EAD)', 
                                            sorted(data_graduacao['Modalidade_Ensino'].unique()), 
                                            default=["Educação Presencial"])
        # Filtrando dados com base na seleção de áreas de conhecimento
        data_modalidade = data_graus if not modalidade_ensino else data_graus[data_graus['Modalidade_Ensino'].isin(modalidade_ensino)]





    data_atual_graduacao = data_modalidade

    col_estado, col_municipio = st.columns(2)
    with col_estado:
        # Multiselect para estados
        estados = st.multiselect('Estado/UF', 
                                sorted(data_atual_graduacao['UF'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de estados
        data_estados = data_atual_graduacao if not estados else data_atual_graduacao[data_atual_graduacao['UF'].isin(estados)]


    with col_municipio:
        # Condicionando a exibição de municípios com base nos estados selecionados
        if estados:
            municipios_opcoes = sorted(data_estados['Municipio'].unique())
        else:
            municipios_opcoes = sorted(data_atual_graduacao['Municipio'].unique())

        # Multiselect para Município
        municipios = st.multiselect('Município da instituição', 
                                    municipios_opcoes, 
                                    default=[])
        # Filtrando dados com base na seleção de municípios
        data_municipios = data_estados if not municipios else data_estados[data_estados['Municipio'].isin(municipios)]


    # Usando 'data_municipios' como base para os próximos filtros
    data_atual_graduacao = data_municipios


    col_nome_ies, col_curso_ies = st.columns(2)

    with col_nome_ies:
        # Multiselect para nomes das instituições
        nomes_ies = st.multiselect('Nome da Instituição', 
                                sorted(data_atual_graduacao['Nome_IES'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de nomes
        data_nome_ies = data_atual_graduacao if not nomes_ies else data_atual_graduacao[data_atual_graduacao['Nome_IES'].isin(nomes_ies)]
    
    with col_curso_ies:
        # Multiselect para nomes das instituições
        curso_ies = st.multiselect('Curso', 
                                sorted(data_nome_ies['Nome_Curso'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de nomes
        data_curso_ies = data_nome_ies if not curso_ies else data_nome_ies[data_nome_ies['Nome_Curso'].isin(curso_ies)]
    
    # Ordenando os dados primeiro por Nome_Programa e depois por Sigla_IES, UF, Município e Modalidade
    filtered_data_sorted = data_curso_ies.sort_values(by=['Nome_Curso', 'Nome_IES', 'UF', 'Municipio', 'Modalidade_Ensino'])
    filtered_data_sorted.reset_index(drop=True, inplace=True)




    st.caption(""" ---
    __Atenção__: Se a tabela estiver muito pequena, você pode clicar no botão de ampliar no canto superior ou baixar a tabela nos botões abaixo""")
    # Exibindo a tabela com os resultados filtrados
    st.dataframe(filtered_data_sorted[['Nome_Curso', 'Nome_IES', 'UF', 
                                    'Municipio', 'Modalidade_Ensino','Grau','Area_Conhecimento' ]])
    

    st.markdown(""" ---
    Utilize os botões abaixo se desejar baixar os dados da tabela acima :red[(primeiro botão)] ou baixar a base de dados orignal com todos os cursos de graduação das universidades públicas do Brasil :blue[(segundo botão)]""")
    col_download1, col_download2 = st.columns(2)
    with col_download1:
        # Botão para baixar dados filtrados
        if st.button('Planilha CSV dos dados da tabela acima', type="primary"):
            csv = convert_df_to_csv(filtered_data_sorted)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Dados_filtrados_graduacao.csv', 
                            mime='text/csv')    
    with col_download2:
        # Botão para baixar todos os dados
        if st.button('Planilha CSV com todos os cursos do Brasil', type="secondary"):
            csv = convert_df_to_csv(data_graduacao)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Todos_os_dados_graduacao.csv', 
                            mime='text/csv')
    





def main():
    st.title('Guia das Federais')
    st.subheader('Encontre cursos de graduação, especialização, mestrado e doutorado das universidades públicas do Brasil num único lugar')

    # Criação de abas para Graduação e Pós-Graduação
    tab1, tab2, tab3 = st.tabs(["CURSOS DE GRADUAÇÃO","ESPECIALIZAÇÃO","MESTRADO E DOUTORADO"])

    with tab1:
        show_graduacao()
    with tab2:
        show_especializacao()
    with tab3:
        show_mestrado_doutorado()
    

    st.markdown(""" ---
    ### O que eu faço agora? 🌟🚀

    Hey, explorador acadêmico! 🕵️‍♂️🎓 Você acabou de mergulhar num oceano de opções incríveis sobre graduações e pós-graduações em universidades públicas brasileiras. Mas, peraí, você deve estar se perguntando: "E agora, o que eu faço com todas essas infos?" 🤔

    Não se preocupe, eu te guio nessa! 🌈✨

    1. **Google é seu novo BFF!** 🌐👯
    - Infelizmente, o MEC, apesar de ter disponibilizado os dados, não nos deu links diretos. 😞
    - Mas isso não é um beco sem saída! Use o poderoso Google para buscar mais sobre os cursos que chamaram sua atenção. Digite o nome da universidade e do curso e... Voilà! Informações fresquinhas ao seu dispor.

    2. **Amantes de Planilhas, Uni-vos!** 📊💻
    - Se você curte uma boa planilha (quem não, né?), temos um presentão! 🎁
    - Você pode baixar **os dados que estão na tela** para uma análise mais aprofundada. Quer ver todos os detalhes e fazer suas próprias tabelas coloridas? É só clicar e baixar!
    - E se você é daqueles que adora ter **toda a base de dados**, temos isso também! Baixe a base completa e sinta-se como um cientista de dados descobrindo novos mundos.

    Então, é isso! Mergulhe fundo nessa busca, jovem padawan! Que a força do conhecimento esteja com você! 🌌👩‍🚀

    Lembre-se: cada clique é um passo em sua jornada acadêmica. Vá em frente e descubra as maravilhas das universidades públicas do Brasil! 🇧🇷🎉

    **Boa jornada!** 🚀🌟

    """)

    # Disclaimer/Avisos legais
    st.markdown(""" ---
    #### Disclaimer
    Apesar do esforço em disponibilizar informações de qualidade, podem haver erros, por isso utilize essas informações :red[por sua conta e risco]. Não são oferecidas quaisquer garantias.

    Este site é uma iniciativa voluntária para facilitar o acesso a informações sobre cursos de graduação, mestrado e doutorado em universidades públicas brasileiras - federais, estaduais e municipais permitindo visualizar todas as opções disponíveis em um único lugar, sem a necessidade de buscas extensas e trabalhosas. As informações aqui disponibilizadas foram extraídas de fontes oficiais do governo, como o e-MEC e a Plataforma Sucupira.
    """)


    # Adicionar o email de contato
    st.markdown('**Desenvolvido por Erick C. Campos:** [erickcampos50@gmail.com](mailto:erickcampos50@gmail.com)')



# %%
if __name__ == '__main__':
    main()
