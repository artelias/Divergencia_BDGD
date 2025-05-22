import altair as alt
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Custos Operacionais - ICO TOTAL", page_icon="💰")
st.title("💰 Relatório de Custos Operacionais - ICO TOTAL")
st.write(
    """
    Este dashboard interativo apresenta os dados de custos operacionais do relatório **ICO TOTAL**.
    Explore os valores ao longo dos anos por unidade (`DIST`), item (`ITEM`) ou grupo temático.
    """
)

# Leitura e pré-processamento
@st.cache_data
def load_data():
    df = pd.read_csv(
        "/workspaces/Divergencia_BDGD/data/ICO TOTAL.txt",
        sep=";",
        encoding="utf-8",
        thousands="."  # Corrige a interpretação de ponto como separador de milhar
    )
    df["DATA_BASE"] = pd.to_datetime(df["DATA_BASE"], dayfirst=True)
    df["Ano"] = df["DATA_BASE"].dt.year
    df["Próprio_Distribuidor"] = pd.to_numeric(df["Próprio_Distribuidor"], errors="coerce")
    df["Diferente_Próprio_Distribuidor"] = pd.to_numeric(df["Diferente_Próprio_Distribuidor"], errors="coerce")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

    # Categorização por grupo de ITEM
    def categorizar_item(item):
        item = item.upper()
        if "CONSUMIDOR" in item:
            return "Consumidores"
        elif "POTÊNCIA" in item:
            return "Potência"
        elif "TRANSFORMADOR" in item:
            return "Transformadores"
        elif "REDE" in item:
            return "Rede"
        else:
            return "Outros"

    df["Grupo"] = df["ITEM"].apply(categorizar_item)

    return df

df = load_data()

# Filtros
anos = st.slider("Ano", int(df["Ano"].min()), int(df["Ano"].max()), (int(df["Ano"].min()), int(df["Ano"].max())))
dists = st.multiselect("DIST (Distribuidora ou Área)", sorted(df["DIST"].unique()), default=sorted(df["DIST"].unique()))
itens = st.multiselect("Grupo", sorted(df["Grupo"].unique()), default=sorted(df["Grupo"].unique()))

# Aplicando filtros
df_filtrado = df[
    (df["Ano"].between(anos[0], anos[1])) &
    (df["DIST"].isin(dists)) &
    (df["Grupo"].isin(itens))
]

# Tabela agregada por Ano
df_agg = df_filtrado.groupby("Ano")[["Próprio_Distribuidor", "Diferente_Próprio_Distribuidor", "Total"]].sum().reset_index()

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

# Tabela pivô: ITEM nas linhas, ANO nas colunas
st.subheader("🧾 Tabela por ITEM e Ano (Total em R$)")
df_pivot = df_filtrado.pivot_table(
    index="ITEM",
    columns="Ano",
    values="Total",
    aggfunc="sum",
    fill_value=0
).round(2)
st.dataframe(df_pivot, use_container_width=True)

# Tabela pivô: Grupo nas linhas, Ano nas colunas
st.subheader("📁 Tabela por Grupo e Ano (Total em R$)")
df_grupo_pivot = df_filtrado.pivot_table(
    index="Grupo",
    columns="Ano",
    values="Total",
    aggfunc="sum",
    fill_value=0
).round(2)
st.dataframe(df_grupo_pivot, use_container_width=True)

st.markdown(
    """
    As tabelas acima mostram os custos totais por **ITEM** e por **Grupo temático**, distribuídos por ano.
    Os valores são apresentados em reais (R$). Use os filtros acima para explorar diferentes combinações.
    """
)


st.title("🌐 Relatório de Dados Técnicos - BDGD")
st.write(
    """
    Este dashboard interativo apresenta os **dados técnicos da BDGD** do **Grupo Energisa**.
    Explore as informações por unidade (`DIST`), tipo de componente (`TUC`) ou grupo temático de equipamentos.
    """
)



# Leitura do arquivo fato
@st.cache_data
def load_fato():
    df_fato = pd.read_csv("/workspaces/Divergencia_BDGD/data/fato.csv", sep=";", encoding="utf-8")
    df_fato["DATA_BASE"] = pd.to_datetime(df_fato["DATA_BASE"], dayfirst=True)
    return df_fato

df_fato = load_fato()

# Dicionário original (empresa: dist)
distribuicao = {
    'EAC': 26,
    'EPB': 6600,
    'EMT': 405,
    'EMS': 404,
    'ESS': 5216,
    'ESE': 6587,
    'ERO': 369,
    'EMR': 6585,
    'ETO': 32
}

# Inverter dicionário (dist: empresa)
distribuicao_invertido = {v: k for k, v in distribuicao.items()}

# Substituir DIST pelo nome da empresa
df_fato["DIST"] = df_fato["DIST"].map(distribuicao_invertido)

# Dicionário de descrição do TUC
descricao_tuc = {
    125: 'BANCO DE CAPACITORES',
    135: 'BARRAMENTO',
    160: 'CHAVE',
    210: 'DISJUNTOR',
    255: 'ESTRUTURA (POSTE, TORRE)',
    295: 'MEDIDOR',
    330: 'REATOR',
    340: 'REGULADOR',
    345: 'RELIGADOR',
    540: 'SUBESTAÇÃO SF 6',
    545: 'SUBESTAÇÃO UNITÁRIA',
    565: 'TRANSFORMADOR DE DISTRIBUIÇÃO',
    570: 'TRANSFORMADOR DE FORÇA',
    575: 'TRANSFORMADOR DE MEDIDA'
}

# Converter TUC para inteiro e remover nulos ou zeros
df_fato["TUC"] = pd.to_numeric(df_fato["TUC"], errors="coerce").fillna(0).astype(int)
df_fato = df_fato[df_fato["TUC"] != 0]

# Adicionar descrição
df_fato["DESCRICAO_TUC"] = df_fato["TUC"].map(descricao_tuc)

# Filtros interativos (caixas suspensas)
dist_filtro = st.selectbox("Distribuidora (DIST)", sorted(df_fato["DIST"].dropna().unique()))
tuc_filtro = st.selectbox("Tipo de Unidade Consumidora (TUC)", sorted(df_fato["DESCRICAO_TUC"].dropna().unique()))

# Aplicando filtros
df_filtrado = df_fato[
    (df_fato["DIST"] == dist_filtro) &
    (df_fato["DESCRICAO_TUC"] == tuc_filtro)
]

# Agregação: total de unidades e extensão de rede
df_resumo = df_filtrado.groupby(["TUC", "DESCRICAO_TUC"]).agg(
    Quantidade_Unidades=("QTD", "sum"),
    Extensao_Rede_km=("SOMA_REDE_KM", "sum")
).reset_index()

# Exibição
st.subheader("📦 Quadro Resumo por Tipo de Unidade Consumidora (TUC)")
st.dataframe(df_resumo, use_container_width=True)

st.markdown(
    """
    O quadro acima mostra a quantidade de unidades e a extensão de rede (em km) por tipo de unidade consumidora.
    Os filtros acima permitem visualizar os dados por distribuidora e tipo de equipamento.
    """
)
