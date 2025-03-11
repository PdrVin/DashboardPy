import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Tamanho Layout
st.set_page_config(
    page_title="Relatório de Dispositivos", page_icon="📊", layout="wide"
)


# Carregamento dos Dados
def load_data(file_path: str) -> pd.DataFrame:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Verificação de Tipo de Arquivo
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".csv":
        df = pd.read_csv(file_path, delimiter=",")
    elif file_extension == ".xlsx":
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado. Use .csv ou .xlsx.")

    # Tratamento dos Dados
    df["Patrimônio"] = df["Patrimônio"].astype(str)
    df["IdadeExtenso"] = df["IdadeExtenso"].astype(str)
    df["Aquisição"] = pd.to_datetime(df["Aquisição"])
    df["Expiração"] = pd.to_datetime(df["Expiração"])

    # Transformação de Dados
    df["Ano"] = df["Aquisição"].dt.year.astype(str)
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

    return df


# Segmentação de Dados no Navegador Lateral
def sidebar_filter(df: pd.DataFrame) -> pd.DataFrame:
    SETORES = ["-"] + sorted(list(df["Setor"].unique()))
    GARANTIA = ["-"] + list(df["Garantia"].unique())
    TIPOS_DISCO = ["-"] + list(df["TipoDisco"].unique())
    TIPOS_EQUIP = ["-"] + list(df["TipoEquipamento"].unique())

    select_setor = st.sidebar.radio("Setor", SETORES, index=0)
    select_garantia = st.sidebar.radio("Garantia", GARANTIA, index=0)
    select_tipo_disco = st.sidebar.radio("Tipo de Disco", TIPOS_DISCO, index=0)
    select_tipo_equip = st.sidebar.radio("Tipo de Equipamento", TIPOS_EQUIP, index=0)

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

    return df_filter


# Treemap - Dispositivos por Setor
def sector_treemap(df_filter: pd.DataFrame):
    fig = px.treemap(
        df_filter["Setor"].str.replace(" ", "<br>"),
        path=["Setor"],
        title="Dispositivos por Setor",
        color_discrete_sequence=[
            "#0B31A5",
            "#0641C8",
            "#0050EB",
            "#0078ED",
            "#008CEE",
            "#009FEF",
            "#46B3F3",
            "#8BC7F7",
        ],
    )
    fig.update_traces(root_color="#061953", textinfo="label+value", textfont_size=15)
    fig.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=235, title_font_size=20)
    return fig


# Indicador - Garantia
def warranty_indicator(df_filter: pd.DataFrame, indicator_value: int):
    range_dispositivos = [0, len(df_filter)]
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=indicator_value,
            gauge={
                "axis": {
                    "range": range_dispositivos,
                    "tickvals": range_dispositivos,
                    "tickfont": {"size": 20},
                    "ticks": "",
                },
                "bgcolor": "#061953",
                "bar": {"color": "#0050EB", "thickness": 0.7},
            },
        )
    )
    fig.update_layout(
        margin=dict(t=30, l=30, r=30, b=20),
        height=190,
        title={
            "text": "Garantia",
            "font": {"size": 20},
        },
    )
    return fig


# Grafico Colunas - Dispositivos por Ano de Aquisição
def age_column(df_filter: pd.DataFrame):
    df_age_category = (
        df_filter.groupby(["Ano", "Categoria"]).size().reset_index(name="Contagem")
    )

    fig = px.bar(
        df_age_category,
        title="Computadores Adquiridos",
        x="Ano",
        y="Contagem",
        text="Contagem",
        color="Categoria",
        color_discrete_map={
            "Ótimo": "#ffffff",
            "Regular": "#66c5f5",
            "Antigo": "#0078ED",
        },
        height=350,
    )
    fig.update_traces(textangle=0)
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        title_font_size=20,
        font_size=14,
        xaxis=dict(
            type="category",
            title="",
            tickfont_size=14,
        ),
        yaxis=dict(
            range=[0, max(df_filter.groupby("Ano").size()) + 0.2],
            title="",
            tickfont_size=14,
            gridcolor="gray",
            griddash="dot",
        ),
        legend=dict(title_font_size=16, font_size=14),
    )
    return fig


