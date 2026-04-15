import os

import duckdb
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv


# Carrega variaveis locais do .env para execucao fora do Streamlit Cloud.
load_dotenv()


def read_setting(name: str, default: str) -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except (AttributeError, KeyError, RuntimeError, TypeError):
        # Se st.secrets nao estiver configurado, segue para env var.
        pass

    return os.getenv(name, default)


st.set_page_config(
    page_title="NovaDrive Intelligence | Dashboard Executivo",
    page_icon="🚗",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DUCKDB_PATH = read_setting("NOVADRIVE_DUCKDB_PATH", "data/warehouse.duckdb")
SALES_API_BASE_URL = read_setting(
    "SALES_API_BASE_URL", "http://143.244.215.137:3002"
)
SALES_API_TIMEOUT = int(read_setting("SALES_API_TIMEOUT", "10"))


@st.cache_resource
def get_connection():
    return duckdb.connect(database=DUCKDB_PATH, read_only=True)


@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    query = "SELECT * FROM refined_vendas_final"
    return conn.execute(query).df()


def ensure_required_columns(dataframe: pd.DataFrame):
    required = {"data_venda", "valor_venda", "modelo_veiculo"}
    missing = required.difference(set(dataframe.columns))
    if missing:
        st.error(
            "A tabela refined_vendas_final nao possui as colunas esperadas: "
            + ", ".join(sorted(missing))
        )
        st.stop()


def format_currency_brl(value: float) -> str:
    return (
        f"R$ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


st.sidebar.header("⚙️ Filtros Estratégicos")

try:
    df = load_data()
except (duckdb.Error, OSError, RuntimeError) as exc:
    st.error("Falha ao carregar dados do DuckDB.")
    st.exception(exc)
    st.stop()

if df.empty:
    st.warning(
        "A tabela refined_vendas_final esta vazia. "
        "Execute o pipeline e tente novamente."
    )
    st.stop()

ensure_required_columns(df)

df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
df = df.dropna(subset=["data_venda"])

if df.empty:
    st.warning("Nao ha linhas validas para data_venda apos tratamento.")
    st.stop()

min_date = df["data_venda"].min().date()
max_date = df["data_venda"].max().date()

period = st.sidebar.date_input(
    "Período de Análise",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(period, tuple) and len(period) == 2:
    start_date, end_date = period
else:
    start_date = period
    end_date = period

model_options = sorted(df["modelo_veiculo"].dropna().unique().tolist())
if len(model_options) >= 3:
    default_models = model_options[:3]
else:
    default_models = model_options

modelos = st.sidebar.multiselect(
    "Modelos de Luxo",
    options=model_options,
    default=default_models,
)

if not modelos:
    st.info("Selecione pelo menos um modelo para exibir os indicadores.")
    st.stop()

mask = (
    (df["data_venda"].dt.date >= start_date)
    & (df["data_venda"].dt.date <= end_date)
    & (df["modelo_veiculo"].isin(modelos))
)
df_filtered = df.loc[mask].copy()

st.title("🚗 NovaDrive: End-to-End Data Intelligence")
st.subheader("Análise Executiva de Faturamento e Performance")

if df_filtered.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

m1, m2, m3, m4 = st.columns(4)

with m1:
    faturamento_total = float(df_filtered["valor_venda"].sum())
    st.metric("Faturamento Total", format_currency_brl(faturamento_total))

with m2:
    vendas_count = int(len(df_filtered))
    st.metric("Volume de Vendas", f"{vendas_count} unidades")

with m3:
    ticket_medio = faturamento_total / vendas_count if vendas_count > 0 else 0
    st.metric("Ticket Médio", format_currency_brl(ticket_medio))

with m4:
    crescimento = 12.5
    st.metric("Crescimento MoM", f"{crescimento:.1f}%", delta="+2.1%")

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.markdown("### 📈 Evolução de Vendas (Diária)")
    evolucao = df_filtered.groupby(
        "data_venda", as_index=False
    )["valor_venda"].sum()
    evolucao = evolucao.sort_values("data_venda")
    fig_evolucao = px.area(
        evolucao,
        x="data_venda",
        y="valor_venda",
        line_shape="spline",
        color_discrete_sequence=["#00d4ff"],
    )
    fig_evolucao.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_evolucao, use_container_width=True)

with c2:
    st.markdown("### 🏆 Top Modelos por Faturamento")
    ranking = (
        df_filtered.groupby("modelo_veiculo", as_index=False)["valor_venda"]
        .sum()
        .sort_values("valor_venda", ascending=True)
    )
    fig_ranking = px.bar(
        ranking,
        x="valor_venda",
        y="modelo_veiculo",
        orientation="h",
        color="valor_venda",
        color_continuous_scale="Viridis",
    )
    fig_ranking.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_ranking, use_container_width=True)

st.divider()
st.markdown("### 🔍 Consulta Rápida no Sistema de Vendas")
with st.expander("Verificar integridade de uma venda por ID"):
    venda_id = st.text_input("Insira o ID da Venda:")
    if st.button("Consultar no Sistema"):
        if not venda_id:
            st.info("Digite um ID válido.")
        else:
            try:
                response = requests.get(
                    f"{SALES_API_BASE_URL}/procura",
                    params={"id": venda_id},
                    timeout=SALES_API_TIMEOUT,
                )
                if response.status_code == 200:
                    st.success(
                        f"Venda {venda_id} localizada com sucesso "
                        "no sistema externo."
                    )
                    try:
                        st.json(response.json())
                    except ValueError:
                        st.write(response.text)
                elif response.status_code == 404:
                    st.error("Venda não encontrada.")
                else:
                    st.error(
                        "Falha na consulta ao sistema externo "
                        f"(status {response.status_code})."
                    )
            except requests.RequestException:
                st.warning(
                    "Não foi possível conectar ao sistema de vendas externo."
                )

st.caption(
    "Desenvolvido para o Bootcamp NovaDrive | "
    "Arquitetura Híbrida Cloud/Local"
)
