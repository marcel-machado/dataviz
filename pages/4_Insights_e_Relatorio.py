import streamlit as st

from src.data_loader import carregar_dados
from src.metrics import ChurnAnalyzer
from src.report import gerar_relatorio_texto
from src.translations import traduzir_dataframe
from src.ui import configurar_pagina, insight_panel, metricas, page_header, saudacao, section_title, sidebar_usuario, tabela_estatica

configurar_pagina("Insights e Relatório", "🧠")
sidebar_usuario()
saudacao()

page_header(
    "Insights gerais e recomendações",
    "Síntese executiva da análise: fatores críticos de cancelamento, leituras adicionais de negócio e relatório textual pronto para entrega.",
)

df = carregar_dados()
analyzer = ChurnAnalyzer(df)

metricas(
    [
        ("Clientes", f"{analyzer.total_clientes:,}".replace(",", "."), "Total da base."),
        ("Cancelaram", f"{analyzer.total_cancelamentos:,}".replace(",", "."), "Clientes que saíram."),
        ("Cancelamento geral", f"{analyzer.taxa_churn:.2%}".replace(".", ","), "Taxa geral de cancelamento."),
        (
            "Receita mensal perdida",
            f"US$ {analyzer.receita_mensal_perdida_churn:,.0f}".replace(",", "."),
            "Mensalidade associada aos clientes cancelados.",
        ),
    ]
)

st.divider()

section_title("Fatores com maior taxa de cancelamento")
tabela_estatica(traduzir_dataframe(analyzer.principais_fatores()))

section_title("Outras análises incorporadas ao relatório")
tabela_estatica(analyzer.resumo_analises_adicionais())

section_title("Leitura executiva")
insight_panel(
    """
    A base aponta que o cancelamento está relacionado a uma combinação de <strong>experiência</strong>, <strong>contrato</strong>, <strong>concorrência</strong>, <strong>percepção de valor</strong> e <strong>momento do relacionamento</strong>. As análises financeiras, geográficas, de produto e de marketing indicam onde a empresa pode agir para melhorar retenção, receita e fidelização.
    """
)

section_title("Relatório escrito")
relatorio = gerar_relatorio_texto(df, st.session_state.get("nome_usuario", ""))
st.text_area("Relatório executivo gerado automaticamente", value=relatorio, height=750)
