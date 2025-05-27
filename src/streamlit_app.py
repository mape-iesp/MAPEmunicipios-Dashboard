import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from shapely import wkt
import duckdb
import json
from shapely.geometry import shape

# -------------------------------------------------
# 🎨  Identidade visual
# -------------------------------------------------
BRAND = {
    "brown": "#cb8106",
    "olive": "#a9a64b",
    "sand": "#f6f5ef",
    "graph_bg": "#ffffff",
    "text": "#1e1e1e",
}

pio.templates["mape"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color=BRAND["text"], size=14),
        paper_bgcolor=BRAND["graph_bg"],
        plot_bgcolor=BRAND["graph_bg"],
        colorway=[BRAND["brown"], BRAND["olive"], "#7a7a7a"],
        margin=dict(l=0, r=0, t=40, b=0),
    )
)
pio.templates.default = "plotly_white+mape"

CHORO_SCALE = [
    [0.0, "#f1efe8"],
    [0.25, "#d9d3b5"],
    [0.5, BRAND["olive"]],
    [0.75, "#b89555"],
    [1.0, BRAND["brown"]],
]

# -------------------------------------------------
# ⚙️  Configuração da página
# -------------------------------------------------
st.set_page_config(page_title="MAPE | Indicadores Municipais",
                   page_icon="../img/favicon.ico", layout="wide")

