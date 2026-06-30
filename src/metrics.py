from __future__ import annotations

import numpy as np
import pandas as pd

from .translations import traduzir_coluna


class ChurnAnalyzer:
    """Classe central para cálculos de churn e análises gerenciais.

    A ideia é manter as regras de negócio fora das páginas Streamlit. Assim, as páginas
    ficam focadas na apresentação e esta classe centraliza métricas, tabelas e
    segmentações reutilizáveis.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if "Churn Value" not in self.df.columns and "Churn Label" in self.df.columns:
            self.df["Churn Value"] = self.df["Churn Label"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
        if "Churn Value" not in self.df.columns:
            self.df["Churn Value"] = 0

    # -------------------------------------------------------------------------
    # Propriedades executivas
    # -------------------------------------------------------------------------
    @property
    def total_clientes(self) -> int:
        return int(len(self.df))

    @property
    def total_cancelamentos(self) -> int:
        return int(self.df["Churn Value"].sum())

    @property
    def taxa_churn(self) -> float:
        if self.total_clientes == 0:
            return 0.0
        return self.total_cancelamentos / self.total_clientes

    @property
    def clientes_ativos_ou_permanecidos(self) -> int:
        if "Customer Status" in self.df.columns:
            return int(self.df["Customer Status"].isin(["Stayed", "Joined"]).sum())
        return self.total_clientes - self.total_cancelamentos

    @property
    def receita_total(self) -> float:
        return self._sum("Total Revenue")

    @property
    def receita_mensal_estimativa(self) -> float:
        return self._sum("Monthly Charge")

    @property
    def mensalidade_media(self) -> float:
        return self._mean("Monthly Charge")

    @property
    def receita_em_risco_churn(self) -> float:
        if "Total Revenue" not in self.df.columns:
            return 0.0
        return float(self.df.loc[self.df["Churn Value"] == 1, "Total Revenue"].sum())

    @property
    def receita_mensal_perdida_churn(self) -> float:
        if "Monthly Charge" not in self.df.columns:
            return 0.0
        return float(self.df.loc[self.df["Churn Value"] == 1, "Monthly Charge"].sum())

    @property
    def cltv_total_previsto(self) -> float:
        return self._sum("CLTV")

    @property
    def score_churn_medio(self) -> float:
        return self._mean("Churn Score")

    @property
    def satisfacao_media(self) -> float:
        return self._mean("Satisfaction Score")

    # -------------------------------------------------------------------------
    # Helpers internos
    # -------------------------------------------------------------------------
    def _sum(self, coluna: str) -> float:
        if coluna not in self.df.columns:
            return 0.0
        return float(pd.to_numeric(self.df[coluna], errors="coerce").fillna(0).sum())

    def _mean(self, coluna: str) -> float:
        if coluna not in self.df.columns or len(self.df) == 0:
            return 0.0
        return float(pd.to_numeric(self.df[coluna], errors="coerce").mean())

    def _count_col(self) -> tuple[str, str]:
        if "Customer ID" in self.df.columns:
            return "Customer ID", "count"
        return "Churn Value", "size"

    @staticmethod
    def _pct(valor: float) -> float:
        if pd.isna(valor) or np.isinf(valor):
            return 0.0
        return round(float(valor) * 100, 2)

    @staticmethod
    def _ordenar_faixa(tabela: pd.DataFrame, coluna: str, ordem: list[str]) -> pd.DataFrame:
        if tabela.empty or coluna not in tabela.columns:
            return tabela
        tabela = tabela.copy()
        tabela[coluna] = pd.Categorical(tabela[coluna], categories=ordem, ordered=True)
        return tabela.sort_values(coluna).reset_index(drop=True)

    # -------------------------------------------------------------------------
    # Tabelas principais de churn
    # -------------------------------------------------------------------------
    def churn_rate_by(self, coluna: str) -> pd.DataFrame:
        if coluna not in self.df.columns:
            return pd.DataFrame(columns=[coluna, "Clientes", "Cancelamentos", "Taxa de churn (%)"])

        tabela = (
            self.df.groupby(coluna, dropna=False)
            .agg(Clientes=(self._count_col()[0], self._count_col()[1]), Cancelamentos=("Churn Value", "sum"))
            .reset_index()
        )
        tabela["Taxa de churn (%)"] = (tabela["Cancelamentos"] / tabela["Clientes"] * 100).round(2)
        tabela["Participação na base (%)"] = (tabela["Clientes"] / max(self.total_clientes, 1) * 100).round(2)
        tabela = tabela.sort_values(["Taxa de churn (%)", "Cancelamentos"], ascending=False)
        return tabela

    def top_churn_reasons(self, limite: int = 10) -> pd.DataFrame:
        if "Churn Reason" not in self.df.columns:
            return pd.DataFrame(columns=["Churn Reason", "Cancelamentos", "Percentual (%)"])

        churn = self.df[self.df["Churn Value"] == 1]
        tabela = (
            churn["Churn Reason"]
            .value_counts(dropna=False)
            .head(limite)
            .rename_axis("Churn Reason")
            .reset_index(name="Cancelamentos")
        )
        total = max(len(churn), 1)
        tabela["Percentual (%)"] = (tabela["Cancelamentos"] / total * 100).round(2)
        return tabela

    def churn_categories(self) -> pd.DataFrame:
        if "Churn Category" not in self.df.columns:
            return pd.DataFrame(columns=["Churn Category", "Cancelamentos", "Percentual (%)"])
        churn = self.df[self.df["Churn Value"] == 1]
        tabela = (
            churn["Churn Category"]
            .value_counts(dropna=False)
            .rename_axis("Churn Category")
            .reset_index(name="Cancelamentos")
        )
        total = max(len(churn), 1)
        tabela["Percentual (%)"] = (tabela["Cancelamentos"] / total * 100).round(2)
        return tabela

    def principais_fatores(self) -> pd.DataFrame:
        """Retorna o grupo mais crítico em várias dimensões de negócio."""
        fatores: list[dict] = []
        colunas = [
            "Contract",
            "Internet Type",
            "Payment Method",
            "Offer",
            "Satisfaction Score",
            "Senior Citizen",
            "Under 30",
            "Dependents",
            "Married",
            "Paperless Billing",
            "Premium Tech Support",
            "Online Security",
            "Online Backup",
            "Device Protection Plan",
            "Referred a Friend",
        ]
        for coluna in colunas:
            tabela = self.churn_rate_by(coluna)
            if tabela.empty:
                continue
            linha = tabela.iloc[0]
            fatores.append(
                {
                    "Variável": coluna,
                    "Grupo mais crítico": str(linha[coluna]),
                    "Clientes": int(linha["Clientes"]),
                    "Cancelamentos": int(linha["Cancelamentos"]),
                    "Taxa de churn (%)": float(linha["Taxa de churn (%)"]),
                }
            )
        if not fatores:
            return pd.DataFrame()
        return pd.DataFrame(fatores).sort_values("Taxa de churn (%)", ascending=False).reset_index(drop=True)

    # -------------------------------------------------------------------------
    # Tabelas de negócio além do cancelamento
    # -------------------------------------------------------------------------
    def tabela_executiva(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Indicador": [
                    "Total de clientes",
                    "Clientes que cancelaram",
                    "Taxa geral de churn",
                    "Clientes permanecidos/ingressados",
                    "Receita total observada",
                    "Receita mensal recorrente estimada",
                    "Receita associada a clientes cancelados",
                    "Receita mensal perdida nos cancelamentos",
                    "Mensalidade média",
                    "Satisfação média",
                    "Churn Score médio",
                ],
                "Valor": [
                    self._fmt_int(self.total_clientes),
                    self._fmt_int(self.total_cancelamentos),
                    self._fmt_pct(self.taxa_churn),
                    self._fmt_int(self.clientes_ativos_ou_permanecidos),
                    self._fmt_moeda(self.receita_total),
                    self._fmt_moeda(self.receita_mensal_estimativa),
                    self._fmt_moeda(self.receita_em_risco_churn),
                    self._fmt_moeda(self.receita_mensal_perdida_churn),
                    self._fmt_moeda(self.mensalidade_media),
                    f"{self.satisfacao_media:.2f}".replace(".", ","),
                    f"{self.score_churn_medio:.2f}".replace(".", ","),
                ],
            }
        )

    def resumo_numerico_por_churn(self) -> pd.DataFrame:
        colunas = [
            "Age",
            "Tenure in Months",
            "Monthly Charge",
            "Total Charges",
            "Total Revenue",
            "Satisfaction Score",
            "Churn Score",
            "CLTV",
            "Number of Referrals",
            "Number of Dependents",
            "Avg Monthly GB Download",
            "Total Extra Data Charges",
        ]
        existentes = [c for c in colunas if c in self.df.columns]
        if not existentes or "Churn Label" not in self.df.columns:
            return pd.DataFrame()
        tabela = self.df.groupby("Churn Label")[existentes].mean().T.round(2)
        tabela.index.name = "Indicador"
        tabela = tabela.reset_index()
        tabela["Indicador"] = tabela["Indicador"].map(traduzir_coluna)
        tabela = tabela.rename(columns=traduzir_coluna)
        return tabela

    def status_summary(self) -> pd.DataFrame:
        if "Customer Status" not in self.df.columns:
            return pd.DataFrame()
        tabela = (
            self.df.groupby("Customer Status", dropna=False)
            .agg(
                Clientes=(self._count_col()[0], self._count_col()[1]),
                Cancelamentos=("Churn Value", "sum"),
                Receita_total=("Total Revenue", "sum") if "Total Revenue" in self.df.columns else ("Churn Value", "sum"),
                Receita_mensal=("Monthly Charge", "sum") if "Monthly Charge" in self.df.columns else ("Churn Value", "sum"),
                Mensalidade_media=("Monthly Charge", "mean") if "Monthly Charge" in self.df.columns else ("Churn Value", "mean"),
                Satisfacao_media=("Satisfaction Score", "mean") if "Satisfaction Score" in self.df.columns else ("Churn Value", "mean"),
                Churn_score_medio=("Churn Score", "mean") if "Churn Score" in self.df.columns else ("Churn Value", "mean"),
                CLTV_medio=("CLTV", "mean") if "CLTV" in self.df.columns else ("Churn Value", "mean"),
            )
            .reset_index()
        )
        tabela["Participação na base (%)"] = (tabela["Clientes"] / max(self.total_clientes, 1) * 100).round(2)
        tabela["Taxa de churn (%)"] = (tabela["Cancelamentos"] / tabela["Clientes"] * 100).round(2)
        tabela = tabela.rename(
            columns={
                "Receita_total": "Receita total",
                "Receita_mensal": "Receita mensal",
                "Mensalidade_media": "Mensalidade média",
                "Satisfacao_media": "Satisfação média",
                "Churn_score_medio": "Churn Score médio",
                "CLTV_medio": "CLTV médio",
            }
        )
        return tabela.round(2).sort_values("Clientes", ascending=False).reset_index(drop=True)

    def resumo_financeiro(self) -> pd.DataFrame:
        indicadores = [
            ("Receita total observada", self.receita_total),
            ("Receita mensal recorrente estimada", self.receita_mensal_estimativa),
            ("Receita de clientes cancelados", self.receita_em_risco_churn),
            ("Receita mensal perdida nos cancelamentos", self.receita_mensal_perdida_churn),
            ("Mensalidade média geral", self.mensalidade_media),
            ("Mensalidade média dos clientes que cancelaram", self._mean_churn("Monthly Charge", 1)),
            ("Mensalidade média dos clientes que permaneceram", self._mean_churn("Monthly Charge", 0)),
            ("Total de reembolsos", self._sum("Total Refunds")),
            ("Cobranças extras de dados", self._sum("Total Extra Data Charges")),
            ("Cobranças totais de longa distância", self._sum("Total Long Distance Charges")),
            ("CLTV total previsto", self.cltv_total_previsto),
            ("CLTV médio", self._mean("CLTV")),
        ]
        return pd.DataFrame(
            {
                "Indicador financeiro": [i[0] for i in indicadores],
                "Valor": [self._fmt_moeda(i[1]) for i in indicadores],
            }
        )

    def _mean_churn(self, coluna: str, churn_value: int) -> float:
        if coluna not in self.df.columns:
            return 0.0
        dados = self.df.loc[self.df["Churn Value"] == churn_value, coluna]
        if dados.empty:
            return 0.0
        return float(dados.mean())

    def receita_por_segmento(self, coluna: str) -> pd.DataFrame:
        if coluna not in self.df.columns:
            return pd.DataFrame()
        agregacoes = {
            "Clientes": (self._count_col()[0], self._count_col()[1]),
            "Cancelamentos": ("Churn Value", "sum"),
        }
        if "Total Revenue" in self.df.columns:
            agregacoes["Receita total"] = ("Total Revenue", "sum")
        if "Monthly Charge" in self.df.columns:
            agregacoes["Receita mensal estimada"] = ("Monthly Charge", "sum")
            agregacoes["Mensalidade média"] = ("Monthly Charge", "mean")
        if "Satisfaction Score" in self.df.columns:
            agregacoes["Satisfação média"] = ("Satisfaction Score", "mean")
        if "CLTV" in self.df.columns:
            agregacoes["CLTV médio"] = ("CLTV", "mean")

        tabela = self.df.groupby(coluna, dropna=False).agg(**agregacoes).reset_index()
        tabela["Taxa de churn (%)"] = (tabela["Cancelamentos"] / tabela["Clientes"] * 100).round(2)
        return tabela.round(2).sort_values("Receita total" if "Receita total" in tabela.columns else "Clientes", ascending=False).reset_index(drop=True)

    def servicos_adesao(self) -> pd.DataFrame:
        servicos = [
            "Phone Service",
            "Multiple Lines",
            "Internet Service",
            "Online Security",
            "Online Backup",
            "Device Protection Plan",
            "Premium Tech Support",
            "Streaming TV",
            "Streaming Movies",
            "Streaming Music",
            "Unlimited Data",
        ]
        linhas: list[dict] = []
        for servico in servicos:
            if servico not in self.df.columns:
                continue
            aderentes = self.df[self.df[servico].astype(str).str.lower().eq("yes")]
            clientes = len(aderentes)
            cancelamentos = int(aderentes["Churn Value"].sum()) if clientes else 0
            linhas.append(
                {
                    "Serviço": servico,
                    "Clientes aderentes": clientes,
                    "Aderência (%)": round(clientes / max(self.total_clientes, 1) * 100, 2),
                    "Cancelamentos entre aderentes": cancelamentos,
                    "Taxa de churn dos aderentes (%)": round(cancelamentos / max(clientes, 1) * 100, 2),
                    "Receita mensal dos aderentes": round(float(aderentes["Monthly Charge"].sum()), 2) if "Monthly Charge" in aderentes.columns else 0.0,
                    "Mensalidade média aderentes": round(float(aderentes["Monthly Charge"].mean()), 2) if clientes and "Monthly Charge" in aderentes.columns else 0.0,
                }
            )
        return pd.DataFrame(linhas).sort_values("Aderência (%)", ascending=False).reset_index(drop=True)

    def satisfacao_summary(self) -> pd.DataFrame:
        tabela = self.churn_rate_by("Satisfaction Score")
        if tabela.empty:
            return tabela
        agreg = self.receita_por_segmento("Satisfaction Score")
        manter = ["Satisfaction Score", "Mensalidade média", "Satisfação média", "CLTV médio"]
        extras = [c for c in manter if c in agreg.columns]
        if len(extras) > 1:
            tabela = tabela.merge(agreg[extras], on="Satisfaction Score", how="left")
        return tabela.sort_values("Satisfaction Score").reset_index(drop=True)

    def tenure_summary(self) -> pd.DataFrame:
        if "Tenure in Months" not in self.df.columns:
            return pd.DataFrame()
        ordem = ["0-6 meses", "7-12 meses", "13-24 meses", "25-48 meses", "49+ meses"]
        bins = [-1, 6, 12, 24, 48, np.inf]
        tmp = self.df.copy()
        tmp["Faixa de permanência"] = pd.cut(tmp["Tenure in Months"], bins=bins, labels=ordem)
        tabela = self._summary_for_temp_col(tmp, "Faixa de permanência")
        return self._ordenar_faixa(tabela, "Faixa de permanência", ordem)

    def age_summary(self) -> pd.DataFrame:
        if "Age" not in self.df.columns:
            return pd.DataFrame()
        ordem = ["18-29", "30-44", "45-64", "65+"]
        bins = [17, 29, 44, 64, np.inf]
        tmp = self.df.copy()
        tmp["Faixa etária"] = pd.cut(tmp["Age"], bins=bins, labels=ordem)
        tabela = self._summary_for_temp_col(tmp, "Faixa etária")
        return self._ordenar_faixa(tabela, "Faixa etária", ordem)

    def referral_summary(self) -> pd.DataFrame:
        if "Number of Referrals" not in self.df.columns:
            return pd.DataFrame()
        ordem = ["0", "1", "2-3", "4+"]
        bins = [-1, 0, 1, 3, np.inf]
        tmp = self.df.copy()
        tmp["Faixa de indicações"] = pd.cut(tmp["Number of Referrals"], bins=bins, labels=ordem)
        tabela = self._summary_for_temp_col(tmp, "Faixa de indicações")
        return self._ordenar_faixa(tabela, "Faixa de indicações", ordem)

    def _summary_for_temp_col(self, tmp: pd.DataFrame, coluna: str) -> pd.DataFrame:
        agregacoes = {
            "Clientes": (self._count_col()[0], self._count_col()[1]),
            "Cancelamentos": ("Churn Value", "sum"),
        }
        if "Monthly Charge" in tmp.columns:
            agregacoes["Receita mensal estimada"] = ("Monthly Charge", "sum")
            agregacoes["Mensalidade média"] = ("Monthly Charge", "mean")
        if "Total Revenue" in tmp.columns:
            agregacoes["Receita total"] = ("Total Revenue", "sum")
        if "Satisfaction Score" in tmp.columns:
            agregacoes["Satisfação média"] = ("Satisfaction Score", "mean")
        if "CLTV" in tmp.columns:
            agregacoes["CLTV médio"] = ("CLTV", "mean")

        tabela = tmp.groupby(coluna, observed=False).agg(**agregacoes).reset_index()
        tabela["Taxa de churn (%)"] = (tabela["Cancelamentos"] / tabela["Clientes"] * 100).round(2)
        return tabela.round(2)

    def perfil_demografico(self) -> pd.DataFrame:
        dimensoes = ["Gender", "Under 30", "Senior Citizen", "Married", "Dependents"]
        linhas: list[pd.DataFrame] = []
        for dim in dimensoes:
            if dim not in self.df.columns:
                continue
            tabela = self.churn_rate_by(dim)
            if tabela.empty:
                continue
            tabela.insert(0, "Dimensão", dim)
            tabela = tabela.rename(columns={dim: "Grupo"})
            linhas.append(tabela[["Dimensão", "Grupo", "Clientes", "Cancelamentos", "Taxa de churn (%)", "Participação na base (%)"]])
        if not linhas:
            return pd.DataFrame()
        return pd.concat(linhas, ignore_index=True)

    def top_cidades(self, limite: int = 15, min_clientes: int = 20, ordenar_por: str = "Clientes") -> pd.DataFrame:
        if "City" not in self.df.columns:
            return pd.DataFrame()
        agrupadores = ["City"]
        if "State" in self.df.columns:
            agrupadores.append("State")
        agregacoes = {
            "Clientes": (self._count_col()[0], self._count_col()[1]),
            "Cancelamentos": ("Churn Value", "sum"),
        }
        if "Total Revenue" in self.df.columns:
            agregacoes["Receita total"] = ("Total Revenue", "sum")
        if "Monthly Charge" in self.df.columns:
            agregacoes["Receita mensal estimada"] = ("Monthly Charge", "sum")
            agregacoes["Mensalidade média"] = ("Monthly Charge", "mean")
        if "Satisfaction Score" in self.df.columns:
            agregacoes["Satisfação média"] = ("Satisfaction Score", "mean")
        tabela = self.df.groupby(agrupadores, dropna=False).agg(**agregacoes).reset_index()
        tabela["Taxa de churn (%)"] = (tabela["Cancelamentos"] / tabela["Clientes"] * 100).round(2)
        tabela = tabela[tabela["Clientes"] >= min_clientes]
        ordenar = ordenar_por if ordenar_por in tabela.columns else "Clientes"
        return tabela.round(2).sort_values(ordenar, ascending=False).head(limite).reset_index(drop=True)

    def clientes_prioritarios(self, limite: int = 20) -> pd.DataFrame:
        """Clientes ainda na base que combinam alto risco, alto valor e/ou baixa satisfação."""
        if self.df.empty:
            return pd.DataFrame()
        tmp = self.df[self.df["Churn Value"] == 0].copy()
        if tmp.empty:
            return pd.DataFrame()

        score_limite = max(70, float(tmp["Churn Score"].quantile(0.75))) if "Churn Score" in tmp.columns else 70
        cltv_limite = float(tmp["CLTV"].quantile(0.75)) if "CLTV" in tmp.columns else 0
        mensalidade_limite = float(tmp["Monthly Charge"].quantile(0.75)) if "Monthly Charge" in tmp.columns else 0

        if "Churn Score" in tmp.columns:
            tmp["Pontos prioridade"] = (tmp["Churn Score"] >= score_limite).astype(int) * 3
        else:
            tmp["Pontos prioridade"] = 0
        if "CLTV" in tmp.columns:
            tmp["Pontos prioridade"] += (tmp["CLTV"] >= cltv_limite).astype(int) * 2
        if "Monthly Charge" in tmp.columns:
            tmp["Pontos prioridade"] += (tmp["Monthly Charge"] >= mensalidade_limite).astype(int) * 1
        if "Satisfaction Score" in tmp.columns:
            tmp["Pontos prioridade"] += (tmp["Satisfaction Score"] <= 2).astype(int) * 2

        colunas = [
            "Customer ID",
            "Customer Status",
            "Contract",
            "Internet Type",
            "Monthly Charge",
            "Satisfaction Score",
            "Churn Score",
            "CLTV",
            "Tenure in Months",
            "Pontos prioridade",
        ]
        existentes = [c for c in colunas if c in tmp.columns]
        return tmp[existentes].sort_values(["Pontos prioridade", "Churn Score", "CLTV"], ascending=False).head(limite).reset_index(drop=True)

    def resumo_analises_adicionais(self) -> pd.DataFrame:
        """Lista as análises além do churn e a pergunta empresarial respondida."""
        return pd.DataFrame(
            {
                "Área analisada": [
                    "Carteira de clientes",
                    "Financeiro",
                    "Contratos",
                    "Produtos e serviços",
                    "Satisfação",
                    "Perfil do cliente",
                    "Geografia",
                    "Marketing e indicação",
                    "Valor de vida e priorização",
                    "Tempo de permanência",
                ],
                "Pergunta de negócio": [
                    "Quem compõe a base: clientes novos, ativos e desligados?",
                    "Onde está a receita, o ticket médio e a perda mensal?",
                    "Quais contratos sustentam mais estabilidade e receita?",
                    "Quais serviços têm maior adesão e melhor vínculo com o cliente?",
                    "A experiência percebida ajuda a explicar risco e fidelização?",
                    "Quais perfis são mais estáveis ou mais frágeis?",
                    "Quais cidades concentram clientes, receita e risco?",
                    "Indicações e ofertas trazem clientes melhores ou mais arriscados?",
                    "Quais clientes de alto valor devem ser monitorados?",
                    "O risco é maior no início do relacionamento ou em clientes antigos?",
                ],
            }
        )

    # -------------------------------------------------------------------------
    # Formatação textual
    # -------------------------------------------------------------------------
    @staticmethod
    def _fmt_int(valor: int | float) -> str:
        return f"{int(valor):,}".replace(",", ".")

    @staticmethod
    def _fmt_pct(valor: float) -> str:
        return f"{valor:.2%}".replace(".", ",")

    @staticmethod
    def _fmt_moeda(valor: int | float) -> str:
        return f"US$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