# Gráfico Barras - Dispositivos por Memória e Tipo
def memory_bar(df_filter: pd.DataFrame):
    df_memory = (
        df_filter.groupby(["Memória", "TipoMemória"])
        .size()
        .reset_index(name="Contagem")
    )
    fig = px.bar(
        df_memory,
        title="Memória",
        x="Contagem",
        y="Memória",
        text="Contagem",
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
        title_font_size=20,
        font_size=14,
        xaxis=dict(
            range=[0, df_filter.groupby(["Memória"]).size() + 1],
            title="",
            tickfont_size=14,
            showgrid=True,
            gridwidth=1,
            gridcolor="gray",
            griddash="dot",
        ),
        yaxis=dict(
            categoryorder="total ascending",
            title="",
            tickfont_size=14,
        ),
        legend=dict(
            font_size=14,
            title_text=None,
            orientation="h",
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


# Gráfico Barras - Dispositivos por Memória e Tipo
def storage_bar(df_filter: pd.DataFrame):
    df_storage = (
        df_filter.groupby(["Armazenamento", "TipoDisco"])
        .size()
        .reset_index(name="Contagem")
    )
    fig = px.bar(
        df_storage,
        title="Armazenamento",
        x="Contagem",
        y="Armazenamento",
        text="Contagem",
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
        title_font_size=20,
        font_size=14,
        xaxis=dict(
            range=[0, max(df_filter.groupby(["Armazenamento"]).size()) + 1],
            title="",
            tickfont_size=14,
            showgrid=True,
            gridwidth=1,
            gridcolor="gray",
            griddash="dot",
        ),
        yaxis=dict(
            categoryorder="total ascending",
            title="",
            tickfont_size=14,
        ),
        legend=dict(
            font_size=14,
            title_text=None,
            orientation="h",
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


# Gráfico Barras - Dispositivos por Situação
def situation_bar(df_filter: pd.DataFrame):
    df_situation = df_filter.groupby(["Situação"]).size().reset_index(name="Contagem")
    fig = px.bar(
        df_situation,
        title="Situação",
        x="Contagem",
        y="Situação",
        text="Contagem",
        color="Situação",
        color_discrete_map={
            "Precária": "#0050EB",
            "Satisfatória": "#ffffff",
        },
        orientation="h",
        height=190,
    )
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        title_font_size=20,
        font_size=14,
        xaxis=dict(
            range=[0, max(df_situation["Contagem"]) + 2],
            title="",
            tickfont_size=14,
            showgrid=True,
            gridwidth=1,
            gridcolor="gray",
            griddash="dot",
        ),
        yaxis=dict(
            categoryorder="total ascending",
            title="",
            tickfont_size=14,
        ),
        showlegend=False,
    )
    return fig


# Card de Valores
def mark_card(object, title: str, value: int):
    object.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center;
            border: 2px solid #0050eb; border-radius: 10px; margin-bottom: 1rem; padding: 10px;">
            <p style="margin: 0; padding: 0; font-size: 20px; font-weight: 800;">{title}</p>
            <p style="margin: 0; padding: 0; font-size: 2.5rem; line-height: normal;">{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Dados
df = load_data("data/DadosPlanilha.csv")
df_filter = sidebar_filter(df)
num_dispositivos = len(df_filter["ServiceTag"])
count_garantia_ativa = len(df_filter[df_filter["Garantia"] == "Ativa"])

# Dashboard
st.title("Relatório de Dispositivos")
st.subheader(f"{df['Departamento'].iloc[0]}", divider="blue")

col1, col2 = st.columns([1, 2])
mark_card(col1, "Dispositivos", num_dispositivos)
col1.plotly_chart(sector_treemap(df_filter))
col1.plotly_chart(warranty_indicator(df_filter, count_garantia_ativa))
col2.plotly_chart(age_column(df_filter))

col2a, col2b = col2.columns(2)
col2a.plotly_chart(memory_bar(df_filter))
col2b.plotly_chart(storage_bar(df_filter))
col1.plotly_chart(situation_bar(df_filter))
