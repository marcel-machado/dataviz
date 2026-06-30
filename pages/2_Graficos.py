import matplotlib.pyplot as plt
import streamlit as st

from src.charts import (
    BUSINESS_INTERACTIVE_CHARTS,
    BUSINESS_STATIC_CHARTS,
    CHURN_INTERACTIVE_CHARTS,
    CHURN_STATIC_CHARTS,
    GraficosChurn,
)
from src.data_loader import carregar_dados
from src.ui import configurar_pagina, insight_panel, page_header, saudacao, section_title, sidebar_usuario

configurar_pagina("Gráficos", "📊")
sidebar_usuario()
saudacao()

page_header(
    "Visualizações de cancelamento e negócio",
    "Gráficos estáticos para relatório/e-mail e gráficos interativos para explorar risco, receita, serviços e geografia.",
)

df = carregar_dados()
graficos = GraficosChurn(df)

tab_churn_static, tab_business_static, tab_churn_inter, tab_business_inter = st.tabs(
    [
        "Cancelamento - estáticos",
        "Empresa - estáticos",
        "Cancelamento - interativos",
        "Empresa - interativos",
    ]
)

with tab_churn_static:
    section_title("Gráfico estático de cancelamento", "Visual pronto para apresentação e envio por e-mail em PNG.")
    escolha = st.selectbox("Escolha o gráfico de cancelamento", list(CHURN_STATIC_CHARTS.keys()))
    metodo = getattr(graficos, CHURN_STATIC_CHARTS[escolha])
    fig = metodo()
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    insight_panel("<strong>Uso recomendado:</strong> escolha estes gráficos quando precisar de uma imagem fechada para anexar ao e-mail ou inserir em apresentação.")

with tab_business_static:
    section_title("Gráfico estático de análise empresarial", "Visualizações de receita, serviços, satisfação, perfil e permanência.")
    escolha = st.selectbox("Escolha o gráfico empresarial", list(BUSINESS_STATIC_CHARTS.keys()))
    metodo = getattr(graficos, BUSINESS_STATIC_CHARTS[escolha])
    fig = metodo()
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    insight_panel("<strong>Leitura executiva:</strong> estes gráficos ajudam a separar volume de clientes, risco de cancelamento e potencial financeiro.")

with tab_churn_inter:
    section_title("Gráfico interativo de cancelamento", "Use hover, zoom e seleção para investigar segmentos críticos.")
    escolha_interativa = st.selectbox("Escolha o gráfico interativo de cancelamento", list(CHURN_INTERACTIVE_CHARTS.keys()))
    metodo_interativo = getattr(graficos, CHURN_INTERACTIVE_CHARTS[escolha_interativa])
    fig_interativa = metodo_interativo()
    st.plotly_chart(fig_interativa, width="stretch")
    insight_panel("<strong>Exploração:</strong> passe o mouse sobre os pontos ou barras para ver clientes, cancelamentos, receita e indicadores do segmento.")

with tab_business_inter:
    section_title("Gráfico interativo de análise empresarial", "Exploração de receita, serviços, geografia e permanência.")
    escolha_interativa = st.selectbox("Escolha o gráfico interativo empresarial", list(BUSINESS_INTERACTIVE_CHARTS.keys()))
    metodo_interativo = getattr(graficos, BUSINESS_INTERACTIVE_CHARTS[escolha_interativa])
    fig_interativa = metodo_interativo()
    st.plotly_chart(fig_interativa, width="stretch")
    insight_panel("<strong>Decisão:</strong> use esta aba para encontrar onde agir primeiro: cidade, serviço, contrato, perfil ou estágio de relacionamento.")
