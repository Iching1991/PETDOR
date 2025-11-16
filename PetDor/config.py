"""
Configurações centralizadas do PET DOR
"""

import streamlit as st
from datetime import timedelta

# ===========================
# URL do aplicativo
# ===========================
# Se usar Streamlit Cloud, coloque a URL pública aqui ou no .streamlit/secrets.toml
APP_URL = st.secrets.get("APP_URL", "https://petdor.streamlit.app")

# ===========================
# Banco de dados
# ===========================
# Caminho do arquivo SQLite
DB_FILE = st.secrets.get("DB_PATH", "petdor.db")

# ===========================
# Segurança / Tokens
# ===========================
# Quantas horas o link de reset de senha fica válido
TOKEN_EXP_HOURS = int(st.secrets.get("TOKEN_EXP_HOURS", 1))
TOKEN_EXPIRATION = timedelta(hours=TOKEN_EXP_HOURS)

# Limite de solicitações de reset por dia (por usuário)
MAX_RESET_ATTEMPTS_PER_DAY = int(st.secrets.get("MAX_RESET_ATTEMPTS_PER_DAY", 3))

# Tamanho mínimo da senha
PASSWORD_MIN_LENGTH = int(st.secrets.get("PASSWORD_MIN_LENGTH", 6))

# ===========================
# E-mail (SMTP)
# ===========================
SMTP_CONFIG = {
    "server": st.secrets.get("SMTP_SERVER", "smtp.gmail.com"),
    "port": int(st.secrets.get("SMTP_PORT", 465)),
    "user": st.secrets.get("EMAIL_USER", ""),
    "password": st.secrets.get("EMAIL_PASS", "")
}

# ===========================
# Níveis de dor (percentuais)
# ===========================
# Estes níveis são usados em:
# - config.get_nivel_dor(percentual)
# - utils/pdf_generator.py para texto e cores
NIVEL_DOR_CONFIG = {
    "baixo": {
        "limite": 30.0,           # < 30%
        "cor": "#28a745",         # verde
        "texto": (
            "Baixa probabilidade de dor significativa. "
            "Continue monitorando o comportamento do animal, "
            "mantendo rotina e ambiente confortáveis."
        )
    },
    "moderado": {
        "limite": 60.0,           # >=30 e <60
        "cor": "#ffc107",         # amarelo
        "texto": (
            "Probabilidade moderada de dor. "
            "Recomenda-se observar com atenção nas próximas 24–48 horas "
            "e considerar avaliação veterinária, especialmente se os sinais persistirem."
        )
    },
    "alto": {
        "limite": 100.0,          # >=60
        "cor": "#dc3545",         # vermelho
        "texto": (
            "Alta probabilidade de dor. "
            "Recomenda-se avaliação veterinária o mais breve possível. "
            "Sinais de piora ou desconforto intenso exigem atendimento imediato."
        )
    }
}

def get_nivel_dor(percentual: float) -> dict:
    """
    Retorna um dicionário com as informações do nível de dor correspondente
    ao percentual informado.

    Usado em:
      - utils/pdf_generator.py
      - pages/avaliacao.py (para recomendação clínica)
    """
    try:
        p = float(percentual)
    except (TypeError, ValueError):
        p = 0.0

    if p < NIVEL_DOR_CONFIG["baixo"]["limite"]:
        return NIVEL_DOR_CONFIG["baixo"]
    elif p < NIVEL_DOR_CONFIG["moderado"]["limite"]:
        return NIVEL_DOR_CONFIG["moderado"]
    else:
        return NIVEL_DOR_CONFIG["alto"]
