from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st
from PIL import Image

from .config import APP_TITLE, BRAND_ICON, BRAND_LOGO_DARK, BRAND_LOGO_FULL, EMPRESA_ANALISE
from .translations import traduzir_dataframe


def configurar_pagina(titulo: str, icone: str = "📊") -> None:
    st.set_page_config(
        page_title=f"{titulo} | {APP_TITLE}",
        page_icon=_page_icon(icone),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    aplicar_estilo()


def _page_icon(fallback: str):
    try:
        if BRAND_ICON.exists():
            return Image.open(BRAND_ICON)
    except Exception:
        pass
    return fallback


def aplicar_estilo() -> None:
    """Aplica uma camada visual comum a todas as páginas."""
    st.markdown(
        """
        <style>
            :root {
                --bg: #f3f7fc;
                --surface: #ffffff;
                --surface-soft: #eaf3fb;
                --text: #0e234b;
                --muted: #596779;
                --line: #d7e2ef;
                --brand-navy: #0e234b;
                --brand-blue: #0f5dab;
                --brand-sky: #2f93d1;
                --brand-ice: #dceeff;
                --risk: #d8583a;
                --warning: #f2b84b;
            }

            .stApp {
                background: var(--bg);
                color: var(--text);
            }

            [data-testid="stAppViewContainer"] > .main .block-container {
                max-width: 1420px;
                padding-top: 1.35rem;
                padding-bottom: 3rem;
            }

            [data-testid="stSidebar"] {
                background: #0e234b;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] * {
                color: #f5fbfc;
            }

            [data-testid="stSidebar"] input {
                color: #0e234b !important;
                background: #ffffff !important;
                border: 1px solid #b9cbe0 !important;
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: rgba(245, 251, 252, 0.75);
            }

            .page-header {
                background: linear-gradient(135deg, #ffffff 0%, #edf6ff 58%, #dceeff 100%);
                border: 1px solid var(--line);
                border-left: 6px solid var(--brand-blue);
                border-radius: 10px;
                padding: 1.4rem 1.55rem;
                margin: 0 0 1.25rem 0;
            }

            .page-eyebrow {
                color: var(--brand-blue);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }

            .page-header h1 {
                color: var(--text);
                font-size: 2rem;
                line-height: 1.15;
                margin: 0 0 0.4rem 0;
                font-weight: 800;
                letter-spacing: 0;
            }

            .page-header p {
                color: #41536a;
                font-size: 1rem;
                line-height: 1.55;
                margin: 0;
                max-width: 980px;
            }

            .section-title {
                margin-top: 1.2rem;
                margin-bottom: 0.35rem;
                color: var(--text);
                font-size: 1.1rem;
                font-weight: 800;
                letter-spacing: 0;
            }

            .section-note {
                color: var(--muted);
                font-size: 0.94rem;
                line-height: 1.5;
                margin-bottom: 0.75rem;
            }

            .user-greeting {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                background: #ffffff;
                border: 1px solid var(--line);
                border-left: 5px solid var(--warning);
                border-radius: 8px;
                color: var(--text);
                font-size: 0.96rem;
                font-weight: 700;
                padding: 0.55rem 0.75rem;
                margin: 0 0 0.85rem 0;
                box-shadow: 0 8px 18px rgba(23, 32, 38, 0.05);
            }

            .insight-panel {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 10px;
                padding: 1rem 1.1rem;
                margin: 0.65rem 0 1rem 0;
            }

            .insight-panel strong {
                color: var(--brand-blue);
            }

            [data-testid="metric-container"] {
                background: #ffffff;
                border: 1px solid var(--line);
                border-left: 5px solid var(--brand-blue);
                border-radius: 10px;
                padding: 0.9rem 1rem;
                box-shadow: 0 10px 24px rgba(23, 32, 38, 0.06);
            }

            [data-testid="metric-container"] label,
            [data-testid="metric-container"] [data-testid="stMetricLabel"] {
                color: var(--muted) !important;
                font-weight: 700;
            }

            [data-testid="metric-container"] [data-testid="stMetricValue"] {
                color: var(--text);
                font-weight: 800;
            }

            div[data-baseweb="tab-list"] {
                gap: 0.35rem;
                border-bottom: 1px solid var(--line);
            }

            button[data-baseweb="tab"] {
                background: transparent;
                border-radius: 8px 8px 0 0;
                padding: 0.7rem 0.9rem;
            }

            button[data-baseweb="tab"][aria-selected="true"] {
                background: #ffffff;
                border: 1px solid var(--line);
                border-bottom: 2px solid #ffffff;
            }

            div[data-testid="stExpander"] {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 10px;
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 8px;
                font-weight: 700;
                border: 1px solid var(--brand-blue);
            }

            .stButton > button[kind="primary"],
            .stDownloadButton > button[kind="primary"] {
                background: var(--brand-blue);
                border-color: var(--brand-blue);
            }

            [data-testid="stTable"] {
                background: #ffffff;
                border: 1px solid var(--line);
                border-radius: 10px;
                overflow: hidden;
            }

            [data-testid="stTable"] table {
                font-size: 0.92rem;
            }

            [data-testid="stTable"] th {
                background: #eaf3fb !important;
                color: #0e234b !important;
                font-weight: 800 !important;
            }

            [data-testid="stAlert"] {
                border-radius: 10px;
            }

            .block-container hr {
                margin: 1.25rem 0;
                border-color: var(--line);
            }

            @media (max-width: 760px) {
                [data-testid="stAppViewContainer"] > .main .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }

                .page-header {
                    padding: 1rem;
                }

                .page-header h1 {
                    font-size: 1.45rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_usuario() -> str:
    if BRAND_LOGO_DARK.exists():
        st.sidebar.image(str(BRAND_LOGO_DARK), width="stretch")
    else:
        st.sidebar.title(APP_TITLE)
    st.sidebar.caption("Navegue pelas páginas do relatório no menu acima.")
    st.sidebar.divider()
    st.sidebar.subheader("Sessão")

    if "nome_usuario_input" not in st.session_state:
        st.session_state["nome_usuario_input"] = st.session_state.get("nome_usuario", "")

    nome_digitado = st.sidebar.text_input("Seu nome", key="nome_usuario_input", placeholder="Digite seu nome")
    nome = nome_digitado.strip()
    st.session_state["nome_usuario"] = nome

    st.sidebar.caption("O nome fica salvo na sessão e aparece nas páginas internas.")
    st.sidebar.divider()
    st.sidebar.caption(f"Análise apresentada por {EMPRESA_ANALISE}.")
    return nome


def saudacao() -> None:
    nome = st.session_state.get("nome_usuario", "").strip()
    if nome:
        texto = f"Olá {nome}."
    else:
        texto = "Olá. Digite seu nome na barra lateral para personalizar esta sessão."
    st.markdown(f'<div class="user-greeting">{escape(texto)}</div>', unsafe_allow_html=True)


def card_metrica(coluna, titulo: str, valor: str, ajuda: str | None = None) -> None:
    coluna.metric(titulo, valor, help=ajuda)


def page_header(titulo: str, descricao: str, etiqueta: str = EMPRESA_ANALISE) -> None:
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-eyebrow">{escape(etiqueta)}</div>
            <h1>{escape(titulo)}</h1>
            <p>{escape(descricao)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def brand_showcase() -> None:
    if BRAND_LOGO_FULL.exists():
        left, center, right = st.columns([0.12, 0.76, 0.12])
        with center:
            st.image(str(BRAND_LOGO_FULL), width="stretch")


def section_title(titulo: str, descricao: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{escape(titulo)}</div>', unsafe_allow_html=True)
    if descricao:
        st.markdown(f'<div class="section-note">{escape(descricao)}</div>', unsafe_allow_html=True)


def insight_panel(texto: str) -> None:
    st.markdown(f'<div class="insight-panel">{texto}</div>', unsafe_allow_html=True)


def metricas(linhas: list[tuple[str, str, str | None]]) -> None:
    cols = st.columns(len(linhas))
    for col, (titulo, valor, ajuda) in zip(cols, linhas):
        col.metric(titulo, valor, help=ajuda)


def tabela_estatica(tabela: pd.DataFrame | dict) -> None:
    if isinstance(tabela, pd.DataFrame):
        st.table(traduzir_dataframe(tabela))
    else:
        st.table(tabela)
