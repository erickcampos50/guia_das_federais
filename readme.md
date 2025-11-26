# Conheça o projeto Guia das Federais

## Introdução

O projeto "Guia das Federais" é uma aplicação web desenvolvida em Python, utilizando a biblioteca Streamlit. Este guia tem como objetivo oferecer uma plataforma unificada para buscar cursos de graduação, mestrado e doutorado em universidades públicas brasileiras. Com uma interface amigável e filtros práticos, permite aos usuários explorar opções educacionais facilmente.

## Funcionalidades

- **Busca de Cursos:** Permite filtrar cursos de graduação, mestrado e doutorado com base em vários critérios como área de conhecimento, instituição, estado, município, etc.
- **Dados Detalhados:** Oferece informações detalhadas sobre cada curso, incluindo a avaliação CAPES, modalidade de ensino, grau acadêmico, entre outros.
- **Download de Dados:** Os usuários podem baixar os dados filtrados em formato CSV para análises mais aprofundadas.

## Como Executar

Para executar o projeto, você precisará ter Python instalado em sua máquina, assim como as bibliotecas Streamlit e Pandas. Siga os passos abaixo:

1. Clone o repositório do projeto para sua máquina local.
2. Instale as dependências necessárias utilizando o comando: `pip install streamlit pandas`.
3. Execute a aplicação com o comando: `streamlit run app.py`.

## Uso da Aplicação

A aplicação está dividida em duas abas principais: Graduação e Pós-Graduação. Cada aba possui filtros específicos que permitem uma busca personalizada de acordo com as preferências do usuário. 

Além disso a aplicação conta com um script denominado `tratamento_dados.py`que aplica os filtros nos arquivos de dados originais para obter os arquivos `mestrado_doutorado_univ_publicas.csv` e `graduacao_univ_publicas.csv` que são as bases de dados da aplicação.

### Encontrar cursos de Graduação

Nesta seção, os usuários podem filtrar os cursos de graduação disponíveis nas universidades públicas do Brasil. Os filtros disponíveis incluem:

- Grau do curso (Licenciatura, Bacharelado, etc.).
- Modalidade de Ensino (Presencial, EAD, etc.).
- Estado/UF e Município da instituição.
- Nome da Instituição e do

Curso.

### Encontrar cursos de Mestrado e Doutorado

Esta aba permite a busca de cursos de pós-graduação, com filtros como:

- Nível do programa (Mestrado, Doutorado).
- Avaliação CAPES.
- Estado/UF e Município do programa.
- Área de conhecimento.
- Nome e Sigla da Instituição de Ensino Superior.

### Instruções Detalhadas

Cada filtro vem acompanhado de uma descrição detalhada e dicas para ajudar na utilização da ferramenta, garantindo uma experiência intuitiva e informativa. 

### Download de Dados

Os usuários podem baixar os resultados da busca em formato CSV, tanto para os dados filtrados quanto para a base de dados completa.

## Contribuições

Contribuições para o projeto são bem-vindas. Se você tem ideias para melhorar a aplicação ou quer ajudar a corrigir bugs, sinta-se à vontade para criar uma issue ou um pull request no repositório do GitHub.

## Suporte e Contato

Em caso de dúvidas ou sugestões, entre em contato com o desenvolvedor principal, Erick C. Campos, através do e-mail: erickcampos50@gmail.com.

## Origem dos Dados

### Dados de Graduação

Os dados referentes aos cursos de graduação foram cuidadosamente obtidos do portal de dados abertos do Ministério da Educação (MEC), mais especificamente na seção de Indicadores sobre o Ensino Superior. Esses dados podem ser acessados diretamente através do link: [Portal de Dados Abertos do MEC - Indicadores sobre Ensino Superior](https://dadosabertos.mec.gov.br/indicadores-sobre-ensino-superior).

Devido ao grande volume do arquivo original, que atualmente excede 200MB, foi necessário realizar um tratamento especial para garantir que o sistema não fosse sobrecarregado. Para isso, aplicamos filtros específicos aos dados, selecionando apenas as instituições classificadas como "Pública Federal" ou "Pública Estadual" e que estivessem com o status de funcionamento como "Em atividade". Esse processo de filtragem é essencial para assegurar que a aplicação funcione de maneira eficiente e confiável, proporcionando aos usuários informações precisas e relevantes.

### Dados de Mestrado e Doutorado

Quanto aos dados referentes aos cursos de mestrado e doutorado, estes foram adquiridos a partir do portal de dados abertos da Capes, especificamente na seção Programas da Pós-Graduação Stricto Sensu no Brasil. Estes dados estão disponíveis para consulta pública no seguinte link: [Portal de Dados Abertos da Capes - Programas da Pós-Graduação Stricto Sensu no Brasil](https://dadosabertos.capes.gov.br/dataset/2017-a-2020-programas-da-pos-graduacao-stricto-sensu-no-brasil).

Da mesma forma que com os dados de graduação, aplicamos filtros específicos para refinar os dados de mestrado e doutorado. Os critérios de filtragem incluíam a seleção de programas que estivessem "Em funcionamento" e cuja dependência administrativa fosse classificada como "Pública". Essa abordagem assegura que somente programas de pós-graduação ativos e gerenciados por instituições públicas sejam incluídos na nossa base de dados. 

Esse cuidado na seleção dos dados é fundamental para manter a relevância e a qualidade das informações disponibilizadas pelo "Guia das Federais". Nosso objetivo é fornecer aos usuários um recurso confiável e atualizado, que facilite a busca por opções educacionais em universidades públicas brasileiras.

## Disclaimer

Este projeto é uma iniciativa independente, e apesar dos esforços para garantir a precisão das informações, pode haver erros. Recomenda-se usar os dados por sua conta e risco, sem garantias.

## Versão JavaScript para GitHub Pages

Para hospedar o Guia das Federais como site estático (sem backend), foi criada uma versão em JavaScript na pasta `webapp`. Ela usa um banco SQLite embarcado com `sql.js` (WebAssembly), renderiza as tabelas com `gridjs` e faz cache do banco em IndexedDB via `localforage`. Assim, depois do primeiro carregamento o usuário não precisa baixar tudo novamente.

- Página de entrada: `webapp/index.html` (apontar o GitHub Pages para essa pasta ou mover os arquivos para a branch de publicação).
- Banco de dados: `webapp/public/data/guia.sqlite` (já versionado; ~10 MB).
- Bibliotecas via CDN: `sql.js`, `gridjs`, `bootstrap` e `localforage`.

### Atualizar a base SQLite

1. Deixe os CSVs tratados atualizados na raiz.
2. Gere o banco consolidado:
   ```bash
   python3 build_sqlite_db.py
   ```
   Isso recria `webapp/public/data/guia.sqlite` com índices para filtros rápidos.
3. Publique a pasta `webapp` no GitHub Pages (ou sirva localmente com qualquer servidor estático).

### Usando o site estático

1. Abra `webapp/index.html`.
2. Escolha a aba (Graduação, Especialização ou Mestrado/Doutorado) e aplique os filtros.
3. Exporte os resultados em CSV quando quiser.
4. O SQLite é baixado uma vez e guardado em cache local automaticamente.
