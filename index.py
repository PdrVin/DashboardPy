import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Tamanho Layout
st.set_page_config(layout="wide")

# Origem dos Dados
df = pd.read_csv("./data/DadosManutencao.csv", delimiter=";")

# Tratamento de Dados
df["Patrimônio"] = df["Patrimônio"].astype(str)
df["IdadeExtenso"] = df["IdadeExtenso"].astype(str)
df["Aquisição"] = pd.to_datetime(df["Aquisição"], format="%d/%m/%Y")
df["Expiração"] = pd.to_datetime(df["Expiração"], format="%d/%m/%Y")

# Transformação de Dados
df["Categoria"] = df["Idade"].apply(
    lambda x: "Ótimo" if x <= 5 else ("Regular" if x <= 9 else "Antigo")
)
df["Situação"] = np.where(
    (df["Idade"] >= 9)
    | ((df["Geração"] <= 6) & (df["CPU"] != "AMD Ryzen 7 3700U"))
    | (df["Memória"].isin(["04 GB", "06 GB"]))
    | (df["TipoDisco"] == "HDD"),
    "Precária",
    "Satisfatória",
)

# Segmentação de Dados no Navegador Lateral
SETORES = ["Todos"] + list(df["Setor"].unique())
GARANTIA = ["Todos"] + list(df["Garantia"].unique())
TIPOS_DISCO = ["Todos"] + list(df["TipoDisco"].unique())
TIPOS_EQUIPAMENTO = ["Todos"] + list(df["TipoEquipamento"].unique())

select_setor = st.sidebar.radio("Selecione o Setor", SETORES, index=0)
select_garantia = st.sidebar.radio("Garantia", GARANTIA, index=0)
select_tipo_disco = st.sidebar.radio("Tipo de Disco", TIPOS_DISCO, index=0)
select_tipo_equip = st.sidebar.radio("Tipo de Equipamento", TIPOS_EQUIPAMENTO, index=0)

# Aplicando filtros ao DataFrame
df_filter = df.copy()

if select_setor != "Todos":
    df_filter = df_filter[df_filter["Setor"] == select_setor]

if select_garantia != "Todos":
    df_filter = df_filter[df_filter["Garantia"] == select_garantia]

if select_tipo_disco != "Todos":
    df_filter = df_filter[df_filter["TipoDisco"] == select_tipo_disco]

if select_tipo_equip != "Todos":
    df_filter = df_filter[df_filter["TipoEquipamento"] == select_tipo_equip]

# Medidas
num_dispositivos = len(df_filter["ServiceTag"])
count_garantia_ativa = len(df_filter[df_filter["Garantia"] == "Ativa"])

# Dasgboard
# Cabeçaçho
st.title("Relatório de Dispositivos")
st.subheader(f"{df['Departamento'].iloc[0]}", divider="blue")

col1, col2, col3 = st.columns([1, 2, 2])

col1.metric("***Dispositivos***", num_dispositivos, border=True)


# Treemap - Dispositivos por Setor
treemap = px.treemap(
    df_filter,
    path=["Setor"],
    title="Dispositivos por Setor",
    color_discrete_sequence=[
        "#0B31A5",  # Azul Escuro
        "#0641C8",  # Azul Médio
        "#0050EB",  # Azul Brilhante
        "#0078ED",  # Azul Claro
        "#008CEE",  # Azul Céu
        "#009FEF",  # Azul Água
        "#46B3F3",  # Azul Pastel
        "#8BC7F7",  # Azul Bebê
    ],
)
treemap.update_traces(root_color="#061953", textinfo="label+value", textfont_size=16)
treemap.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=300)
col2.plotly_chart(treemap)

# Indicador - Garantia
indicator = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=count_garantia_ativa,
        title={
            "text": "Garantia",
            "align": "left",
            "font": {"size": 16, "weight": 500},
        },
        gauge={
            "axis": {"range": [None, len(df_filter)]},
            "bgcolor": "#061953",
            "bar": {"color": "#0050EB", "thickness": 0.7},
        },
    )
)
indicator.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=350)
col3.plotly_chart(indicator)

# Grafico Colunas - Dispositivos por Ano de Aquisição
df_filter["Ano"] = df_filter["Aquisição"].dt.year.astype(str)
df_age_category = (
    df_filter.groupby(["Ano", "Categoria"]).size().reset_index(name="Contagem")
)

# Cores
color_map = {"Ótimo": "#ffffff", "Regular": "#66c5f5", "Antigo": "#0078ED"}

age_column = px.bar(
    df_age_category,
    title="Computadores Adquiridos",
    x="Ano",
    y="Contagem",
    labels={"Ano": "", "Contagem": ""},
    color="Categoria",
    color_discrete_map=color_map,
    height=400,
    text="Contagem",
)
age_column.update_xaxes(type="category")
age_column.update_layout(
    margin=dict(t=50, l=0, r=0, b=0),
    yaxis=dict(range=[0, max(df_age_category["Contagem"]) + 1]),
)
st.plotly_chart(age_column)
