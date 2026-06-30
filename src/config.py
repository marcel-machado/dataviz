from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "telco.csv"
BRAND_DIR = BASE_DIR / "assets" / "brand"
BRAND_LOGO_FULL = BRAND_DIR / "dataprime_logo_full.png"
BRAND_LOGO_DARK = BRAND_DIR / "dataprime_logo_dark.png"
BRAND_LOGO_BLUE = BRAND_DIR / "dataprime_logo_blue.png"
BRAND_SYMBOL = BRAND_DIR / "dataprime_symbol.png"
BRAND_WORDMARK = BRAND_DIR / "dataprime_wordmark.png"
BRAND_ICON = BRAND_DIR / "dataprime_icon.png"

APP_TITLE = "Análise Telco de Cancelamentos"
EMPRESA_ANALISE = "DataPrime Consultoria"
RESPONSAVEL_ANALISE = "Marcel Machado"
ASSUNTO_EMAIL_PADRAO = "Relatório Telco - DataPrime Consultoria"
