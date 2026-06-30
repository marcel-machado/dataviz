from __future__ import annotations

import pandas as pd


COLUMN_LABELS = {
    "Customer ID": "ID do cliente",
    "Gender": "Gênero",
    "Age": "Idade",
    "Senior Citizen": "Idoso (65+)",
    "Under 30": "Menor de 30",
    "Married": "Casado",
    "Dependents": "Dependentes",
    "Number of Dependents": "Quantidade de dependentes",
    "Count": "Contagem",
    "Country": "País",
    "State": "Estado",
    "City": "Cidade",
    "Zip Code": "CEP",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "Population": "População",
    "Quarter": "Trimestre",
    "Referred a Friend": "Indicou um amigo",
    "Number of Referrals": "Quantidade de indicações",
    "Tenure in Months": "Tempo de permanência (meses)",
    "Offer": "Oferta",
    "Phone Service": "Serviço telefônico",
    "Avg Monthly Long Distance Charges": "Tarifa média mensal de longa distância",
    "Multiple Lines": "Múltiplas linhas",
    "Internet Service": "Serviço de internet",
    "Internet Type": "Tipo de internet",
    "Avg Monthly GB Download": "Download médio mensal (GB)",
    "Online Security": "Segurança online",
    "Online Backup": "Backup online",
    "Device Protection Plan": "Proteção de dispositivos",
    "Premium Tech Support": "Suporte técnico premium",
    "Streaming TV": "Streaming de TV",
    "Streaming Movies": "Streaming de filmes",
    "Streaming Music": "Streaming de música",
    "Unlimited Data": "Dados ilimitados",
    "Contract": "Contrato",
    "Paperless Billing": "Fatura digital",
    "Payment Method": "Método de pagamento",
    "Monthly Charge": "Cobrança mensal",
    "Total Charges": "Cobranças totais",
    "Total Refunds": "Reembolsos totais",
    "Total Extra Data Charges": "Cobranças extras de dados",
    "Total Long Distance Charges": "Cobranças totais de longa distância",
    "Total Revenue": "Receita total",
    "Satisfaction Score": "Nota de satisfação",
    "Satisfaction Score Label": "Rótulo de satisfação",
    "Customer Status": "Status do cliente",
    "Churn Label": "Cancelou?",
    "Churn Value": "Valor de cancelamento",
    "Churn Score": "Pontuação de cancelamento",
    "Churn Score Category": "Faixa da pontuação de cancelamento",
    "CLTV": "Valor de vida do cliente (CLTV)",
    "CLTV Category": "Faixa de CLTV",
    "Churn Category": "Categoria do cancelamento",
    "Churn Reason": "Motivo do cancelamento",
    "Taxa de churn (%)": "Taxa de cancelamento (%)",
    "Taxa geral de churn": "Taxa geral de cancelamento",
    "Taxa de churn dos aderentes (%)": "Taxa de cancelamento dos aderentes (%)",
    "Churn Score médio": "Pontuação de cancelamento média",
    "CLTV médio": "Valor de vida médio (CLTV)",
    "CLTV total previsto": "Valor de vida total previsto",
    "Churn Score": "Pontuação de cancelamento",
    "CLTV": "Valor de vida do cliente (CLTV)",
}


