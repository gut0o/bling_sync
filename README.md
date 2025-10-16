#  Integração Financeira com Bling (MVP)

Este projeto sincroniza **Contas a Pagar** e **Contas a Receber** do Bling ERP usando a **API v3 (OAuth2)**  
e armazena localmente em um banco SQLite (`bling.db`).

---

##  Funcionalidades
- Autenticação via OAuth2 (Bling API v3)
- Sincronização automática (`sync.py` / `scheduler.py`)
- Armazenamento local e deduplicação
- Relatórios financeiros simples (`report.py`)

---

##  Como rodar
1. Configure o `.env` com suas credenciais:
 BLING_CLIENT_ID=...
BLING_CLIENT_SECRET=...
BLING_REDIRECT_URI=http://localhost:8000/callback

BLING_ACCESS_TOKEN=...
BLING_REFRESH_TOKEN=...

2. Execute a primeira sincronização:
```bash
python sync.py

