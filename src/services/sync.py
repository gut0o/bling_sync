# src/services/sync.py
from typing import Iterable, Dict, Any, List

# database: tenta raiz (database.py) ou dentro de src
try:
    from database import migrate, upsert_conta  # raiz do projeto
except ImportError:
    from src.database import migrate, upsert_conta  # fallback se você mover para src/

# bling_api: tenta em src/api, depois em api/, depois na raiz
try:
    from src.api.bling_api import get_contas_pagar, get_contas_receber
except ImportError:
    try:
        from api.bling_api import get_contas_pagar, get_contas_receber
    except ImportError:
        from bling_api import get_contas_pagar, get_contas_receber


def _iter_paginated(fetch_fn, page_size=100) -> Iterable[List[Dict[str, Any]]]:
    """
    fetch_fn(page, limit) -> dict/json do Bling v3.
    Suporta os formatos: {data: [...]} ou {items: [...]} ou lista pura.
    """
    page = 1
    while True:
        payload = fetch_fn(page=page, limit=page_size)
        data = None

        if isinstance(payload, dict):
            if isinstance(payload.get("data"), list):
                data = payload["data"]
            elif isinstance(payload.get("items"), list):
                data = payload["items"]

        if data is None:
            data = payload if isinstance(payload, list) else []

        if not data:
            break

        yield data
        page += 1


def sync_contas_pagar() -> Dict[str, int]:
    vistos = 0
    for batch in _iter_paginated(get_contas_pagar, page_size=100):
        for item in batch:
            upsert_conta("contas_pagar", item)
            vistos += 1
    return {"vistos": vistos}


def sync_contas_receber() -> Dict[str, int]:
    vistos = 0
    for batch in _iter_paginated(get_contas_receber, page_size=100):
        for item in batch:
            upsert_conta("contas_receber", item)
            vistos += 1
    return {"vistos": vistos}


def main():
    print(" Preparando banco...")
    migrate()

    print(" Buscando contas a pagar...")
    try:
        r1 = sync_contas_pagar()
        print(f" Contas a pagar sincronizadas (itens processados: {r1.get('vistos', 0)})")
    except Exception as e:
        print(" Erro ao sincronizar contas a pagar:", e)
        raise

    print(" Buscando contas a receber...")
    try:
        r2 = sync_contas_receber()
        print(f" Contas a receber sincronizadas (itens processados: {r2.get('vistos', 0)})")
    except Exception as e:
        print(" Erro ao sincronizar contas a receber:", e)
        raise

    print(" Sincronização concluída!")


if __name__ == "__main__":
    main()
