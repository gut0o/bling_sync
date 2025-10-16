# oauth_server.py — modo DEV (ignora validação de state para destravar)
import os
import webbrowser
import requests
import urllib.parse
import secrets
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer

load_dotenv()

CLIENT_ID = os.getenv("BLING_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")
REDIRECT_URI = os.getenv("BLING_REDIRECT_URI", "http://localhost:8000/callback")

AUTH_URL = "https://www.bling.com.br/Api/v3/oauth/authorize"
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"

# Gera um state (a validação estará desativada para DEV)
STATE = secrets.token_urlsafe(16)

def update_env(**kv):
    path = ".env"
    lines = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    kv = {k: str(v) for k, v in kv.items()}
    keys = set(kv.keys())
    new_lines, seen = [], set()
    for line in lines:
        if "=" in line:
            k = line.split("=", 1)[0].strip()
            if k in keys:
                new_lines.append(f"{k}={kv[k]}")
                seen.add(k)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    for k in keys - seen:
        new_lines.append(f"{k}={kv[k]}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

class Handler(BaseHTTPRequestHandler):
    def _send_text(self, text: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def log_message(self, fmt, *args):  # silencia logs chatos
        return

    def do_GET(self):
        if not self.path.startswith("/callback"):
            return self._send_text("OK")

        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        # Se o provedor mandou erro
        err = params.get("error", [None])[0]
        if err:
            desc = params.get("error_description", [""])[0]
            return self._send_text(f"Erro de autorização: {err} - {desc}", 400)

        # DEBUG do state (validação desativada no DEV)
        state_recv = params.get("state", [None])[0]
        print("\n STATE esperado:", STATE)
        print(" STATE recebido:", state_recv)
        # >>> intencionalmente NÃO bloqueia se for diferente (para DEV)

        code = params.get("code", [None])[0]
        if not code:
            return self._send_text("Faltou ?code= na URL.", 400)

        # Troca code por tokens (Basic Auth)
        form = {
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            resp = requests.post(
                TOKEN_URL,
                data=form,
                headers=headers,
                auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
                timeout=20,
            )
        except Exception as e:
            return self._send_text(f"Falha na requisição de token: {e}", 500)

        if not resp.ok:
            return self._send_text(f"Erro ao trocar code: {resp.text}", 500)

        tok = resp.json()
        access_token = tok.get("access_token", "")
        refresh_token = tok.get("refresh_token", "")

        update_env(
            BLING_ACCESS_TOKEN=access_token,
            BLING_REFRESH_TOKEN=refresh_token
        )

        self._send_text(" Autorizado! Tokens salvos no .env. Pode fechar esta aba.")
        print("\n Tokens obtidos e salvos no .env com sucesso!")
        if access_token:
            print("Access Token:", access_token[:24] + "...")
        if refresh_token:
            print("Refresh Token:", refresh_token[:24] + "...")
        os._exit(0)

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print(" Configure BLING_CLIENT_ID e BLING_CLIENT_SECRET no .env.")
        return
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": STATE,
    }
    url = f"{AUTH_URL}?" + urllib.parse.urlencode(params)
    print("\n Abra e autorize o app neste link:\n", url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    print("\nAguardando callback em http://localhost:8000/callback ...\n")
    HTTPServer(("localhost", 8000), Handler).serve_forever()

if __name__ == "__main__":
    main()
