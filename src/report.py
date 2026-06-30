from __future__ import annotations

from datetime import datetime
import pandas as pd

from .config import EMPRESA_ANALISE
from .metrics import ChurnAnalyzer
from .translations import traduzir_coluna, traduzir_valor


def _moeda(valor: float) -> str:
    return f"US$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(valor: float) -> str:
    return f"{float(valor):.2%}".replace(".", ",")


def _num(valor: float, casas: int = 2) -> str:
    return f"{float(valor):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _inteiro(valor: int | float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def _primeira_linha(tabela: pd.DataFrame) -> pd.Series | None:
    if tabela is None or tabela.empty:
        return None
    return tabela.iloc[0]


def gerar_relatorio_texto(df: pd.DataFrame, nome_usuario: str = "") -> str:
    analyzer = ChurnAnalyzer(df)

    motivos = analyzer.top_churn_reasons(5)
    categorias = analyzer.churn_categories()
    fatores = analyzer.principais_fatores().head(8)
    contrato_churn = analyzer.churn_rate_by("Contract")
    internet_churn = analyzer.churn_rate_by("Internet Type")
    satisfacao = analyzer.satisfacao_summary()
    status = analyzer.status_summary()
    contrato_receita = analyzer.receita_por_segmento("Contract")
    internet_receita = analyzer.receita_por_segmento("Internet Type")
    servicos = analyzer.servicos_adesao()
    permanencia = analyzer.tenure_summary()
    indicacoes = analyzer.referral_summary()
    ofertas = analyzer.receita_por_segmento("Offer")
    cidades_clientes = analyzer.top_cidades(limite=5, min_clientes=20, ordenar_por="Clientes")
    cidades_churn = analyzer.top_cidades(limite=5, min_clientes=20, ordenar_por="Taxa de churn (%)")
    prioritarios = analyzer.clientes_prioritarios(25)

    top_motivo = _primeira_linha(motivos)
    top_categoria = _primeira_linha(categorias)
    top_contrato_churn = _primeira_linha(contrato_churn)
    top_internet_churn = _primeira_linha(internet_churn)
    top_satisfacao = _primeira_linha(satisfacao.sort_values("Taxa de churn (%)", ascending=False) if not satisfacao.empty else satisfacao)
    top_contrato_receita = _primeira_linha(contrato_receita)
    top_internet_receita = _primeira_linha(internet_receita)
    top_servico = _primeira_linha(servicos)
    top_permanencia_churn = _primeira_linha(permanencia.sort_values("Taxa de churn (%)", ascending=False) if not permanencia.empty else permanencia)
    top_indicacao = _primeira_linha(indicacoes.sort_values("Taxa de churn (%)", ascending=True) if not indicacoes.empty else indicacoes)
    top_oferta_receita = _primeira_linha(ofertas)
    top_cidade_clientes = _primeira_linha(cidades_clientes)
    top_cidade_churn = _primeira_linha(cidades_churn)

    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    saudacao = f"Relatório preparado para: {nome_usuario}\n" if nome_usuario else ""

    linhas: list[str] = [
        "RELATÓRIO EXECUTIVO - ANÁLISE TELCO DE CANCELAMENTOS",
        f"Empresa de análise: {EMPRESA_ANALISE}",
        saudacao.strip(),
        f"Gerado em: {data}",
        "",
        "1. RESUMO GERAL",
        f"A base possui {_inteiro(analyzer.total_clientes)} clientes.",
        f"Foram identificados {_inteiro(analyzer.total_cancelamentos)} cancelamentos, com taxa geral de cancelamento de {_pct(analyzer.taxa_churn)}.",
        f"A receita total observada é de {_moeda(analyzer.receita_total)} e a receita mensal recorrente estimada é de {_moeda(analyzer.receita_mensal_estimativa)}.",
        f"A receita mensal associada aos clientes que cancelaram é de {_moeda(analyzer.receita_mensal_perdida_churn)}, indicando perda recorrente relevante para a empresa.",
        f"A mensalidade média geral é de {_moeda(analyzer.mensalidade_media)}, a satisfação média é {_num(analyzer.satisfacao_media)} e a pontuação de cancelamento média é {_num(analyzer.score_churn_medio)}.",
        "",
        "2. CHURN: MOTIVOS, CATEGORIAS E FATORES CRÍTICOS",
    ]

    if top_categoria is not None:
        linhas.append(
            f"A categoria de cancelamento mais frequente é '{traduzir_valor(top_categoria['Churn Category'])}', com {_inteiro(top_categoria['Cancelamentos'])} ocorrências ({_num(top_categoria['Percentual (%)'])}% dos cancelamentos)."
        )
    if top_motivo is not None:
        linhas.append(
            f"O motivo específico mais recorrente é '{traduzir_valor(top_motivo['Churn Reason'])}', com {_inteiro(top_motivo['Cancelamentos'])} clientes."
        )
    if top_contrato_churn is not None:
        linhas.append(
            f"O contrato com maior taxa de cancelamento é '{traduzir_valor(top_contrato_churn['Contract'])}', com {_num(top_contrato_churn['Taxa de churn (%)'])}% de cancelamento."
        )
    if top_internet_churn is not None:
        linhas.append(
            f"O tipo de internet com maior taxa de cancelamento é '{traduzir_valor(top_internet_churn['Internet Type'])}', com {_num(top_internet_churn['Taxa de churn (%)'])}% de cancelamento."
        )
    if top_satisfacao is not None:
        linhas.append(
            f"A faixa de satisfação mais crítica é a nota '{top_satisfacao['Satisfaction Score']}', com {_num(top_satisfacao['Taxa de churn (%)'])}% de cancelamento."
        )

    linhas.extend(["", "3. OUTRAS ANÁLISES RELEVANTES PARA A EMPRESA"])

    if not status.empty:
        linhas.append("3.1 Carteira de clientes")
        for _, row in status.iterrows():
            linhas.append(
                f"- Status '{traduzir_valor(row['Customer Status'])}': {_inteiro(row['Clientes'])} clientes, {_num(row['Participação na base (%)'])}% da base, receita mensal estimada de {_moeda(row['Receita mensal'])}."
            )

    if top_contrato_receita is not None or top_internet_receita is not None:
        linhas.append("")
        linhas.append("3.2 Análise financeira e contratual")
        if top_contrato_receita is not None:
            linhas.append(
                f"- O contrato que mais concentra receita total é '{traduzir_valor(top_contrato_receita['Contract'])}', com {_moeda(top_contrato_receita['Receita total'])} e {_inteiro(top_contrato_receita['Clientes'])} clientes."
            )
        if top_internet_receita is not None:
            linhas.append(
                f"- O tipo de internet que mais concentra receita total é '{traduzir_valor(top_internet_receita['Internet Type'])}', com {_moeda(top_internet_receita['Receita total'])}."
            )
        linhas.append(
            f"- A comparação entre receita e cancelamento ajuda a diferenciar segmentos grandes, segmentos rentáveis e segmentos realmente críticos para retenção."
        )

    if top_servico is not None:
        linhas.append("")
        linhas.append("3.3 Produtos e serviços")
        linhas.append(
            f"- O serviço com maior adesão é '{traduzir_valor(top_servico['Serviço'])}', utilizado por {_inteiro(top_servico['Clientes aderentes'])} clientes ({_num(top_servico['Aderência (%)'])}% da base)."
        )
        linhas.append(
            "- Serviços complementares como segurança online, backup, proteção de dispositivos e suporte premium devem ser avaliados como instrumentos de fidelização e venda cruzada."
        )

    if top_permanencia_churn is not None:
        linhas.append("")
        linhas.append("3.4 Satisfação e tempo de permanência")
        linhas.append(
            f"- A faixa de permanência com maior taxa de cancelamento é '{top_permanencia_churn['Faixa de permanência']}', com {_num(top_permanencia_churn['Taxa de churn (%)'])}% de cancelamento."
        )
        linhas.append(
            "- Isso indica a importância de acompanhar a experiência nos primeiros ciclos de relacionamento e não apenas no momento do cancelamento."
        )

    if top_indicacao is not None or top_oferta_receita is not None:
        linhas.append("")
        linhas.append("3.5 Marketing, ofertas e indicações")
        if top_indicacao is not None:
            linhas.append(
                f"- A faixa de indicações com menor cancelamento é '{top_indicacao['Faixa de indicações']}', com {_num(top_indicacao['Taxa de churn (%)'])}% de cancelamento."
            )
        if top_oferta_receita is not None:
            linhas.append(
                f"- A oferta com maior receita total associada é '{traduzir_valor(top_oferta_receita['Offer'])}', com {_moeda(top_oferta_receita['Receita total'])}."
            )
        linhas.append(
            "- O programa de indicação pode ser tratado como sinal de vínculo com a marca e usado como estratégia de aquisição e retenção."
        )

    if top_cidade_clientes is not None or top_cidade_churn is not None:
        linhas.append("")
        linhas.append("3.6 Geografia")
        if top_cidade_clientes is not None:
            linhas.append(
                f"- Entre cidades com base relevante, '{top_cidade_clientes['City']}' concentra grande volume, com {_inteiro(top_cidade_clientes['Clientes'])} clientes."
            )
        if top_cidade_churn is not None:
            linhas.append(
                f"- A cidade com maior cancelamento entre as cidades filtradas é '{top_cidade_churn['City']}', com {_num(top_cidade_churn['Taxa de churn (%)'])}% de cancelamento."
            )
        linhas.append(
            "- A leitura geográfica pode apoiar campanhas locais, diagnóstico de qualidade operacional e priorização comercial por região."
        )

    linhas.extend(["", "4. CLIENTES DE ALTO VALOR E PRIORIZAÇÃO"])
    if not prioritarios.empty:
        linhas.append(
            f"Foram identificados {_inteiro(len(prioritarios))} clientes ativos exibidos como prioridade inicial na tabela do sistema, combinando alto risco, valor financeiro, mensalidade e/ou baixa satisfação."
        )
        linhas.append(
            "A empresa deve usar essa visão como fila de ação para contato preventivo, revisão de oferta ou melhoria de experiência."
        )
    else:
        linhas.append("Não foram encontrados clientes ativos prioritários com os critérios atuais.")

    linhas.extend(["", "5. FATORES ASSOCIADOS AO CANCELAMENTO"])
    if not fatores.empty:
        for _, row in fatores.iterrows():
            linhas.append(
                f"- {traduzir_coluna(row['Variável'])}: grupo crítico '{traduzir_valor(row['Grupo mais crítico'])}' com {_num(row['Taxa de churn (%)'])}% de cancelamento ({_inteiro(row['Cancelamentos'])} cancelamentos em {_inteiro(row['Clientes'])} clientes)."
            )

    linhas.extend(
        [
            "",
            "6. INTERPRETAÇÃO EXECUTIVA",
            "Os cancelamentos não parecem estar concentrados em um único aspecto. A base indica uma combinação de concorrência, baixa satisfação, contratos mais flexíveis, maior mensalidade, ausência de serviços de suporte/proteção e fragilidade nos primeiros ciclos de relacionamento.",
            "A análise adicional mostra que o problema não deve ser tratado apenas como perda de clientes, mas como uma questão de receita recorrente, segmentação, experiência, portfólio de serviços e priorização comercial.",
            "",
            "7. RECOMENDAÇÕES BASEADAS EM DADOS",
            "- Criar campanha de retenção para clientes mês a mês, oferecendo migração para contratos anuais com benefícios progressivos.",
            "- Monitorar clientes ativos com pontuação de cancelamento alta, baixa satisfação, valor de vida elevado e mensalidade elevada.",
            "- Reavaliar ofertas e benefícios para usuários de fibra óptica e segmentos onde a concorrência aparece como motivo frequente de saída.",
            "- Fortalecer suporte técnico premium, segurança online, backup e proteção de dispositivos como mecanismos de aumento de valor percebido.",
            "- Criar jornada de onboarding nos primeiros meses, pois a permanência inicial é uma janela crítica de fidelização.",
            "- Usar geografia para priorizar regiões com alta concentração de clientes, receita ou cancelamento.",
            "- Fortalecer o programa de indicação, pois indicações podem representar maior vínculo e melhor qualidade de aquisição.",
            "",
            "8. CONCLUSÃO",
            "A empresa deve tratar cancelamentos como um problema de relacionamento, proposta de valor e gestão de carteira. A estratégia recomendada é segmentar os clientes por risco, valor, satisfação, contrato, serviços contratados e geografia, aplicando ações diferentes para preço, concorrência, suporte, experiência e fidelização.",
            "",
            "Atenciosamente,",
            EMPRESA_ANALISE,
        ]
    )

    return "\n".join([linha for linha in linhas if linha is not None])
