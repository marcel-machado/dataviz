import streamlit as st

from src.data_loader import carregar_dados
from src.metrics import ChurnAnalyzer
from src.ui import configurar_pagina, insight_panel, metricas, page_header, saudacao, section_title, sidebar_usuario, tabela_estatica

configurar_pagina("Análises da Empresa", "🏢")
sidebar_usuario()
saudacao()

page_header(
    "Análises adicionais para a empresa",
    "Leitura gerencial da carteira além do cancelamento: receita, contratos, serviços, satisfação, geografia, marketing e clientes prioritários.",
)

df = carregar_dados()
analyzer = ChurnAnalyzer(df)

insight_panel(
    """
    Além de explicar os cancelamentos, a empresa precisa entender <strong>onde está a receita</strong>, <strong>quais segmentos são mais fortes</strong>, <strong>quais serviços têm maior adesão</strong>, <strong>quais clientes merecem prioridade</strong> e <strong>onde existem oportunidades comerciais</strong>.
    """
)

metricas(
    [
        ("Receita total", f"US$ {analyzer.receita_total:,.0f}".replace(",", "."), "Receita histórica observada."),
        (
            "Receita mensal estimada",
            f"US$ {analyzer.receita_mensal_estimativa:,.0f}".replace(",", "."),
            "Receita recorrente estimada.",
        ),
        (
            "Mensalidade média",
            f"US$ {analyzer.mensalidade_media:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Ticket mensal médio.",
        ),
        ("Satisfação média", f"{analyzer.satisfacao_media:.2f}".replace(".", ","), "Satisfação média da base."),
    ]
)

st.divider()

section_title("Mapa das análises adicionais", "Perguntas de negócio cobertas pelas tabelas desta página.")
tabela_estatica(analyzer.resumo_analises_adicionais())

aba_carteira, aba_financeiro, aba_produtos, aba_satisfacao, aba_geo_mkt, aba_prioridade = st.tabs(
    [
        "Carteira e perfil",
        "Financeiro e contratos",
        "Produtos e serviços",
        "Satisfação e permanência",
        "Geografia e marketing",
        "Valor de vida e prioridade",
    ]
)

with aba_carteira:
    insight_panel(
        """
        <strong>Objetivo:</strong> entender a composição da carteira. A análise mostra clientes novos, permanecidos, desligados e perfis demográficos com maior peso.
        """
    )
    section_title("Status da carteira")
    tabela_estatica(analyzer.status_summary())

    section_title("Perfil demográfico")
    tabela_estatica(analyzer.perfil_demografico())

    section_title("Faixas etárias")
    tabela_estatica(analyzer.age_summary())

with aba_financeiro:
    insight_panel(
        """
        <strong>Objetivo:</strong> avaliar o negócio pelo ponto de vista financeiro: receita total, receita mensal estimada, ticket médio, reembolsos, cobranças extras e valor de vida do cliente.
        """
    )
    section_title("Resumo financeiro")
    tabela_estatica(analyzer.resumo_financeiro())

    section_title("Receita por contrato")
    tabela_estatica(analyzer.receita_por_segmento("Contract"))

    section_title("Receita por método de pagamento")
    tabela_estatica(analyzer.receita_por_segmento("Payment Method"))

with aba_produtos:
    insight_panel(
        """
        <strong>Objetivo:</strong> identificar quais produtos e serviços têm maior adesão e quais estão associados a maior ou menor risco. Isso apoia retenção, venda cruzada e reposicionamento de ofertas.
        """
    )
    section_title("Aderência aos serviços")
    tabela_estatica(analyzer.servicos_adesao())

    section_title("Receita por tipo de internet")
    tabela_estatica(analyzer.receita_por_segmento("Internet Type"))

    section_title("Receita por oferta")
    tabela_estatica(analyzer.receita_por_segmento("Offer"))

with aba_satisfacao:
    insight_panel(
        """
        <strong>Objetivo:</strong> avaliar experiência do cliente. A satisfação ajuda a explicar cancelamentos e revela oportunidades de melhoria operacional.
        """
    )
    section_title("Satisfação e cancelamento")
    tabela_estatica(analyzer.satisfacao_summary())

    section_title("Tempo de permanência")
    tabela_estatica(analyzer.tenure_summary())

    section_title("Médias por cancelamento")
    tabela_estatica(analyzer.resumo_numerico_por_churn())

with aba_geo_mkt:
    insight_panel(
        """
        <strong>Objetivo:</strong> identificar regiões prioritárias e avaliar se indicações e ofertas atraem clientes mais estáveis ou mais rentáveis.
        """
    )
    section_title("Top cidades por clientes")
    tabela_estatica(analyzer.top_cidades(limite=15, min_clientes=20, ordenar_por="Clientes"))

    section_title("Top cidades por receita mensal")
    tabela_estatica(analyzer.top_cidades(limite=15, min_clientes=20, ordenar_por="Receita mensal estimada"))

    section_title("Indicações")
    tabela_estatica(analyzer.referral_summary())

    section_title("Ofertas de marketing")
    tabela_estatica(analyzer.receita_por_segmento("Offer"))

with aba_prioridade:
    insight_panel(
        """
        <strong>Objetivo:</strong> sair da análise descritiva e apontar uma fila de ação. Clientes ativos com alta pontuação de cancelamento, alto valor de vida, mensalidade elevada ou baixa satisfação devem ser tratados como prioridade comercial.
        """
    )
    section_title("Clientes ativos prioritários para retenção")
    tabela_estatica(analyzer.clientes_prioritarios(25))

    section_title("Fatores com maior taxa de cancelamento")
    tabela_estatica(analyzer.principais_fatores())
