from __future__ import annotations

import mimetypes
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from .config import ASSUNTO_EMAIL_PADRAO, EMPRESA_ANALISE, RESPONSAVEL_ANALISE

load_dotenv()


def _buscar_config(chave: str, padrao: str | None = None) -> str | None:
    """Busca credencial primeiro no Streamlit Secrets e depois no .env/ambiente."""
    try:
        valor = st.secrets.get(chave)
        if valor:
            return str(valor)
    except Exception:
        pass
    return os.getenv(chave, padrao)


class EmailSender:
    """Classe para envio de e-mail via SMTP com anexo opcional."""

    def __init__(self):
        self.remetente = _buscar_config("EMAIL_REMETENTE")
        self.senha = _buscar_config("SENHA_EMAIL")
        self.smtp_host = _buscar_config("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(_buscar_config("SMTP_PORT", "465") or 465)
        self.destinatario_padrao = _buscar_config("EMAIL_DESTINO_PADRAO", "")

    def credenciais_configuradas(self) -> bool:
        return bool(self.remetente and self.senha and self.smtp_host and self.smtp_port)

    def enviar_email(
        self,
        destinatario: str,
        corpo: str,
        anexos: list[str | Path] | None = None,
        assunto: str = ASSUNTO_EMAIL_PADRAO,
    ) -> None:
        if not self.credenciais_configuradas():
            raise ValueError(
                "Credenciais de e-mail ausentes. Configure EMAIL_REMETENTE e SENHA_EMAIL em .env ou no Secrets do Streamlit Cloud."
            )

        mensagem = MIMEMultipart()
        mensagem["From"] = self.remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto
        mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

        for anexo in anexos or []:
            self._adicionar_anexo(mensagem, Path(anexo))

        contexto = ssl.create_default_context()
        if self.smtp_port == 465:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=contexto) as servidor:
                servidor.login(self.remetente, self.senha)
                servidor.send_message(mensagem)
        else:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as servidor:
                servidor.starttls(context=contexto)
                servidor.login(self.remetente, self.senha)
                servidor.send_message(mensagem)

    @staticmethod
    def _adicionar_anexo(mensagem: MIMEMultipart, caminho: Path) -> None:
        if not caminho.exists():
            raise FileNotFoundError(f"Anexo não encontrado: {caminho}")

        tipo_mime, _ = mimetypes.guess_type(str(caminho))
        if tipo_mime is None:
            tipo_mime = "application/octet-stream"
        tipo_principal, subtipo = tipo_mime.split("/", 1)

        with open(caminho, "rb") as arquivo:
            parte = MIMEBase(tipo_principal, subtipo)
            parte.set_payload(arquivo.read())

        encoders.encode_base64(parte)
        parte.add_header("Content-Disposition", f'attachment; filename="{caminho.name}"')
        mensagem.attach(parte)


def _saudacao_email(nome_usuario: str = "") -> str:
    nome = nome_usuario.strip()
    if nome:
        return f"Olá, {nome},\n\n"
    return "Olá,\n\n"


def _assinatura_email() -> str:
    return f"\n\nAtenciosamente,\n{RESPONSAVEL_ANALISE},\n{EMPRESA_ANALISE}"


def corpo_email_grafico(nome_grafico: str, nome_usuario: str = "") -> str:
    return "".join(
        [
            _saudacao_email(nome_usuario),
            f"Segue em anexo o gráfico estático solicitado: {nome_grafico}.\n",
            "Este material faz parte da análise de cancelamento de clientes e indicadores empresariais da base Telco.",
            _assinatura_email(),
        ]
    )


def corpo_email_relatorio(nome_usuario: str = "") -> str:
    return "".join(
        [
            _saudacao_email(nome_usuario),
            "Segue em anexo o relatório executivo com os principais insights e recomendações sobre cancelamentos, receita, carteira de clientes, serviços e oportunidades de retenção.\n",
            "O relatório apresenta uma análise geral dos dados, não uma análise isolada por gráfico.",
            _assinatura_email(),
        ]
    )
