import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="📊 Dashboard de Salários - Área de Dados",
    page_icon="💼",
    layout="wide"
)

# =========================
# CARREGAMENTO DOS DADOS
# =========================
@st.cache_data
def carregar_dados():
    return pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

df = carregar_dados()

# =========================
# SIDEBAR - FILTROS
# =========================
st.sidebar.header("🔍 Filtros")

filtros = {
    "Ano": sorted(df['ano'].unique()),
    "Senioridade": sorted(df['senioridade'].unique()),
    "Tipo de Contrato": sorted(df['contrato'].unique()),
    "Tamanho da Empresa": sorted(df['tamanho_empresa'].unique())
}

anos_selecionados = st.sidebar.multiselect("Ano", filtros["Ano"], default=filtros["Ano"])
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", filtros["Senioridade"], default=filtros["Senioridade"])
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", filtros["Tipo de Contrato"], default=filtros["Tipo de Contrato"])
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", filtros["Tamanho da Empresa"], default=filtros["Tamanho da Empresa"])

# =========================
# FILTRAGEM DO DATAFRAME
# =========================
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# =========================
# CABEÇALHO
# =========================
st.title("💼 Dashboard de Salários na Área de Dados")
st.markdown("Use os filtros ao lado para explorar **tendências salariais** e **informações de mercado** de forma interativa.")

st.markdown("---")

# =========================
# MÉTRICAS
# =========================
st.subheader("📌 Indicadores Gerais")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio = salario_maximo = total_registros = 0
    cargo_mais_frequente = "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("💵 Salário médio", f"${salario_medio:,.0f}")
col2.metric("📈 Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("📊 Total registros", f"{total_registros:,}")
col4.metric("👔 Cargo mais comum", cargo_mais_frequente)

st.markdown("---")

# =========================
# GRÁFICOS
# =========================
st.subheader("📊 Análises Visuais")

template_visual = "plotly_white"

col_graf1, col_graf2 = st.columns(2)

# Top cargos por salário
if not df_filtrado.empty:
    top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
    fig_cargos = px.bar(
        top_cargos, x='usd', y='cargo',
        orientation='h',
        title="Top 10 cargos por salário médio",
        labels={'usd': 'Média Salarial Anual (USD)', 'cargo': ''},
        template=template_visual,
        color='usd',
        color_continuous_scale='Blues'
    )
    col_graf1.plotly_chart(fig_cargos, use_container_width=True)

# Histograma salários
    fig_hist = px.histogram(
        df_filtrado, x='usd',
        nbins=30,
        title="Distribuição de Salários Anuais",
        labels={'usd': 'Faixa Salarial (USD)', 'count': 'Quantidade'},
        template=template_visual,
        color_discrete_sequence=['#00b4d8']
    )
    col_graf2.plotly_chart(fig_hist, use_container_width=True)
else:
    col_graf1.warning("Nenhum dado para exibir.")
    col_graf2.warning("Nenhum dado para exibir.")

# Gráficos extras
col_graf3, col_graf4 = st.columns(2)

# Tipos de trabalho
if not df_filtrado.empty:
    remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
    remoto_contagem.columns = ['Tipo de Trabalho', 'Quantidade']
    fig_remoto = px.pie(
        remoto_contagem, names='Tipo de Trabalho', values='Quantidade',
        title='Proporção dos Tipos de Trabalho',
        hole=0.4,
        template=template_visual
    )
    fig_remoto.update_traces(textinfo='percent+label')
    col_graf3.plotly_chart(fig_remoto, use_container_width=True)

# Salário de Data Scientist por país
    df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
    if not df_ds.empty:
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        fig_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='YlGnBu',
            title='Salário Médio de Data Scientist por País',
            labels={'usd': 'Salário Médio (USD)', 'residencia_iso3': 'País'},
            template=template_visual
        )
        col_graf4.plotly_chart(fig_paises, use_container_width=True)
    else:
        col_graf4.info("Sem dados para Cientista de Dados.")
else:
    col_graf3.warning("Nenhum dado para exibir.")
    col_graf4.warning("Nenhum dado para exibir.")

st.markdown("---")

# =========================
# TABELA DETALHADA
# =========================
st.subheader("📄 Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)
