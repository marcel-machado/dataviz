from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st
from .config import DATA_PATH


NUMERIC_COLUMNS = [
    "Age",
    "Number of Dependents",
    "Population",
    "Number of Referrals",
    "Tenure in Months",
    "Avg Monthly Long Distance Charges",
    "Avg Monthly GB Download",
    "Monthly Charge",
    "Total Charges",
    "Total Refunds",
    "Total Extra Data Charges",
    "Total Long Distance Charges",
    "Total Revenue",
    "Satisfaction Score",
    "Churn Score",
    "CLTV",
]


@st.cache_data(show_spinner=False)
def carregar_dados(caminho: str | Path = DATA_PATH) -> pd.DataFrame:
    """Carrega e padroniza o dataset Telco.

    A função fica em cache para evitar recarregamento a cada interação no Streamlit.
    """
    df = pd.read_csv(caminho)
    df = padronizar_dados(df)
    return df


def padronizar_dados(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Churn Value" not in df.columns and "Churn Label" in df.columns:
        df["Churn Value"] = df["Churn Label"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)

    if "Churn Label" not in df.columns and "Churn Value" in df.columns:
        df["Churn Label"] = df["Churn Value"].map({1: "Yes", 0: "No"})

    # Colunas textuais usadas em filtros/relatórios: manter ausências legíveis.
    for col in ["Offer", "Internet Type", "Churn Category", "Churn Reason"]:
        if col in df.columns:
            if col in ["Churn Category", "Churn Reason"]:
                df[col] = df[col].fillna("Não se aplica")
            else:
                df[col] = df[col].fillna("Não informado")

    return df


def filtrar_dados(
    df: pd.DataFrame,
    status: list[str] | None = None,
    contrato: list[str] | None = None,
    internet: list[str] | None = None,
    churn_label: list[str] | None = None,
) -> pd.DataFrame:
    """Aplica filtros escolhidos pelo usuário mantendo a tabela estática."""
    filtrado = df.copy()
    if status and "Customer Status" in filtrado.columns:
        filtrado = filtrado[filtrado["Customer Status"].isin(status)]
    if contrato and "Contract" in filtrado.columns:
        filtrado = filtrado[filtrado["Contract"].isin(contrato)]
    if internet and "Internet Type" in filtrado.columns:
        filtrado = filtrado[filtrado["Internet Type"].isin(internet)]
    if churn_label and "Churn Label" in filtrado.columns:
        filtrado = filtrado[filtrado["Churn Label"].isin(churn_label)]
    return filtrado
