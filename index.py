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
df["Ano"] = df["Aquisição"].dt.year

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
SETORES = ["-"] + list(df["Setor"].unique())
GARANTIA = ["-"] + list(df["Garantia"].unique())
TIPOS_DISCO = ["-"] + list(df["TipoDisco"].unique())
TIPOS_EQUIPAMENTO = ["-"] + list(df["TipoEquipamento"].unique())

select_setor = st.sidebar.selectbox("Setor", SETORES, index=0)
select_garantia = st.sidebar.selectbox("Garantia", GARANTIA, index=0)
select_tipo_disco = st.sidebar.selectbox("Tipo de Disco", TIPOS_DISCO, index=0)
select_tipo_equip = st.sidebar.selectbox(
    "Tipo de Equipamento", TIPOS_EQUIPAMENTO, index=0
)

# Aplicando filtros ao DataFrame
df_filter = df.copy()

if select_setor != "-":
    df_filter = df_filter[df_filter["Setor"] == select_setor]

if select_garantia != "-":
    df_filter = df_filter[df_filter["Garantia"] == select_garantia]

if select_tipo_disco != "-":
    df_filter = df_filter[df_filter["TipoDisco"] == select_tipo_disco]

if select_tipo_equip != "-":
    df_filter = df_filter[df_filter["TipoEquipamento"] == select_tipo_equip]

# Medidas
num_dispositivos = len(df_filter["ServiceTag"])
count_garantia_ativa = len(df_filter[df_filter["Garantia"] == "Ativa"])


# Treemap - Dispositivos por Setor
def sector_treemap():
    fig = px.treemap(
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
    fig.update_traces(root_color="#061953", textinfo="label+value", textfont_size=16)
    fig.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=250)
    return fig


# Indicador - Garantia
def warranty_indicator():
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=count_garantia_ativa,
            title={
                "text": "Garantia",
                "font": {
                    "size": 17,
                    "weight": 700,
                },
            },
            gauge={
                "axis": {
                    "range": [None, len(df_filter)],
                    "tickfont": {"size": 16},
                },
                "bgcolor": "#061953",
                "bar": {"color": "#0050EB", "thickness": 0.7},
            },
        )
    )
    fig.update_layout(margin=dict(t=40, l=30, r=30, b=0), height=200)
    return fig


# Grafico Colunas - Dispositivos por Ano de Aquisição
def age_column():
    df_age_category = (
        df_filter.groupby(["Ano", "Categoria"]).size().reset_index(name="Contagem")
    )

    color_map = {"Ótimo": "#ffffff", "Regular": "#66c5f5", "Antigo": "#0078ED"}

    fig = px.bar(
        df_age_category,
        title="Computadores Adquiridos",
        x="Ano",
        y="Contagem",
        labels={"Ano": "", "Contagem": ""},
        color="Categoria",
        color_discrete_map=color_map,
        height=350,
        text="Contagem",
    )
    fig.update_xaxes(type="category")
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        yaxis=dict(range=[0, max(df_age_category["Contagem"]) + 1]),
    )
    return fig


# Gráfico Barras - Dispositivos por Memória e Tipo
def memory_bar():
    df_memoria = (
        df_filter.groupby(["Memória", "TipoMemória"])
        .size()
        .reset_index(name="Contagem")
    )
    fig = px.bar(
        df_memoria,
        title="Memória",
        y="Memória",
        x="Contagem",
        text="Contagem",
        labels={"Memória": "", "Contagem": ""},
        color="TipoMemória",
        color_discrete_map={
            "DDR3": "#0050EB",
            "DDR4": "#ffffff",
        },
        orientation="h",
        height=350,
    )
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis=dict(range=[0, df_memoria.groupby(["Memória"]).size() + 1]),
        yaxis={"categoryorder": "total ascending"},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


# Gráfico Barras - Dispositivos por Memória e Tipo
def storage_bar():
    df_storage = (
        df_filter.groupby(["Armazenamento", "TipoDisco"])
        .size()
        .reset_index(name="Contagem")
    )
    fig = px.bar(
        df_storage,
        title="Armazenamento",
        y="Armazenamento",
        x="Contagem",
        text="Contagem",
        labels={"Armazenamento": "", "Contagem": ""},
        color="TipoDisco",
        color_discrete_map={
            "HDD": "#0050EB",
            "SSD": "#ffffff",
        },
        orientation="h",
        height=350,
    )
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis=dict(range=[0, df_storage.groupby(["Armazenamento"]).size() + 1]),
        yaxis={"categoryorder": "total ascending"},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


# Gráfico Barras - Dispositivos por Situação
def situation_bar():
    df_situation = df_filter.groupby(["Situação"]).size().reset_index(name="Contagem")
    fig = px.bar(
        df_situation,
        title="Situação",
        y="Situação",
        x="Contagem",
        text="Contagem",
        labels={"Situação": "", "Contagem": ""},
        color="Situação",
        color_discrete_map={
            "Precária": "#0050EB",
            "Satisfatória": "#ffffff",
        },
        orientation="h",
        height=200,
    )
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis=dict(range=[0, max(df_situation["Contagem"]) + 1]),
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
    )
    return fig


# Dasgboard
# Cabeçaçho
st.title("Relatório de Dispositivos")
st.subheader(f"{df['Departamento'].iloc[0]}", divider="blue")

col1, col2 = st.columns([1, 2])
col1a, col1b = col1.columns(2)
col1a.markdown(
    f"""
    <div style="border: 2px solid #0050eb; border-radius: 10px; margin-bottom: 1rem; padding: 15px;">
        <h6 style="margin: 0; padding: 3.04px 0; font-size: 14px;"><b><i>Dispositivos</i></b></h6>
        <p style="margin: 0; padding: 0; font-size: 2.25rem; line-height: normal;">{num_dispositivos}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
col1b.markdown(
    f"""
    <div style="border: 2px solid #0050eb; border-radius: 10px; margin-bottom: 1rem; padding: 15px;">
        <p style="margin: 0; padding: 3.04px 0; font-size: 14px;"><b><i> </i></b></p>
        <p style="margin: 0; padding: 0; font-size: 2.25rem; line-height: normal;"></p>
    </div>
    """,
    unsafe_allow_html=True,
)
col1.plotly_chart(sector_treemap())
col1.plotly_chart(warranty_indicator())
col2.plotly_chart(age_column())

col2a, col2b = col2.columns(2)
col2a.plotly_chart(memory_bar())
col2b.plotly_chart(storage_bar())
col1.plotly_chart(situation_bar())
