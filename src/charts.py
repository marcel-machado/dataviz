from __future__ import annotations

import inspect

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

from .metrics import ChurnAnalyzer
from .translations import traduzir_coluna, traduzir_dataframe, traduzir_serie, traduzir_valor


TEXT = "#0e234b"
MUTED = "#596779"
GRID = "#d7e2ef"
SURFACE = "#ffffff"
NAVY = "#0e234b"
BLUE = "#0f5dab"
SKY = "#2f93d1"
ICE = "#dceeff"
SLATE = "#4f6176"
STEEL = "#7d8fa6"
WARNING = "#f2b84b"
RISK = "#d8583a"

PALETTE = [BLUE, SKY, NAVY, WARNING, SLATE, "#6aaed6", STEEL]
STATUS_COLORS = {
    "Churned": RISK,
    "Stayed": BLUE,
    "Joined": WARNING,
    "Yes": RISK,
    "No": BLUE,
    "Sim": RISK,
    "Não": BLUE,
    "Cliente cancelou": RISK,
    "Cliente permaneceu": BLUE,
    "Novo cliente": WARNING,
}
RISK_SCALE = [[0, SKY], [0.55, WARNING], [1, RISK]]
VALUE_SCALE = [[0, ICE], [1, BLUE]]


sns.set_theme(style="whitegrid", context="notebook")