st.markdown(
    f"""
    <style>
        /* Aplica branco apenas ao conteúdo textual da barra lateral */
        [data-testid="stSidebar"] > div:first-child p,
        [data-testid="stSidebar"] > div:first-child a,
        [data-testid="stSidebar"] > div:first-child h1,
        [data-testid="stSidebar"] > div:first-child h2,
        [data-testid="stSidebar"] > div:first-child h3,
        [data-testid="stSidebar"] > div:first-child h4,
        [data-testid="stSidebar"] > div:first-child h5,
        [data-testid="stSidebar"] > div:first-child h6,
        [data-testid="stSidebar"] > div:first-child span {{
            color: white !important;
        }}

        /* Mantém os textos dos inputs (select, etc) em preto */
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stSelectbox * {{
            color: black !important;
        }}

        .main {{
            background-color: {BRAND['brown']};
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background-color: {BRAND['brown']};
        }}

        .stButton > button {{
            background-color: {BRAND['olive']} !important;
            color: #fff !important;
            border: none !important;
            border-radius: 8px !important;
        }}

        .stButton > button:hover {{
            background-color: {BRAND['brown']} !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {BRAND['brown']};
            font-weight: 600;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.image("../img/mape.jpg", use_container_width=True)
st.sidebar.markdown(
    """
    **MAPE** é o Laboratório de Monitoramento e Avaliação de Políticas e Eleições do
    Instituto de Estudos Sociais e Políticos (IESP-UERJ). 
    Somos um grupo de pesquisa empírico em Ciências Sociais que estuda políticas públicas e 
    eleições para apoiar a tomada de decisão baseada em evidências.
    Conheça mais sobre o nosso trabalho em [https://mape.org.br/](https://mape.org.br/).
    """
)


# -------------------------------------------------
# 🏷️  Apresentação 
# -------------------------------------------------
st.title("`mape_municipios`")
st.markdown("""
            Dada a importância dos municípios para implementação de políticas públicas, 
            e as grandes variações e desigualdades entre eles, o MAPE criou o `mape_municipios`. 
            Consiste em um dos mais completos bancos de dados sobre informações dos municípios 
            brasileiros, cobrindo escopo temporal de 30 anos, 17 dimensões, 31 pesquisas e 451 variáveis. 
            O objetivo é oferecer informações de maneira unificada e qualificada para pesquisadores/as, 
            gestores/as e sociedade civil, que embase boas pesquisas e boa tomada de decisão no campo das 
            políticas públicas.
            
            Nessa aplicação, você pode explorar os dados de forma interativa. No painel lateral,
            escolha o indicador e o ano desejados. Você verá um mapa coroplético, um gráfico de linha
            com a evolução temporal do indicador e um gráfico de dispersão para comparar dois indicadores.
            """)


# -------------------------------------------------
# 📂 DuckDB connection & lazy tables
# -------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_duckdb():
    con = duckdb.connect("../data/mape.duckdb", read_only=True)
    # spatial + httpfs are the only two extra things we need
    con.execute("LOAD spatial;")
    return con

con = get_duckdb()                 # ← replace the global `con = duckdb.connect(...)`


# -------------------------------------------------
# 🔢 Preparação de variáveis 
# -------------------------------------------------
exclude_cols = ["ano", "id_municipio", "geometry"]
cols_info = con.sql("PRAGMA table_info('mape_municipios')").df()
indicator_cols = [c for c in cols_info["name"].tolist() if c not in exclude_cols]


# -------------------------------------------------
# 🧭 Sidebar
# -------------------------------------------------
st.sidebar.header("Configurações")

padrao = "total_desastres" if "total_desastres" in indicator_cols else indicator_cols[0]
indicador1 = st.sidebar.selectbox("Indicador principal:", indicator_cols,
                                 index=indicator_cols.index(padrao))

anos_validos = con.sql(
    f"SELECT DISTINCT ano FROM mape_municipios WHERE {indicador1} IS NOT NULL ORDER BY ano"
).df()["ano"].tolist()

if not anos_validos:
    st.error("Indicador selecionado sem valores.")
    st.stop()

default_year = 2023 if 2023 in anos_validos else anos_validos[-1]
ano = st.sidebar.selectbox("Ano:", anos_validos, index=anos_validos.index(default_year))

indicator_cols2 = [c for c in indicator_cols if c != indicador1]
indicador2 = (
    indicador1 if not indicator_cols2 else st.sidebar.selectbox("Segundo indicador:", indicator_cols2)
)

dicionario = con.sql(
    f"""
    SELECT Nome_banco, Descrição
    FROM dicionario_mape_municipios
    WHERE Nome_banco = '{indicador1}' OR Nome_banco = '{indicador2}'
    """
).df()

# mostrar dicionário de dados
if not dicionario.empty:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dicionário de Dados")
    for _, row in dicionario.iterrows():
        st.sidebar.markdown(f"**{row['Nome_banco']}**: {row['Descrição']}")


######################
st.markdown("---")
######################


# -------------------------------------------------
# 🗺️  1. Mapa coroplético
# -------------------------------------------------
st.subheader(f"🗺️ Distribuição territorial » {indicador1.replace('_',' ').capitalize()} ({ano})")

tbl = con.sql(
    f"""
    SELECT m.name_muni AS nome_municipio,
           d.{indicador1},
           ST_AsText(m.geometry) AS geometry_wkt
    FROM   mape_municipios d
    JOIN   municipalities  m 
    ON d.id_municipio = m.code_muni
    WHERE  d.ano = {ano} AND d.{indicador1} IS NOT NULL
    """
).df()

tbl["geometry"] = gpd.GeoSeries.from_wkt(tbl["geometry_wkt"])
gdf = gpd.GeoDataFrame(tbl, geometry="geometry")
gdf = gdf.drop(columns=["geometry_wkt"])


fig_map = px.choropleth_map(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    color=indicador1,
    hover_data={"nome_municipio": True, indicador1: ":.2f"},
    map_style="carto-positron",
    zoom=3,
    center={"lat": -14.235, "lon": -51.9253},
    opacity=0.8,
    color_continuous_scale=CHORO_SCALE,
    labels={indicador1: indicador1.replace('_',' ').capitalize()},
    template="mape",
)
# Barra de cor horizontal
fig_map.update_coloraxes(colorbar=dict(title="", 
                                       orientation="h", 
                                       x=0.5, 
                                       y=-0.15,
                                       xanchor="center", 
                                       yanchor="top", 
                                       len=0.7,
                                       thickness=15))

# aumenta o tamanho do mapa
fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=650)
st.plotly_chart(fig_map, use_container_width=True)


######################
st.markdown("---")
######################


# -------------------------------------------------
# 📈  2. Gráfico de linha
# -------------------------------------------------
st.subheader(f"📈 Evolução temporal » {indicador1.replace('_',' ').capitalize()} ({ano})")

line_df = con.sql(
    f"""
    SELECT ano, SUM({indicador1}) AS {indicador1}
    FROM mape_municipios
    WHERE {indicador1} IS NOT NULL
    GROUP BY ano
    HAVING SUM({indicador1}) > 0
    ORDER BY ano
    """
).df()

fig_line = px.area(
    line_df,
    x="ano",
    y=indicador1,
    labels={"ano": "Ano", indicador1: indicador1.replace('_',' ').capitalize()},
    template="mape",
)
fig_line.update_traces(line=dict(width=2, color=BRAND["brown"]), opacity=0.3)

# Linha sobreposta para contorno
fig_line.add_scatter(x=line_df["ano"], y=line_df[indicador1], mode="lines",
                     line=dict(width=3, color=BRAND["olive"]), showlegend=False)
# Destaque do último ponto
fig_line.add_scatter(x=[line_df["ano"].iloc[-1]],
                     y=[line_df[indicador1].iloc[-1]],
                     mode="markers+text",
                     marker=dict(size=12, color=BRAND["brown"]),
                     text=[f"{line_df[indicador1].iloc[-1]:.2f}"], textposition="top center",
                     showlegend=False)

fig_line.update_yaxes(showgrid=True, gridcolor=BRAND["sand"], zeroline=False)
fig_line.update_xaxes(showgrid=False)

st.plotly_chart(fig_line, use_container_width=True)


######################
st.markdown("---")
######################


# -------------------------------------------------
# 🔄  3. Scatterplot comparação
# -------------------------------------------------
st.subheader(f"🔬 Relação entre indicadores » {indicador1.replace('_',' ').capitalize()} x  {indicador2.replace('_',' ').capitalize()} ({ano})")

scat_df = con.sql(
    f"""
    SELECT m.name_muni AS nome_municipio, 
           d.{indicador1}, 
           d.{indicador2}
    FROM mape_municipios AS d
    JOIN   municipalities AS m 
    ON d.id_municipio = m.code_muni
    WHERE ano = {ano} AND {indicador1} IS NOT NULL AND {indicador2} IS NOT NULL
    """,
).df()

if scat_df.empty:
    st.info("Sem dados suficientes para o scatterplot.")
else:
    fig_scat = px.scatter(
        scat_df,
        x=indicador1,
        y=indicador2,
        size_max=25,
        hover_name="nome_municipio",
        trendline="ols",
        opacity=0.7,
        labels={
            indicador1: indicador1.replace('_',' ').capitalize(),
            indicador2: indicador2.replace('_',' ').capitalize(),
        },
        template="mape",
    )

    st.plotly_chart(fig_scat, use_container_width=True)

