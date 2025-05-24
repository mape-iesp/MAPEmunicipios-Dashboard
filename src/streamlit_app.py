import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from shapely import wkt

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
        .main {{background-color:{BRAND['brown']};}}
        [data-testid="stSidebar"] > div:first-child {{background-color:{BRAND['brown']};}}
        .stButton > button {{background-color:{BRAND['olive']}!important;
                             color:#fff!important; border:none!important; border-radius:8px!important;}}
        .stButton > button:hover {{background-color:{BRAND['brown']}!important;}}
        h1,h2,h3,h4,h5,h6 {{color:{BRAND['brown']}; font-weight:600;}}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 📂 Carregamento dos dados (cache)
# -------------------------------------------------
@st.cache_data(show_spinner="Carregando dados…")
def load_data():
    df = pd.read_csv("../data/base_municipios_brasileiros_flt.csv")
    municipalities = pd.read_csv("../data/municipalities.csv")
    return df, municipalities

try:
    df, municipalities = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

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
# 🔢 Preparação de variáveis 
# -------------------------------------------------
exclude_cols = ["ano", "id_municipio", "geometry"]
indicator_cols = [c for c in df.columns if c not in exclude_cols]


# -------------------------------------------------
# 🧭 Sidebar
# -------------------------------------------------
st.sidebar.header("Configurações")

padrao = "total_desastres" if "total_desastres" in indicator_cols else indicator_cols[0]
indicador1 = st.sidebar.selectbox("Indicador principal:", indicator_cols,
                                 index=indicator_cols.index(padrao))

anos_validos = sorted(df.loc[df[indicador1].notna(), "ano"].unique())
if not anos_validos:
    st.error("Indicador selecionado sem valores.")
    st.stop()

default_year = 2023 if 2023 in anos_validos else anos_validos[-1]
ano = st.sidebar.selectbox("Ano:", anos_validos, index=anos_validos.index(default_year))

indicator_cols2 = [c for c in indicator_cols if c != indicador1]
indicador2 = (
    indicador1 if not indicator_cols2 else st.sidebar.selectbox("Segundo indicador:", indicator_cols2)
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


######################
st.markdown("---")
######################

# -------------------------------------------------
# 🗺️  1. Mapa coroplético
# -------------------------------------------------
st.subheader(f"🌎 Distribuição territorial » {indicador1.replace('_',' ').capitalize()} ({ano})")

map_df = (
    df[df["ano"] == ano]
      .merge(municipalities, left_on="id_municipio", right_on="code_muni", how="left")
      .dropna(subset=["geometry"])
)
map_df["geometry"] = map_df["geometry"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(map_df, geometry="geometry")

fig_map = px.choropleth_map(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    color=indicador1,
    hover_data={"id_municipio": True, indicador1: ":.2f"},
    map_style="carto-positron",
    zoom=3,
    center={"lat": -14.235, "lon": -51.9253},
    opacity=0.8,
    color_continuous_scale=CHORO_SCALE,
    labels={indicador1: indicador1.replace('_',' ').capitalize()},
    template="mape",
)
# Barra de cor horizontal
fig_map.update_coloraxes(colorbar=dict(title="", orientation="h", x=0.5, y=-0.15,
                                       xanchor="center", yanchor="top", len=0.7,
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

line_df = df.groupby("ano")[indicador1].sum().reset_index().sort_values("ano")
line_df.query(f"{indicador1} > 0", inplace=True)


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

scat_df = df[df["ano"] == ano].dropna(subset=[indicador1, indicador2])

if scat_df.empty:
    st.info("Sem dados suficientes para o scatterplot.")
else:
    fig_scat = px.scatter(
        scat_df,
        x=indicador1,
        y=indicador2,
        size_max=25,
        hover_name="id_municipio",
        trendline="ols",
        opacity=0.7,
        labels={
            indicador1: indicador1.replace('_',' ').capitalize(),
            indicador2: indicador2.replace('_',' ').capitalize(),
        },
        template="mape",
    )

    st.plotly_chart(fig_scat, use_container_width=True)

