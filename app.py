import streamlit as st

from src.config import EMPRESA_ANALISE
from src.data_loader import carregar_dados
from src.metrics import ChurnAnalyzer
from src.ui import brand_showcase, configurar_pagina, insight_panel, metricas, page_header, section_title, sidebar_usuario, tabela_estatica

configurar_pagina("Início", "🏠")
sidebar_usuario()

df = carregar_dados()
analyzer = ChurnAnalyzer(df)

brand_showcase()

page_header(
    "Painel executivo de cancelamentos Telco",
    "Relatório interativo para entender cancelamentos, receita, perfil da carteira e prioridades de retenção em uma base de telecomunicações.",
    EMPRESA_ANALISE,
)

metricas(
    [
        ("Clientes na base", f"{analyzer.total_clientes:,}".replace(",", "."), "Total de registros analisados."),
        ("Cancelamentos", f"{analyzer.total_cancelamentos:,}".replace(",", "."), "Clientes que cancelaram no período."),
        ("Taxa de cancelamento", f"{analyzer.taxa_churn:.2%}".replace(".", ","), "Percentual de clientes cancelados."),
        ("Receita total", f"US$ {analyzer.receita_total:,.0f}".replace(",", "."), "Receita total observada na base."),
    ]
)

metricas(
    [
        (
            "Receita mensal estimada",
            f"US$ {analyzer.receita_mensal_estimativa:,.0f}".replace(",", "."),
            "Soma das mensalidades atuais.",
        ),
        (
            "Mensalidade média",
            f"US$ {analyzer.mensalidade_media:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Ticket mensal médio por cliente.",
        ),
        ("Satisfação média", f"{analyzer.satisfacao_media:.2f}".replace(".", ","), "Nota média de satisfação."),
        ("Pontuação de cancelamento média", f"{analyzer.score_churn_medio:.1f}".replace(".", ","), "Risco médio previsto na base."),
    ]
)

st.divider()

insight_panel(
    """
    <strong>Objetivo do relatório:</strong> responder por que os clientes cancelam, quais segmentos concentram risco e quais ações podem proteger receita. Além do cancelamento, o painel cobre carteira, contratos, serviços, satisfação, geografia, marketing, valor de vida do cliente e tempo de permanência.
    """
)

section_title("Navegação do relatório", "Cada página aprofunda uma parte da análise e mantém tabelas estáticas quando o enunciado exige.")
tabela_estatica(
    {
        "Página": [
            "Tabelas",
            "Gráficos",
            "Análises da Empresa",
            "Insights e Relatório",
            "Enviar por E-mail",
            "Download",
        ],
        "O que entrega": [
            "Tabelas estáticas com filtros, cancelamentos, finanças, produtos, satisfação, geografia e clientes prioritários.",
            "Gráficos estáticos e interativos sobre cancelamentos e indicadores empresariais.",
            "Página dedicada às análises além dos cancelamentos, com leitura gerencial por área.",
            "Relatório geral com recomendações baseadas nos dados.",
            "Envio de gráfico estático ou relatório escrito por e-mail.",
            "Download do relatório em arquivo .txt.",
        ],
    }
)

st.info(
    "Use a barra lateral para digitar seu nome. Nas demais páginas, o sistema exibirá a sessão personalizada no início."
)
