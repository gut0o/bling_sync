# test_api_receber.py
import os, requests
from dotenv import load_dotenv
load_dotenv()

BASE="https://www.bling.com.br/Api/v3"
h={"Authorization": f"Bearer {os.getenv('BLING_ACCESS_TOKEN')}", "Accept":"application/json"}

for path in ("contas/pagar","contas/receber"):
    r = requests.get(f"{BASE}/{path}", headers=h, params={"page":1,"limit":5}, timeout=20)
    r.raise_for_status()
    js = r.json()
    print(path, "→", len(js.get("data", [])), "itens")
