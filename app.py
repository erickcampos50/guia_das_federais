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
def load_data(csv_file):
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

#%%
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# %%
# Carregar os dados
data_pos = load_data('mestrado_doutorado_univ_publicas.csv')
data_graduacao = load_data_graduacao('graduacao_univ_publicas.csv')


# %%
# Interface Pós graduação do Streamlit 
def show_pos_graduacao():
    

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
        niveis = st.multiselect('Tipos de graduação/pós-graduação', 
                                sorted(data_pos['Nivel_Programa'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de níveis
        data_niveis = data_pos if not niveis else data_pos[data_pos['Nivel_Programa'].isin(niveis)]

    with col_area:
        # Multiselect para Área de Conhecimento
        areas_conhecimento = st.multiselect('Área de conhecimento', 
                                            sorted(data_pos['Area_Conhecimento'].unique()), 
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
        municipios = st.multiselect('Município', 
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
            csv = convert_df_to_csv(data_pos)
            st.download_button(label="Dados prontos para download. Clique aqui para baixar.", 
                            data=csv, 
                            file_name='Todos_os_dados.csv', 
                            mime='text/csv')
    
    


# Função para exibir a mensagem de "Em Construção"
def show_graduacao():
    
    st.markdown("* **Atenção:** Todos os filtros são opcionais e você pode escolher vários ao mesmo tempo. Se nenhum for selecionado, todos os dados estarão disponíveis")

    col_graus, col_modalidade = st.columns(2)
    with col_graus:
        # Seleção múltipla para os níveis de curso
        graus = st.multiselect('Tipos de graduação (Licenciatura,Bacharelado, etc.)', 
                                sorted(data_graduacao['Grau'].unique()), 
                                default=[])
        # Filtrando dados com base na seleção de níveis
        data_graus = data_graduacao if not graus else data_graduacao[data_graduacao['Grau'].isin(graus)]

    with col_modalidade:
        # Multiselect para Área de Conhecimento
        modalidade_ensino = st.multiselect('Modalidade de Ensino (Presencial, Remoto, etc.)', 
                                            sorted(data_graduacao['Modalidade_Ensino'].unique()), 
                                            default=[])
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
    st.caption('Se você tiver selecionado alguum :blue[estado] somente serão exibidos os municípios pertencentes àquele estado. Se nenhum :blue[estado] estiver marcado, serão exibidos todos os municípios')


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

    # Resetando os índices para não exibi-los
    filtered_data_sorted.reset_index(drop=True, inplace=True)

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
    st.subheader('Encontre cursos de graduação, mestrado e doutorado das universidades públicas do Brasil num único lugar')
    st.markdown(""" Este site é uma iniciativa voluntária para facilitar o acesso a informações sobre cursos de graduação, mestrado e doutorado em universidades públicas brasileiras - federais, estaduais e municipais permitindo visualizar todas as opções disponíveis em um único lugar, sem a necessidade de buscas extensas e trabalhosas. As informações aqui disponibilizadas foram extraídas de fontes oficiais do governo, como o e-MEC e a Plataforma Sucupira. 
    """)

    # Criação de abas para Graduação e Pós-Graduação
    tab1, tab2 = st.tabs(["Encontrar cursos de Graduação","Encontrar cursos de Mestrado e Doutorado"])

    with tab1:
        show_graduacao()
    with tab2:
        show_pos_graduacao()


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
    """)

    # Adicionar o email de contato
    st.markdown('**Desenvolvido por Erick C. Campos:** [erickcampos50@gmail.com](mailto:erickcampos50@gmail.com)')



# %%
if __name__ == '__main__':
    main()