class GraficosChurn:
    """Centraliza os gráficos estáticos e interativos do relatório."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.analyzer = ChurnAnalyzer(self.df)

    # ------------------------------------------------------------------
    # Helpers visuais
    # ------------------------------------------------------------------
    @staticmethod
    def _fmt_int(valor: float) -> str:
        return f"{float(valor):,.0f}".replace(",", ".")

    @staticmethod
    def _fmt_pct(valor: float) -> str:
        return f"{float(valor):.1f}%".replace(".", ",")

    @staticmethod
    def _fmt_moeda_curta(valor: float) -> str:
        valor = float(valor)
        if abs(valor) >= 1_000_000:
            return f"US$ {valor / 1_000_000:.1f} mi".replace(".", ",")
        if abs(valor) >= 1_000:
            return f"US$ {valor / 1_000:.0f} mil".replace(".", ",")
        return f"US$ {valor:.0f}".replace(".", ",")

    @staticmethod
    def _fig_ax(figsize: tuple[float, float] = (10, 5.6)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor(SURFACE)
        ax.set_facecolor(SURFACE)
        return fig, ax

    @staticmethod
    def _formatar_ax(ax, eixo_grade: str = "x") -> None:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(GRID)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(axis="both", colors=MUTED, labelsize=10)
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)
        ax.grid(True, axis=eixo_grade, color=GRID, linewidth=0.8, alpha=0.75)
        ax.set_axisbelow(True)

    def _formatar_figura(self, fig, titulo: str, subtitulo: str | None = None):
        fig.text(0.01, 0.985, titulo, ha="left", va="top", fontsize=16, fontweight="bold", color=TEXT)
        topo = 0.88
        if subtitulo:
            fig.text(0.01, 0.935, subtitulo, ha="left", va="top", fontsize=10.5, color=MUTED)
            topo = 0.84
        fig.tight_layout(rect=[0, 0, 1, topo])
        return fig

    @staticmethod
    def _rotacionar_xticks(ax, graus: int = 15):
        for label in ax.get_xticklabels():
            label.set_rotation(graus)
            label.set_horizontalalignment("right")

    @staticmethod
    def _bar_labels(ax, labels: list[str] | None = None, padding: int = 4, color: str = TEXT):
        for container in ax.containers:
            ax.bar_label(container, labels=labels, padding=padding, color=color, fontsize=9, fontweight="bold")

    def _barh(
        self,
        ax,
        labels: pd.Series,
        valores: pd.Series,
        *,
        cores: list[str] | None = None,
        formatter=None,
        xlabel: str = "",
        ylabel: str = "",
    ):
        valores = pd.to_numeric(valores, errors="coerce").fillna(0)
        labels = labels.astype(str)
        bars = ax.barh(labels, valores, color=cores or PALETTE[: len(labels)], edgecolor="none", height=0.62)
        limite = float(valores.max()) if len(valores) else 0
        ax.set_xlim(0, max(limite * 1.18, 1))
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        texto = [formatter(v) if formatter else self._fmt_int(v) for v in valores]
        ax.bar_label(bars, labels=texto, padding=5, color=TEXT, fontsize=9, fontweight="bold")
        self._formatar_ax(ax, "x")
        return bars

    @staticmethod
    def _cores_status(valores: pd.Series) -> list[str]:
        return [STATUS_COLORS.get(str(valor), SLATE) for valor in valores]

    @staticmethod
    def _traduzir_dados(tabela: pd.DataFrame) -> pd.DataFrame:
        return traduzir_dataframe(tabela)

    @staticmethod
    def _aplicar_plotly(fig: go.Figure, titulo: str, altura: int = 520) -> go.Figure:
        fig.update_layout(
            template="plotly_white",
            title=dict(text=titulo, x=0.02, xanchor="left", font=dict(size=20, color=TEXT)),
            height=altura,
            margin=dict(l=24, r=24, t=78, b=42),
            paper_bgcolor=SURFACE,
            plot_bgcolor=SURFACE,
            font=dict(family="Arial, sans-serif", size=13, color=TEXT),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, title_standoff=12)
        fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, title_standoff=12)
        return fig

    # ------------------------------------------------------------------
    # Gráficos estáticos: churn
    # ------------------------------------------------------------------
    def estatico_status_clientes(self):
        fig, ax = self._fig_ax((9.5, 5.2))
        dados = self.df["Customer Status"].value_counts().sort_values().reset_index()
        dados.columns = ["Status", "Clientes"]
        self._barh(
            ax,
            traduzir_serie(dados["Status"]),
            dados["Clientes"],
            cores=self._cores_status(dados["Status"]),
            formatter=self._fmt_int,
            xlabel="Quantidade de clientes",
        )
        return self._formatar_figura(
            fig,
            "Distribuição da carteira por status",
            "Separação entre clientes permanecidos, ingressantes e cancelados.",
        )

    def estatico_top_motivos(self):
        fig, ax = self._fig_ax((11, 6.6))
        dados = self.analyzer.top_churn_reasons(10).sort_values("Cancelamentos", ascending=True)
        self._barh(
            ax,
            traduzir_serie(dados["Churn Reason"]),
            dados["Cancelamentos"],
            cores=[RISK] * len(dados),
            formatter=self._fmt_int,
            xlabel="Cancelamentos",
        )
        return self._formatar_figura(
            fig,
            "Principais motivos específicos de cancelamento",
            "Ranking dos motivos declarados pelos clientes que saíram.",
        )

    def estatico_categorias_churn(self):
        fig, ax = self._fig_ax((9.5, 5.6))
        dados = self.analyzer.churn_categories().sort_values("Cancelamentos", ascending=True)
        self._barh(
            ax,
            traduzir_serie(dados["Churn Category"]),
            dados["Cancelamentos"],
            cores=PALETTE[: len(dados)],
            formatter=self._fmt_int,
            xlabel="Cancelamentos",
        )
        return self._formatar_figura(
            fig,
            "Cancelamentos por categoria",
            "Visão consolidada das causas de cancelamento informadas na base.",
        )

    def estatico_churn_por_contrato(self):
        fig, ax = self._fig_ax((9.5, 5.2))
        dados = self.analyzer.churn_rate_by("Contract").sort_values("Taxa de churn (%)")
        self._barh(
            ax,
            traduzir_serie(dados["Contract"]),
            dados["Taxa de churn (%)"],
            cores=[BLUE, WARNING, RISK][: len(dados)],
            formatter=self._fmt_pct,
            xlabel="Taxa de cancelamento",
        )
        media = self.analyzer.taxa_churn * 100
        ax.axvline(media, color=NAVY, linestyle="--", linewidth=1.4, alpha=0.8)
        ax.text(media, len(dados) - 0.45, f"Média {self._fmt_pct(media)}", color=NAVY, fontsize=9, fontweight="bold")
        return self._formatar_figura(
            fig,
            "Taxa de cancelamento por tipo de contrato",
            "A linha pontilhada mostra a taxa média de cancelamento da carteira.",
        )

    def estatico_churn_por_internet(self):
        fig, ax = self._fig_ax((9.5, 5.2))
        dados = self.analyzer.churn_rate_by("Internet Type").sort_values("Taxa de churn (%)")
        self._barh(
            ax,
            traduzir_serie(dados["Internet Type"]),
            dados["Taxa de churn (%)"],
            cores=PALETTE[: len(dados)],
            formatter=self._fmt_pct,
            xlabel="Taxa de cancelamento",
        )
        media = self.analyzer.taxa_churn * 100
        ax.axvline(media, color=NAVY, linestyle="--", linewidth=1.4, alpha=0.8)
        return self._formatar_figura(
            fig,
            "Taxa de cancelamento por tipo de internet",
            "Comparação de risco por tecnologia contratada.",
        )

    def estatico_churn_por_satisfacao(self):
        fig, ax = self._fig_ax((9.5, 5.4))
        dados = self.analyzer.churn_rate_by("Satisfaction Score").sort_values("Satisfaction Score")
        ax.fill_between(
            dados["Satisfaction Score"].astype(float),
            dados["Taxa de churn (%)"].astype(float),
            color=RISK,
            alpha=0.16,
        )
        ax.plot(
            dados["Satisfaction Score"],
            dados["Taxa de churn (%)"],
            marker="o",
            color=RISK,
            linewidth=2.8,
            markersize=7,
        )
        ax.set_xlabel("Nota de satisfação")
        ax.set_ylabel("Taxa de cancelamento")
        ax.set_ylim(0, max(dados["Taxa de churn (%)"].max() * 1.22, 10))
        for _, row in dados.iterrows():
            ax.text(
                row["Satisfaction Score"],
                row["Taxa de churn (%)"] + 1,
                self._fmt_pct(row["Taxa de churn (%)"]),
                ha="center",
                color=TEXT,
                fontsize=9,
                fontweight="bold",
            )
        self._formatar_ax(ax, "y")
        return self._formatar_figura(
            fig,
            "Relação entre satisfação e cancelamento",
            "Quanto menor a satisfação, maior tende a ser a taxa de cancelamento.",
        )

    def estatico_boxplot_cobranca_mensal(self):
        fig, ax = self._fig_ax((9, 5.5))
        dados = self.df.dropna(subset=["Monthly Charge"]).copy()
        if "Churn Label" not in dados.columns:
            grupos = [dados["Monthly Charge"].values]
            rotulo_parametro = "tick_labels" if "tick_labels" in inspect.signature(ax.boxplot).parameters else "labels"
            ax.boxplot(grupos, **{rotulo_parametro: ["Base"]}, patch_artist=True)
        else:
            dados["Cancelou?"] = traduzir_serie(dados["Churn Label"])
            sns.boxplot(
                data=dados,
                x="Cancelou?",
                y="Monthly Charge",
                hue="Cancelou?",
                palette=STATUS_COLORS,
                width=0.5,
                linewidth=1.2,
                showfliers=False,
                legend=False,
                ax=ax,
            )
            sns.stripplot(
                data=dados.sample(min(len(dados), 1000), random_state=42),
                x="Cancelou?",
                y="Monthly Charge",
                hue="Cancelou?",
                palette=STATUS_COLORS,
                dodge=False,
                alpha=0.18,
                size=2.4,
                legend=False,
                ax=ax,
            )
        ax.set_xlabel("Cancelou?")
        ax.set_ylabel("Cobrança mensal")
        self._formatar_ax(ax, "y")
        return self._formatar_figura(
            fig,
            "Distribuição da cobrança mensal por cancelamento",
            "Boxplot sem outliers visuais extremos, com amostra de pontos para leitura de dispersão.",
        )

    # ------------------------------------------------------------------
    # Gráficos estáticos: outras análises empresariais
    # ------------------------------------------------------------------
    def estatico_receita_por_contrato(self):
        fig, ax = self._fig_ax((9.5, 5.2))
        dados = self.analyzer.receita_por_segmento("Contract").sort_values("Receita mensal estimada")
        self._barh(
            ax,
            traduzir_serie(dados["Contract"]),
            dados["Receita mensal estimada"],
            cores=PALETTE[: len(dados)],
            formatter=self._fmt_moeda_curta,
            xlabel="Receita mensal estimada",
        )
        return self._formatar_figura(
            fig,
            "Receita mensal por contrato",
            "Concentração da receita recorrente por tipo contratual.",
        )

    def estatico_receita_por_internet(self):
        fig, ax = self._fig_ax((9.5, 5.2))
        dados = self.analyzer.receita_por_segmento("Internet Type").sort_values("Receita mensal estimada")
        self._barh(
            ax,
            traduzir_serie(dados["Internet Type"]),
            dados["Receita mensal estimada"],
            cores=PALETTE[: len(dados)],
            formatter=self._fmt_moeda_curta,
            xlabel="Receita mensal estimada",
        )
        return self._formatar_figura(
            fig,
            "Receita mensal por tipo de internet",
            "Receita recorrente associada a cada tecnologia de acesso.",
        )

    def estatico_servicos_adesao(self):
        fig, ax = self._fig_ax((10.5, 6.2))
        dados = self.analyzer.servicos_adesao().sort_values("Aderência (%)", ascending=True)
        self._barh(
            ax,
            traduzir_serie(dados["Serviço"]),
            dados["Aderência (%)"],
            cores=[SKY] * len(dados),
            formatter=self._fmt_pct,
            xlabel="Clientes aderentes",
        )
        return self._formatar_figura(
            fig,
            "Aderência aos serviços",
            "Percentual da base que utiliza cada serviço do portfólio.",
        )

    def estatico_churn_por_tempo_permanencia(self):
        fig, ax = self._fig_ax((10, 5.5))
        dados = self.analyzer.tenure_summary()
        barras = ax.bar(
            dados["Faixa de permanência"].astype(str),
            dados["Taxa de churn (%)"],
            color=RISK,
            edgecolor="none",
            width=0.58,
            label="Taxa de cancelamento",
        )
        ax.bar_label(
            barras,
            labels=[self._fmt_pct(v) for v in dados["Taxa de churn (%)"]],
            padding=4,
            color=TEXT,
            fontsize=9,
            fontweight="bold",
        )
        ax.set_xlabel("Tempo de permanência")
        ax.set_ylabel("Taxa de cancelamento")
        ax.set_ylim(0, max(dados["Taxa de churn (%)"].max() * 1.24, 10))
        self._formatar_ax(ax, "y")

        if "Satisfação média" in dados.columns:
            ax2 = ax.twinx()
            ax2.plot(
                dados["Faixa de permanência"].astype(str),
                dados["Satisfação média"],
                color=BLUE,
                linewidth=2.4,
                marker="o",
                label="Satisfação média",
            )
            ax2.set_ylabel("Satisfação média", color=BLUE)
            ax2.tick_params(axis="y", colors=BLUE)
            ax2.set_ylim(0, 5)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_color(GRID)

        return self._formatar_figura(
            fig,
            "Cancelamento por tempo de permanência",
            "Barras mostram cancelamento; linha mostra satisfação média por faixa de permanência.",
        )

    def estatico_clientes_por_faixa_etaria(self):
        fig, ax = self._fig_ax((9, 5.2))
        dados = self.analyzer.age_summary()
        barras = ax.bar(
            dados["Faixa etária"].astype(str),
            dados["Clientes"],
            color=[BLUE, SKY, NAVY, WARNING][: len(dados)],
            edgecolor="none",
            width=0.58,
        )
        ax.bar_label(
            barras,
            labels=[self._fmt_int(v) for v in dados["Clientes"]],
            padding=4,
            color=TEXT,
            fontsize=9,
            fontweight="bold",
        )
        ax.set_xlabel("Faixa etária")
        ax.set_ylabel("Clientes")
        ax.set_ylim(0, max(dados["Clientes"].max() * 1.18, 10))
        self._formatar_ax(ax, "y")
        return self._formatar_figura(
            fig,
            "Distribuição de clientes por faixa etária",
            "Composição demográfica da carteira analisada.",
        )

    def estatico_satisfacao_media_por_status(self):
        fig, ax = self._fig_ax((9, 5.2))
        dados = self.analyzer.status_summary().sort_values("Satisfação média")
        self._barh(
            ax,
            traduzir_serie(dados["Customer Status"]),
            dados["Satisfação média"],
            cores=self._cores_status(dados["Customer Status"]),
            formatter=lambda v: f"{v:.2f}".replace(".", ","),
            xlabel="Satisfação média",
        )
        ax.set_xlim(0, 5)
        return self._formatar_figura(
            fig,
            "Satisfação média por status",
            "Comparação de experiência percebida entre grupos da carteira.",
        )

    def estatico_churn_por_indicacoes(self):
        fig, ax = self._fig_ax((9, 5.2))
        dados = self.analyzer.referral_summary()
        barras = ax.bar(
            dados["Faixa de indicações"].astype(str),
            dados["Taxa de churn (%)"],
            color=[RISK, WARNING, SKY, BLUE][: len(dados)],
            edgecolor="none",
            width=0.58,
        )
        ax.bar_label(
            barras,
            labels=[self._fmt_pct(v) for v in dados["Taxa de churn (%)"]],
            padding=4,
            color=TEXT,
            fontsize=9,
            fontweight="bold",
        )
        ax.set_xlabel("Quantidade de indicações")
        ax.set_ylabel("Taxa de cancelamento")
        ax.set_ylim(0, max(dados["Taxa de churn (%)"].max() * 1.2, 10))
        self._formatar_ax(ax, "y")
        return self._formatar_figura(
            fig,
            "Cancelamento por quantidade de indicações",
            "Indicações funcionam como sinal de vínculo com a marca.",
        )

    # ------------------------------------------------------------------
    # Gráficos interativos: churn e negócio
    # ------------------------------------------------------------------
    def interativo_churn_por_contrato(self):
        dados_raw = self.analyzer.churn_rate_by("Contract").sort_values("Taxa de churn (%)", ascending=False)
        dados = traduzir_dataframe(dados_raw)
        fig = px.bar(
            dados,
            x="Contrato",
            y="Taxa de cancelamento (%)",
            color="Taxa de cancelamento (%)",
            color_continuous_scale=RISK_SCALE,
            text="Taxa de cancelamento (%)",
            hover_data=["Clientes", "Cancelamentos", "Participação na base (%)"],
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0)
        fig.update_layout(coloraxis_colorbar_title="Cancelamento")
        fig.update_yaxes(title="Taxa de cancelamento (%)", range=[0, max(dados["Taxa de cancelamento (%)"].max() * 1.25, 10)])
        fig.update_xaxes(title="Contrato")
        return self._aplicar_plotly(fig, "Taxa de cancelamento por contrato", 500)

    def interativo_motivos_churn(self):
        dados_raw = self.analyzer.top_churn_reasons(12).sort_values("Cancelamentos", ascending=True)
        dados = traduzir_dataframe(dados_raw)
        fig = px.bar(
            dados,
            x="Cancelamentos",
            y="Motivo do cancelamento",
            orientation="h",
            color="Percentual (%)",
            color_continuous_scale=RISK_SCALE,
            text="Cancelamentos",
            hover_data=["Percentual (%)"],
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(coloraxis_colorbar_title="% dos cancelamentos")
        fig.update_xaxes(title="Cancelamentos")
        fig.update_yaxes(title="")
        return self._aplicar_plotly(fig, "Top motivos de cancelamento", 610)

    def interativo_distribuicao_mensalidade(self):
        dados = traduzir_dataframe(self.df)
        fig = px.box(
            dados,
            x="Cancelou?",
            y="Cobrança mensal",
            color="Cancelou?",
            color_discrete_map=STATUS_COLORS,
            points="outliers",
            hover_data=["Contrato", "Tipo de internet", "Nota de satisfação"],
        )
        fig.update_traces(marker_opacity=0.45, line_width=1.4)
        fig.update_xaxes(title="Cancelou?")
        fig.update_yaxes(title="Cobrança mensal")
        return self._aplicar_plotly(fig, "Mensalidade por status de cancelamento", 520)

    def interativo_churn_score_cltv(self):
        dados = traduzir_dataframe(self.df)
        fig = px.scatter(
            dados,
            x="Pontuação de cancelamento",
            y="Valor de vida do cliente (CLTV)",
            color="Cancelou?",
            color_discrete_map=STATUS_COLORS,
            size="Cobrança mensal",
            size_max=18,
            opacity=0.72,
            hover_data=["ID do cliente", "Contrato", "Tipo de internet", "Cobrança mensal", "Nota de satisfação"],
        )
        if "CLTV" in self.df.columns:
            fig.add_hline(
                y=float(self.df["CLTV"].mean()),
                line_dash="dash",
                line_color=NAVY,
                opacity=0.65,
                annotation_text="Valor de vida médio",
                annotation_position="bottom right",
            )
        fig.add_vline(
            x=70,
            line_dash="dash",
            line_color=RISK,
            opacity=0.7,
            annotation_text="Risco alto",
            annotation_position="top left",
        )
        fig.update_xaxes(title="Pontuação de cancelamento")
        fig.update_yaxes(title="Valor de vida do cliente (CLTV)")
        return self._aplicar_plotly(fig, "Risco de cancelamento x valor de vida do cliente", 620)

    def interativo_receita_por_status(self):
        dados = traduzir_dataframe(self.analyzer.status_summary())
        fig = px.bar(
            dados,
            x="Status do cliente",
            y="Receita total",
            color="Status do cliente",
            color_discrete_map=STATUS_COLORS,
            text="Clientes",
            hover_data=["Clientes", "Receita mensal", "Mensalidade média", "Satisfação média"],
        )
        fig.update_traces(texttemplate="%{text:.0f} clientes", textposition="outside", marker_line_width=0)
        fig.update_xaxes(title="Status do cliente")
        fig.update_yaxes(title="Receita total")
        return self._aplicar_plotly(fig, "Receita total por status do cliente", 520)

    def interativo_treemap_receita(self):
        dados = traduzir_dataframe(self.df)
        fig = px.treemap(
            dados,
            path=["Contrato", "Tipo de internet", "Status do cliente"],
            values="Receita total",
            color="Cobrança mensal",
            color_continuous_scale=VALUE_SCALE,
            hover_data=["Pontuação de cancelamento", "Nota de satisfação", "Valor de vida do cliente (CLTV)"],
        )
        fig.update_traces(root_color="#f4f7fb", marker_line_color="#ffffff", marker_line_width=2)
        fig.update_layout(coloraxis_colorbar_title="Mensalidade")
        return self._aplicar_plotly(fig, "Composição da receita por contrato, internet e status", 640)

    def interativo_servicos_churn(self):
        dados = traduzir_dataframe(self.analyzer.servicos_adesao())
        fig = px.scatter(
            dados,
            x="Aderência (%)",
            y="Taxa de cancelamento dos aderentes (%)",
            size="Clientes aderentes",
            color="Taxa de cancelamento dos aderentes (%)",
            color_continuous_scale=RISK_SCALE,
            hover_name="Serviço",
            hover_data=["Receita mensal dos aderentes", "Mensalidade média aderentes"],
            size_max=34,
        )
        fig.update_traces(marker=dict(line=dict(width=1, color="#ffffff")), opacity=0.86)
        fig.update_layout(coloraxis_colorbar_title="Cancelamento")
        fig.update_xaxes(title="Aderência (%)")
        fig.update_yaxes(title="Taxa de cancelamento dos aderentes (%)")
        return self._aplicar_plotly(fig, "Aderência de serviços x cancelamento dos aderentes", 570)

    def interativo_cidades_receita_churn(self):
        dados = traduzir_dataframe(self.analyzer.top_cidades(limite=40, min_clientes=10, ordenar_por="Clientes"))
        fig = px.scatter(
            dados,
            x="Clientes",
            y="Receita mensal estimada",
            size="Receita total",
            color="Taxa de cancelamento (%)",
            color_continuous_scale=RISK_SCALE,
            hover_name="Cidade",
            hover_data=["Estado", "Cancelamentos", "Mensalidade média", "Satisfação média"],
            size_max=38,
        )
        fig.update_traces(marker=dict(line=dict(width=1, color="#ffffff")), opacity=0.86)
        fig.update_layout(coloraxis_colorbar_title="Cancelamento")
        fig.update_xaxes(title="Clientes")
        fig.update_yaxes(title="Receita mensal estimada")
        return self._aplicar_plotly(fig, "Cidades: base de clientes, receita e cancelamento", 590)

    def interativo_permanencia_receita(self):
        dados = traduzir_dataframe(self.analyzer.tenure_summary())
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=dados["Faixa de permanência"].astype(str),
                y=dados["Taxa de cancelamento (%)"],
                name="Taxa de cancelamento",
                marker_color=RISK,
                text=[self._fmt_pct(v) for v in dados["Taxa de cancelamento (%)"]],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Cancelamento: %{y:.1f}%<extra></extra>",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=dados["Faixa de permanência"].astype(str),
                y=dados["Satisfação média"],
                name="Satisfação média",
                mode="lines+markers",
                line=dict(color=BLUE, width=3),
                marker=dict(size=9, color=BLUE),
                hovertemplate="<b>%{x}</b><br>Satisfação: %{y:.2f}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig.update_yaxes(title_text="Taxa de cancelamento (%)", secondary_y=False)
        fig.update_yaxes(title_text="Satisfação média", range=[0, 5], secondary_y=True)
        fig.update_xaxes(title_text="Tempo de permanência")
        return self._aplicar_plotly(fig, "Tempo de permanência: cancelamento e satisfação", 560)

    def interativo_mapa_clientes(self):
        amostra = self.df.copy()
        if len(amostra) > 2500:
            amostra = amostra.sample(2500, random_state=42)
        amostra = traduzir_dataframe(amostra)
        fig = px.scatter_mapbox(
            amostra,
            lat="Latitude",
            lon="Longitude",
            color="Cancelou?",
            color_discrete_map=STATUS_COLORS,
            size="Cobrança mensal",
            hover_name="Cidade",
            hover_data=["ID do cliente", "Contrato", "Tipo de internet", "Pontuação de cancelamento"],
            zoom=4,
            height=620,
        )
        fig.update_traces(marker=dict(opacity=0.72))
        fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 76, "l": 0, "b": 0})
        return self._aplicar_plotly(fig, "Distribuição geográfica de clientes e cancelamento", 640)


CHURN_STATIC_CHARTS = {
    "Status dos clientes": "estatico_status_clientes",
    "Top motivos de cancelamento": "estatico_top_motivos",
    "Categorias de cancelamento": "estatico_categorias_churn",
    "Cancelamento por contrato": "estatico_churn_por_contrato",
    "Cancelamento por tipo de internet": "estatico_churn_por_internet",
    "Cancelamento por satisfação": "estatico_churn_por_satisfacao",
    "Boxplot da cobrança mensal": "estatico_boxplot_cobranca_mensal",
}

BUSINESS_STATIC_CHARTS = {
    "Receita mensal por contrato": "estatico_receita_por_contrato",
    "Receita mensal por tipo de internet": "estatico_receita_por_internet",
    "Aderência aos serviços": "estatico_servicos_adesao",
    "Cancelamento por tempo de permanência": "estatico_churn_por_tempo_permanencia",
    "Clientes por faixa etária": "estatico_clientes_por_faixa_etaria",
    "Satisfação média por status": "estatico_satisfacao_media_por_status",
    "Cancelamento por indicações": "estatico_churn_por_indicacoes",
}

STATIC_CHARTS = {**CHURN_STATIC_CHARTS, **BUSINESS_STATIC_CHARTS}

CHURN_INTERACTIVE_CHARTS = {
    "Taxa de cancelamento por contrato": "interativo_churn_por_contrato",
    "Top motivos de cancelamento": "interativo_motivos_churn",
    "Distribuição da mensalidade": "interativo_distribuicao_mensalidade",
    "Pontuação de cancelamento x valor de vida": "interativo_churn_score_cltv",
}

BUSINESS_INTERACTIVE_CHARTS = {
    "Receita por status": "interativo_receita_por_status",
    "Treemap da receita": "interativo_treemap_receita",
    "Serviços: aderência x cancelamento": "interativo_servicos_churn",
    "Cidades: receita x cancelamento": "interativo_cidades_receita_churn",
    "Tempo de permanência": "interativo_permanencia_receita",
    "Mapa de clientes": "interativo_mapa_clientes",
}

INTERACTIVE_CHARTS = {**CHURN_INTERACTIVE_CHARTS, **BUSINESS_INTERACTIVE_CHARTS}
