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

# Medidas
count_garantia_ativa = len(df[df["Garantia"] == "Ativa"])

# Dasgboard
# Cabeçaçho
st.title("Relatório de Dispositivos")
st.subheader(f"{df['Departamento'].iloc[0]}")

# Segmentação de Dados no Navegador Lateral
SETORES = df["Setor"].unique()
GARANTIA = df["Garantia"].unique()
TIPOS_DISCO = df["TipoDisco"].unique()
TIPOS_EQUIPAMENTO = df["TipoEquipamento"].unique()

select_setor = st.sidebar.selectbox("Selecione o Setor", SETORES)
select_garantia = st.sidebar.radio("Garantia", GARANTIA)
select_tipo_disco = st.sidebar.radio("Garantia", TIPOS_DISCO)
select_tipo_equipamento = st.sidebar.radio("Garantia", TIPOS_EQUIPAMENTO)

# Treemap - Dispositivos por Setor
treemap = px.treemap(
    df,
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
treemap.update_layout(margin=dict(t=50, l=0, r=0, b=0))

col1, col2 = st.columns(2)
col1.plotly_chart(treemap)

# Indicador - Garantia
indicator = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=count_garantia_ativa,
        title={"text": "Garantia"},
        gauge={
            "axis": {"range": [None, len(df)]},
            "bgcolor": "#061953",
            "bar": {"color": "#0050EB"},
        },
    )
)
indicator.update_layout()
col2.plotly_chart(indicator)
