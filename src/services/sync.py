# sync.py
import sys, time
from typing import Iterable, Dict, Any, List
from db import migrate, upsert_conta
import bling_api

def _iter_paginated(fetch_fn, page_size=100) -> Iterable[List[Dict[str, Any]]]:
    """
    fetch_fn(page, limit) -> dict/json do Bling v3.
    Tenta suportar formatos mais comuns: {data: [...]} e/ou paginação por 'page'.
    Para MVP: incrementa page até vir lista vazia.
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
            # fallback: se o payload já for lista
            if isinstance(payload, list):
                data = payload
            else:
                data = []
        if not data:
            break
        yield data
        page += 1

def sync_contas_pagar() -> Dict[str, int]:
    novos = 0
    atualizados = 0
    vistos = 0

    for batch in _iter_paginated(bling_api.get_contas_pagar, page_size=100):
        for item in batch:
            # upsert — se já existia, conta como atualizado; senão, novo
            # Como o SQLite não retorna changedRows facilmente, vamos estimar:
            # primeiro tentamos inserir; se conflitar, é update — mas nosso helper já faz isso direto.
            # Aqui só contamos “vistos”; ao final, diferença entre vistos e “novos” não é confiável sem SELECT prévio.
            upsert_conta("contas_pagar", item)
            vistos += 1
    return {"vistos": vistos}

def sync_contas_receber() -> Dict[str, int]:
    novos = 0
    atualizados = 0
    vistos = 0

    for batch in _iter_paginated(bling_api.get_contas_receber, page_size=100):
        for item in batch:
            upsert_conta("contas_receber", item)
            vistos += 1
    return {"vistos": vistos}

def main():
    print(" Preparando banco...")
    migrate()

    print("🔹 Buscando contas a pagar...")
    r1 = {}
    try:
        r1 = sync_contas_pagar()
        print(f" Contas a pagar sincronizadas (itens processados: {r1.get('vistos', 0)})")
    except Exception as e:
        print(" Erro ao sincronizar contas a pagar:", e)
        raise

    print("🔹 Buscando contas a receber...")
    r2 = {}
    try:
        r2 = sync_contas_receber()
        print(f" Contas a receber sincronizadas (itens processados: {r2.get('vistos', 0)})")
    except Exception as e:
        print(" Erro ao sincronizar contas a receber:", e)
        raise

    print(" Sincronização concluída!")

if __name__ == "__main__":
    main()
