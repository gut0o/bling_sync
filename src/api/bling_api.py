# src/api/bling_api.py
import os, requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

# --- carregar .env de forma robusta ---
dotenv_path = find_dotenv()
if not dotenv_path:
    dotenv_path = Path(__file__).resolve().parents[2] / ".env"  # raiz do projeto
load_dotenv(dotenv_path)

def _save_env(kv: dict):
    """Atualiza/insere chaves no .env da raiz."""
    p = Path(dotenv_path)
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    m = {k: str(v) for k, v in kv.items()}
    new = []
    seen = set()
    for line in lines:
        if "=" in line:
            k = line.split("=", 1)[0].strip()
            if k in m:
                new.append(f"{k}={m[k]}"); seen.add(k)
            else:
                new.append(line)
        else:
            new.append(line)
    for k, v in m.items():
        if k not in seen:
            new.append(f"{k}={v}")
    p.write_text("\n".join(new) + "\n", encoding="utf-8")

# --------- Configs comuns ---------
TIMEOUT = 20

# v2 (chave antiga)
API_KEY = os.getenv("BLING_API_KEY")
V2_BASE = "https://bling.com.br/Api/v2"

# v3 (OAuth2)
V3_BASE = "https://www.bling.com.br/Api/v3"
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"

CLIENT_ID = os.getenv("BLING_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("BLING_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("BLING_REFRESH_TOKEN")

_token_exp = None  # expiração em memória (opcional)

def _raise_detail(resp):
    try:
        print(" Erro:", resp.status_code, resp.text[:600])
    except Exception:
        pass
    resp.raise_for_status()

# --------- v2 ---------
def v2_get(path, params=None):
    params = params or {}
    if not API_KEY:
        raise RuntimeError("BLING_API_KEY não configurado para v2.")
    params["apikey"] = API_KEY
    if not path.endswith("/json"):
        path = f"{path}/json"
    url = f"{V2_BASE}/{path.lstrip('/')}"
    r = requests.get(url, params=params, timeout=TIMEOUT)
    if not r.ok:
        _raise_detail(r)
    return r.json()

def v2_contas_receber(page=1, limite=100):
    return v2_get("contasreceber", {"pagina": page, "limite": limite})

def v2_contas_pagar(page=1, limite=100):
    return v2_get("contaspagar", {"pagina": page, "limite": limite})

# --- troque APENAS esta função no src/api/bling_api.py ---

def _refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN, _token_exp
    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
        raise RuntimeError(
            "Faltam variáveis no .env: defina BLING_CLIENT_ID, BLING_CLIENT_SECRET e BLING_REFRESH_TOKEN."
        )

    # OAuth2 refresh_token com client_id/client_secret via HTTP Basic
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }
    headers = {"Accept": "application/json"}
    # 'auth=(user, pass)' envia Authorization: Basic base64(client_id:client_secret)
    r = requests.post(
        TOKEN_URL,
        data=data,
        headers=headers,
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=TIMEOUT,
    )

    if not r.ok:
        _raise_detail(r)  # imprime detalhe e levanta HTTPError

    jd = r.json()
    ACCESS_TOKEN = jd.get("access_token")
    # alguns providers retornam novo refresh_token; se não vier, mantemos o atual
    REFRESH_TOKEN = jd.get("refresh_token") or REFRESH_TOKEN
    expires_in = int(jd.get("expires_in", 3000))
    _token_exp = datetime.utcnow() + timedelta(seconds=expires_in - 30)

    # persiste tokens no .env
    _save_env({
        "BLING_ACCESS_TOKEN": ACCESS_TOKEN or "",
        "BLING_REFRESH_TOKEN": REFRESH_TOKEN or "",
    })

    # persiste no .env
    _save_env({"BLING_ACCESS_TOKEN": ACCESS_TOKEN or "", "BLING_REFRESH_TOKEN": REFRESH_TOKEN or ""})

def _bearer_headers():
    if not ACCESS_TOKEN:
        _refresh_access_token()
    return {"Authorization": f"Bearer {ACCESS_TOKEN}", "Accept": "application/json"}

def v3_get(path, params=None):
    if not ACCESS_TOKEN:
        _refresh_access_token()
    url = f"{V3_BASE}/{path.lstrip('/')}"
    headers = _bearer_headers()
    r = requests.get(url, headers=headers, params=params or {}, timeout=TIMEOUT)
    if r.status_code == 401:
        # token expirado -> refresh e tenta 1x
        _refresh_access_token()
        headers = _bearer_headers()
        r = requests.get(url, headers=headers, params=params or {}, timeout=TIMEOUT)
    if not r.ok:
        _raise_detail(r)
    return r.json()

def v3_contas_receber(page=1, limit=100):
    return v3_get("contas/receber", {"page": page, "limit": limit})

def v3_contas_pagar(page=1, limit=100):
    return v3_get("contas/pagar", {"page": page, "limit": limit})

# --------- Facades ---------
def get_contas_receber(page=1, limit=100):
    # Se houver API_KEY, usa v2; senão v3.
    if API_KEY:
        return v2_contas_receber(page, limit)
    return v3_contas_receber(page, limit)

def get_contas_pagar(page=1, limit=100):
    if API_KEY:
        return v2_contas_pagar(page, limit)
    return v3_contas_pagar(page, limit)
