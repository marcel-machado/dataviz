from pathlib import Path
import tempfile

import matplotlib.pyplot as plt
import streamlit as st

from src.charts import GraficosChurn, STATIC_CHARTS
from src.config import ASSUNTO_EMAIL_PADRAO
from src.data_loader import carregar_dados
from src.email_sender import EmailSender, corpo_email_grafico, corpo_email_relatorio
from src.report import gerar_relatorio_texto
from src.ui import configurar_pagina, insight_panel, page_header, saudacao, section_title, sidebar_usuario

configurar_pagina("Enviar por E-mail", "📧")
sidebar_usuario()
saudacao()

page_header(
    "Envio de análise por e-mail",
    "Selecione um gráfico estático em PNG ou o relatório escrito e envie com assunto e corpo padronizados.",
)

df = carregar_dados()
graficos = GraficosChurn(df)
email_sender = EmailSender()
nome_usuario = st.session_state.get("nome_usuario", "")

if not email_sender.credenciais_configuradas():
    st.warning(
        "As credenciais de e-mail ainda não estão configuradas. Para usar esta página no Streamlit Cloud, cadastre EMAIL_REMETENTE, SENHA_EMAIL, SMTP_HOST e SMTP_PORT em Secrets."
    )

insight_panel(f"<strong>Assunto padronizado:</strong> {ASSUNTO_EMAIL_PADRAO}")

section_title("Dados do envio")
destinatario = st.text_input(
    "E-mail do destinatário",
    value=email_sender.destinatario_padrao or "",
    placeholder="usuario@empresa.com",
)
tipo_envio = st.radio("O que deseja enviar?", ["Gráfico estático", "Relatório escrito"], horizontal=True)

anexos = []
corpo = ""
preview = None
nome_grafico = None

if tipo_envio == "Gráfico estático":
    section_title("Prévia do gráfico")
    nome_grafico = st.selectbox("Escolha o gráfico a enviar", list(STATIC_CHARTS.keys()))
    metodo = getattr(graficos, STATIC_CHARTS[nome_grafico])
    fig = metodo()
    st.pyplot(fig, width="stretch")
    preview = fig
    corpo = corpo_email_grafico(nome_grafico, nome_usuario)
else:
    section_title("Prévia do relatório")
    relatorio = gerar_relatorio_texto(df, st.session_state.get("nome_usuario", ""))
    st.text_area("Prévia do relatório", value=relatorio, height=500)
    corpo = corpo_email_relatorio(nome_usuario)

section_title("Corpo do e-mail")
st.text_area("Mensagem", value=corpo, height=180, disabled=True)

if st.button("Enviar e-mail", type="primary"):
    if not destinatario:
        st.error("Informe o e-mail do destinatário.")
    else:
        try:
            with st.spinner("Preparando e enviando o e-mail..."):
                arquivos_temporarios: list[Path] = []

                if tipo_envio == "Gráfico estático":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        caminho = Path(tmp.name)
                    preview.savefig(caminho, dpi=160, bbox_inches="tight")
                    arquivos_temporarios.append(caminho)
                    anexos = [caminho]
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                        tmp.write(gerar_relatorio_texto(df, st.session_state.get("nome_usuario", "")))
                        caminho = Path(tmp.name)
                    arquivos_temporarios.append(caminho)
                    anexos = [caminho]

                email_sender.enviar_email(destinatario=destinatario, corpo=corpo, anexos=anexos)

                for arquivo in arquivos_temporarios:
                    try:
                        arquivo.unlink(missing_ok=True)
                    except Exception:
                        pass

            st.success("E-mail enviado com sucesso.")
        except Exception as erro:
            st.error(f"Não foi possível enviar o e-mail: {erro}")

if preview is not None:
    plt.close(preview)
