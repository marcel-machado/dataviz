import streamlit as st

from src.data_loader import carregar_dados, filtrar_dados
from src.metrics import ChurnAnalyzer
from src.translations import traduzir_valor
from src.ui import configurar_pagina, metricas, page_header, saudacao, section_title, sidebar_usuario, tabela_estatica

configurar_pagina("Tabelas", "📋")
sidebar_usuario()
saudacao()

page_header(
    "Tabelas estáticas da base",
    "Resumo tabular dos indicadores, filtros de segmentação e listas de clientes prioritários para retenção.",
)

df = carregar_dados()

with st.expander("Filtros", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    status = col1.multiselect(
        "Status do cliente",
        sorted(df["Customer Status"].dropna().unique()),
        default=sorted(df["Customer Status"].dropna().unique()),
        format_func=traduzir_valor,
    )
    contrato = col2.multiselect(
        "Contrato",
        sorted(df["Contract"].dropna().unique()),
        default=sorted(df["Contract"].dropna().unique()),
        format_func=traduzir_valor,
    )
    internet = col3.multiselect(
        "Tipo de internet",
        sorted(df["Internet Type"].dropna().unique()),
        default=sorted(df["Internet Type"].dropna().unique()),
        format_func=traduzir_valor,
    )
    churn_label = col4.multiselect(
        "Cancelou?",
        sorted(df["Churn Label"].dropna().unique()),
        default=sorted(df["Churn Label"].dropna().unique()),
        format_func=traduzir_valor,
    )

filtrado = filtrar_dados(df, status=status, contrato=contrato, internet=internet, churn_label=churn_label)
analyzer = ChurnAnalyzer(filtrado)

metricas(
    [
        ("Clientes filtrados", f"{len(filtrado):,}".replace(",", "."), "Quantidade após filtros."),
        ("Cancelamentos filtrados", f"{analyzer.total_cancelamentos:,}".replace(",", "."), "Cancelamentos no recorte atual."),
        ("Taxa de cancelamento filtrada", f"{analyzer.taxa_churn:.2%}".replace(".", ","), "Cancelamento do recorte selecionado."),
        ("Receita filtrada", f"US$ {analyzer.receita_total:,.0f}".replace(",", "."), "Receita total do recorte."),
    ]
)

st.divider()

tab_resumo, tab_churn, tab_negocio, tab_marketing_geo, tab_amostra = st.tabs(
    ["Resumo", "Cancelamento", "Negócio", "Marketing, geografia e risco", "Amostra"]
)

with tab_resumo:
    section_title("Resumo executivo")
    tabela_estatica(analyzer.tabela_executiva())

    section_title("Status da carteira de clientes")
    tabela_estatica(analyzer.status_summary())

    section_title("Médias dos principais indicadores por cancelamento")
    tabela_estatica(analyzer.resumo_numerico_por_churn())

with tab_churn:
    section_title("Taxa de cancelamento por contrato")
    tabela_estatica(analyzer.churn_rate_by("Contract"))

    section_title("Taxa de cancelamento por tipo de internet")
    tabela_estatica(analyzer.churn_rate_by("Internet Type"))

    section_title("Taxa de cancelamento por satisfação")
    tabela_estatica(analyzer.satisfacao_summary())

    section_title("Categorias de cancelamento")
    tabela_estatica(analyzer.churn_categories())

    section_title("Top motivos de cancelamento")
    tabela_estatica(analyzer.top_churn_reasons(12))

with tab_negocio:
    section_title("Resumo financeiro")
    tabela_estatica(analyzer.resumo_financeiro())

    section_title("Receita por tipo de contrato")
    tabela_estatica(analyzer.receita_por_segmento("Contract"))

    section_title("Receita por tipo de internet")
    tabela_estatica(analyzer.receita_por_segmento("Internet Type"))

    section_title("Aderência aos produtos e serviços")
    tabela_estatica(analyzer.servicos_adesao())

    section_title("Tempo de permanência")
    tabela_estatica(analyzer.tenure_summary())

    section_title("Perfil demográfico")
    tabela_estatica(analyzer.perfil_demografico())

with tab_marketing_geo:
    section_title("Indicações de clientes")
    tabela_estatica(analyzer.referral_summary())

    section_title("Ofertas de marketing")
    tabela_estatica(analyzer.receita_por_segmento("Offer"))

    section_title("Top cidades por quantidade de clientes")
    tabela_estatica(analyzer.top_cidades(limite=15, min_clientes=20, ordenar_por="Clientes"))

    section_title("Cidades com maior taxa de cancelamento entre cidades com base relevante")
    tabela_estatica(analyzer.top_cidades(limite=15, min_clientes=20, ordenar_por="Taxa de churn (%)"))

    section_title("Clientes ativos prioritários para retenção")
    st.caption("Clientes ainda não cancelados que combinam maior pontuação de cancelamento, valor de vida, mensalidade e/ou baixa satisfação.")
    tabela_estatica(analyzer.clientes_prioritarios(20))

with tab_amostra:
    section_title("Amostra dos registros")
    qtd_linhas = st.slider("Quantidade de linhas exibidas", min_value=5, max_value=100, value=20, step=5)
    colunas_padrao = [
        "Customer ID",
        "Gender",
        "Age",
        "Contract",
        "Internet Type",
        "Monthly Charge",
        "Total Revenue",
        "Satisfaction Score",
        "Customer Status",
        "Churn Label",
        "Churn Score",
        "CLTV",
        "Churn Category",
        "Churn Reason",
    ]
    colunas_existentes = [c for c in colunas_padrao if c in filtrado.columns]
    tabela_estatica(filtrado[colunas_existentes].head(qtd_linhas))