VALUE_LABELS = {
    "Yes": "Sim",
    "No": "Não",
    "Female": "Feminino",
    "Male": "Masculino",
    "Churned": "Cliente cancelou",
    "Stayed": "Cliente permaneceu",
    "Joined": "Novo cliente",
    "Month-to-Month": "Mês a mês",
    "One Year": "Um ano",
    "Two Year": "Dois anos",
    "Fiber Optic": "Fibra óptica",
    "Cable": "Cabo",
    "Bank Withdrawal": "Saque bancário",
    "Credit Card": "Cartão de crédito",
    "Mailed Check": "Cheque enviado",
    "Offer A": "Oferta A",
    "Offer B": "Oferta B",
    "Offer C": "Oferta C",
    "Offer D": "Oferta D",
    "Offer E": "Oferta E",
    "None": "Nenhum",
    "Attitude": "Atitude",
    "Competitor": "Concorrente",
    "Dissatisfaction": "Insatisfação",
    "Other": "Outro",
    "Price": "Preço",
    "Attitude of service provider": "Atitude do provedor de serviço",
    "Attitude of support person": "Atitude do atendente de suporte",
    "Competitor had better devices": "Concorrente tinha dispositivos melhores",
    "Competitor made better offer": "Concorrente fez oferta melhor",
    "Competitor offered higher download speeds": "Concorrente ofereceu velocidades maiores de download",
    "Competitor offered more data": "Concorrente ofereceu mais dados",
    "Deceased": "Falecimento",
    "Don't know": "Não sabe informar",
    "Extra data charges": "Cobranças extras de dados",
    "Lack of affordable download/upload speed": "Falta de velocidade de download/upload acessível",
    "Lack of self-service on Website": "Falta de autoatendimento no site",
    "Limited range of services": "Variedade limitada de serviços",
    "Long distance charges": "Cobranças de longa distância",
    "Moved": "Mudança de endereço",
    "Network reliability": "Confiabilidade da rede",
    "Poor expertise of online support": "Baixa qualificação do suporte online",
    "Poor expertise of phone support": "Baixa qualificação do suporte telefônico",
    "Price too high": "Preço muito alto",
    "Product dissatisfaction": "Insatisfação com produto",
    "Service dissatisfaction": "Insatisfação com serviço",
    "Customer ID": "ID do cliente",
    "Customer Status": "Status do cliente",
    "Contract": "Contrato",
    "Internet Type": "Tipo de internet",
    "Payment Method": "Método de pagamento",
    "Offer": "Oferta",
    "Satisfaction Score": "Nota de satisfação",
    "Senior Citizen": "Idoso (65+)",
    "Under 30": "Menor de 30",
    "Dependents": "Dependentes",
    "Married": "Casado",
    "Paperless Billing": "Fatura digital",
    "Premium Tech Support": "Suporte técnico premium",
    "Online Security": "Segurança online",
    "Online Backup": "Backup online",
    "Device Protection Plan": "Proteção de dispositivos",
    "Referred a Friend": "Indicou um amigo",
    "Phone Service": "Serviço telefônico",
    "Multiple Lines": "Múltiplas linhas",
    "Internet Service": "Serviço de internet",
    "Streaming TV": "Streaming de TV",
    "Streaming Movies": "Streaming de filmes",
    "Streaming Music": "Streaming de música",
    "Unlimited Data": "Dados ilimitados",
    "Monthly Charge": "Cobrança mensal",
    "Total Revenue": "Receita total",
    "Tenure in Months": "Tempo de permanência (meses)",
    "Churn Category": "Categoria do cancelamento",
    "Churn Reason": "Motivo do cancelamento",
}


def traduzir_coluna(coluna: object) -> str:
    texto = str(coluna)
    return COLUMN_LABELS.get(texto, VALUE_LABELS.get(texto, texto))


def traduzir_valor(valor: object) -> object:
    if pd.isna(valor):
        return valor
    texto = str(valor)
    return VALUE_LABELS.get(texto, COLUMN_LABELS.get(texto, texto))


def traduzir_serie(serie: pd.Series) -> pd.Series:
    return serie.map(traduzir_valor)


def traduzir_dataframe(tabela: pd.DataFrame) -> pd.DataFrame:
    if tabela is None or tabela.empty:
        return tabela

    traduzida = tabela.copy()
    for coluna in traduzida.columns:
        if (
            pd.api.types.is_object_dtype(traduzida[coluna])
            or pd.api.types.is_string_dtype(traduzida[coluna])
            or isinstance(traduzida[coluna].dtype, pd.CategoricalDtype)
        ):
            traduzida[coluna] = traduzida[coluna].map(traduzir_valor)

    traduzida = traduzida.rename(columns=traduzir_coluna)
    return traduzida
