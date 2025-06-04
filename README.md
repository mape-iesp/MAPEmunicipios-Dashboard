# Dashboard do `mape_municipios`

Dashboard interativo, construído em **Streamlit**, que facilita a exploração e o acompanhamento de indicadores do projeto **MAPE Municípios**.
O pipeline de dados coleta, limpa e armazena informações em um banco **DuckDB** utilizado diretamente pelo aplicativo.

## Índice

1. [Visão geral](#visão-geral)
2. [Estrutura do repositório](#estrutura-do-repositório)
3. [Pré‑requisitos](#pré-requisitos)
4. [Instalação](#instalação)
6. [Executando a aplicação](#executando-a-aplicação)
7. [Licença](#licença)

## Visão geral

O repositório contém dois componentes principais:

* **Scripts de processamento** (`src/*.py`) – automatizam a etapa ETL (Extract, Transform, Load) e criam o arquivo `mape.duckdb`.
* **Aplicação Streamlit** (`src/streamlit_app.py`) – consome o banco gerado e exibe o dashboard ao usuário final.

> **Nota:** Todos os arquivos em `data/` são intermediários; somente `data/mape.duckdb` é lido pela aplicação.

## Estrutura do repositório

```
MAPEMUNICIPIOS-DASHBOARD/
├── data/                 # Arquivos intermediários do pipeline
│   ├── base_municipios_brasileiros_flt.csv
│   ├── base_municipios_brasileiros.csv
│   ├── dicionario.csv
│   ├── municipalities.csv
│   └── mape.duckdb       # Banco de dados usado pelo Streamlit
├── img/                  # Recursos visuais (favicon, logos etc.)
│   ├── favicon.ico
│   └── mape.jpg
├── src/                  # Código‑fonte
│   ├── download_geometry.py   # Baixa geometrias dos municípios
│   ├── filter_dataset.py      # Filtra e padroniza bases CSV
│   ├── create_duckdb.py       # Gera o banco DuckDB
│   └── streamlit_app.py       # Dashboard web
├── requirements.txt      # Dependências Python
├── README.md             # (este arquivo)
├── LICENSE               # Tipo de licença
└── .gitignore            # Arquivos/paths ignorados pelo Git
```

## Instalação

```bash
# Clone o repositório
git clone https://github.com/<usuario>/MAPEMUNICIPIOS-DASHBOARD.git
cd MAPEMUNICIPIOS-DASHBOARD

# Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

## Executando a aplicação

```bash
streamlit run src/streamlit_app.py
```

O comando acima abrirá o Streamlit em `http://localhost:8501/` no seu navegador padrão. O app utiliza apenas o banco `data/mape.duckdb`, que é gerado pelo pipeline de dados, e as imagens em `img/`.

O app já está no ar em [https://mape-municipios-dashboard.streamlit.app/](https://mape-municipios-dashboard.streamlit.app/). Esse Streamlit App não lê diretamente deste repositório, mas de um repositório privado mantido por [@felipelmc](https://github.com/felipelmc), porque o deploy a partir deste repositório esbarrou em problemas de permissão.

## Licença

Distribuído sob os termos da licença definida em [`LICENSE`](LICENSE).
