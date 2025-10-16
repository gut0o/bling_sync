# bling_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BLING_API_KEY")            # v2 (chave antiga)
ACCESS_TOKEN = os.getenv("BLING_ACCESS_TOKEN")  # v3 (OAuth)
TIMEOUT = 20

def _raise_detail(resp):
    try:
        print("❌ Erro:", resp.status_code, resp.text[:600])
    except Exception:
        pass
    resp.raise_for_status()

# -----------------------------
# v2 (API Key, “chave” antiga)
# -----------------------------
V2_BASE = "https://bling.com.br/Api/v2"

def v2_get(path, params=None):
    params = params or {}
    if not API_KEY:
        raise RuntimeError("BLING_API_KEY não configurado para v2.")
    params["apikey"] = API_KEY
    # v2 precisa do sufixo /json para responder JSON
    if not path.endswith("/json"):
        path = f"{path}/json"
    url = f"{V2_BASE}/{path.lstrip('/')}"
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    if not resp.ok:
        _raise_detail(resp)
    return resp.json()

def v2_contas_receber(page=1, limite=100):
    # endpoints típicos v2: contasreceber / contaspagar
    return v2_get("contasreceber", {"pagina": page, "limite": limite})

def v2_contas_pagar(page=1, limite=100):
    return v2_get("contaspagar", {"pagina": page, "limite": limite})

# -----------------------------
# v3 (OAuth2 Bearer)
# -----------------------------
V3_BASE = "https://www.bling.com.br/Api/v3"

def v3_get(path, params=None):
    if not ACCESS_TOKEN:
        raise RuntimeError("BLING_ACCESS_TOKEN não configurado para v3.")
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Accept": "application/json"}
    url = f"{V3_BASE}/{path.lstrip('/')}"
    resp = requests.get(url, headers=headers, params=params or {}, timeout=TIMEOUT)
    if not resp.ok:
        _raise_detail(resp)
    return resp.json()

def v3_contas_receber(page=1, limit=100):
    return v3_get("contas/receber", {"page": page, "limit": limit})

def v3_contas_pagar(page=1, limit=100):
    return v3_get("contas/pagar", {"page": page, "limit": limit})

# -----------------------------
# Facades usados pelo resto do código
# -----------------------------
def get_contas_receber(page=1, limit=100):
    """
    Decide automaticamente: v2 (API Key) ou v3 (OAuth).
    Retorna um dicionário e deixa para o sync normalizar.
    """
    if API_KEY:
        return v2_contas_receber(page, limit)
    return v3_contas_receber(page, limit)

def get_contas_pagar(page=1, limit=100):
    if API_KEY:
        return v2_contas_pagar(page, limit)
    return v3_contas_pagar(page, limit)
