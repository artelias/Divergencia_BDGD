import pandas as pd
import altair as alt
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Custos Operacionais - ICO TOTAL", page_icon="💰")
st.title("💰 Relatório de Custos Operacionais - ICO TOTAL")
st.write(
    """
    Este dashboard interativo apresenta os dados de custos operacionais do relatório **ICO TOTAL**.
    Explore os valores ao longo dos anos por unidade ou distribuidora (`DIST`).
    """
)

# Leitura e pré-processamento
@st.cache_data
def load_data():
    df = pd.read_csv("ICO TOTAL.txt", sep=";", encoding="utf-8")
    df["DATA_BASE"] = pd.to_datetime(df["DATA_BASE"], dayfirst=True)
    df["Ano"] = df["DATA_BASE"].dt.year
    df["Próprio_Distribuidor"] = pd.to_numeric(df["Próprio_Distribuidor"], errors="coerce")
    df["Diferente_Próprio_Distribuidor"] = pd.to_numeric(df["Diferente_Próprio_Distribuidor"], errors="coerce")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    return df

df = load_data()

# Filtros
anos = st.slider("Ano", int(df["Ano"].min()), int(df["Ano"].max()), (int(df["Ano"].min()), int(df["Ano"].max())))
dists = st.multiselect("DIST (Distribuidora ou Área)", sorted(df["DIST"].unique()), default=sorted(df["DIST"].unique()))

df_filtrado = df[
    (df["Ano"].between(anos[0], anos[1])) &
    (df["DIST"].isin(dists))
]

# Agregação
df_agg = df_filtrado.groupby("Ano")[["Próprio_Distribuidor", "Diferente_Próprio_Distribuidor", "Total"]].sum().reset_index()

# Tabela de dados
st.subheader("📊 Tabela Agregada por Ano")
st.dataframe(df_agg, use_container_width=True)

# Gráfico de linhas
st.subheader("📈 Evolução dos Custos Operacionais")

df_melt = df_agg.melt(id_vars="Ano", var_name="Tipo", value_name="Valor")

chart = (
    alt.Chart(df_melt)
    .mark_line(point=True)
    .encode(
        x=alt.X("Ano:O", title="Ano"),
        y=alt.Y("Valor:Q", title="Custo (R$)"),
        color="Tipo:N"
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)
