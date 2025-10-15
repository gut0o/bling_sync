# sync.py
from database import SessionLocal
from models import ContaPagar, ContaReceber
from bling_api import get_contas_pagar, get_contas_receber
from datetime import datetime

def _coerce_date(s):
    if not s:
        return None
    s = str(s).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        # v2 às vezes retorna 'dd/mm/aaaa' -> tenta parse simples
        try:
            d, m, y = s.split("/")
            return datetime(int(y), int(m), int(d))
        except Exception:
            return None

def _iter_itens(resp, tipo):  # tipo: "pagar" | "receber"
    """
    v3 costuma vir como {"data": [...]}
    v2 costuma vir como {"retorno": {"contaspagar":[{"contapagar":{...}}]}}
                               ou  {"contasreceber":[{"contareceber":{...}}]}
    """
    if not resp:
        return []
    # v3
    if isinstance(resp, dict) and "data" in resp and isinstance(resp["data"], list):
        for it in resp["data"]:
            yield it
        return
    # v2
    r = resp.get("retorno") if isinstance(resp, dict) else None
    if not isinstance(r, dict):
        return
    key_lista = "contaspagar" if tipo == "pagar" else "contasreceber"
    key_item  = "contapagar" if tipo == "pagar" else "contareceber"
    lista = r.get(key_lista) or []
    for wrapper in lista:
        it = wrapper.get(key_item) if isinstance(wrapper, dict) else None
        if it:
            yield it

def sync_contas_pagar():
    print("🔹 Buscando contas a pagar...")
    session = SessionLocal()
    resp = get_contas_pagar()
    novos = 0
    for item in _iter_itens(resp, "pagar"):
        _id = str(item.get("id") or item.get("numero") or item.get("idLancamento") or "")
        if not _id:
            continue
        conta = session.get(ContaPagar, _id)
        if not conta:
            conta = ContaPagar(
                id=_id,
                descricao=item.get("descricao") or item.get("historico"),
                valor=float(item.get("valor", 0) or item.get("valorTitulo", 0) or 0),
                vencimento=_coerce_date(item.get("dataVencimento") or item.get("dataVencimentoOriginal")),
                pagamento=_coerce_date(item.get("dataPagamento")),
                status=item.get("situacao") or item.get("situacaoTitulo"),
            )
            session.add(conta)
            novos += 1
    session.commit()
    session.close()
    print(f"✅ Contas a pagar sincronizadas (novos: {novos})")

def sync_contas_receber():
    print("🔹 Buscando contas a receber...")
    session = SessionLocal()
    resp = get_contas_receber()
    novos = 0
    for item in _iter_itens(resp, "receber"):
        _id = str(item.get("id") or item.get("numero") or item.get("idLancamento") or "")
        if not _id:
            continue
        conta = session.get(ContaReceber, _id)
        if not conta:
            conta = ContaReceber(
                id=_id,
                descricao=item.get("descricao") or item.get("historico"),
                valor=float(item.get("valor", 0) or item.get("valorTitulo", 0) or 0),
                vencimento=_coerce_date(item.get("dataVencimento") or item.get("dataVencimentoOriginal")),
                pagamento=_coerce_date(item.get("dataPagamento")),
                status=item.get("situacao") or item.get("situacaoTitulo"),
            )
            session.add(conta)
            novos += 1
    session.commit()
    session.close()
    print(f"✅ Contas a receber sincronizadas (novos: {novos})")

if __name__ == "__main__":
    sync_contas_pagar()
    sync_contas_receber()
    print("🎯 Sincronização concluída!")
