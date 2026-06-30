from datetime import datetime
import streamlit as st

from src.data_loader import carregar_dados
from src.report import gerar_relatorio_texto
from src.ui import configurar_pagina, page_header, saudacao, section_title, sidebar_usuario

configurar_pagina("Download", "⬇️")
sidebar_usuario()
saudacao()

page_header(
    "Download do relatório em texto",
    "Prévia do relatório executivo e botão de download em arquivo .txt, conforme solicitado no projeto.",
)

df = carregar_dados()
relatorio = gerar_relatorio_texto(df, st.session_state.get("nome_usuario", ""))

section_title("Prévia do arquivo .txt")
st.text_area("Prévia do arquivo .txt", value=relatorio, height=650)

nome_arquivo = f"relatorio_telco_cancelamentos_{datetime.now().strftime('%Y%m%d')}.txt"
st.download_button(
    label="Baixar relatório .txt",
    data=relatorio.encode("utf-8"),
    file_name=nome_arquivo,
    mime="text/plain",
    type="primary",
)
