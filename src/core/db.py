# db.py
import sqlite3, json, os
from pathlib import Path

DB_PATH = os.getenv("BLING_DB_PATH", "bling.db")

def _conn():
    return sqlite3.connect(DB_PATH)

def migrate():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = _conn()
    cur = con.cursor()

    # Tabela base (pagar)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contas_pagar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_bling TEXT UNIQUE,
        numero_documento TEXT,
        descricao TEXT,
        categoria TEXT,
        contato_id TEXT,
        contato_nome TEXT,
        valor REAL,
        data_emissao TEXT,
        data_vencimento TEXT,
        data_pagamento TEXT,
        situacao TEXT,     -- Ex.: ABERTA/BAIXADA
        status TEXT,       -- se existir no payload
        raw_json TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )
    """)

    # Tabela base (receber)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contas_receber (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_bling TEXT UNIQUE,
        numero_documento TEXT,
        descricao TEXT,
        categoria TEXT,
        contato_id TEXT,
        contato_nome TEXT,
        valor REAL,
        data_emissao TEXT,
        data_vencimento TEXT,
        data_pagamento TEXT,
        situacao TEXT,
        status TEXT,
        raw_json TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )
    """)

    # Índices úteis para consultas
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pagar_venc ON contas_pagar(data_vencimento)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_receber_venc ON contas_receber(data_vencimento)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pagar_sit ON contas_pagar(situacao)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_receber_sit ON contas_receber(situacao)")

    con.commit(); con.close()

def _extract(item: dict):
    """Mapeia campos comuns independentemente de pequenas variações do payload."""
    contato = item.get("contato") or {}
    return {
        "id_bling": str(item.get("id") or item.get("numero") or ""),
        "numero_documento": item.get("numeroDocumento") or item.get("numero") or "",
        "descricao": item.get("descricao") or item.get("historico") or "",
        "categoria": (item.get("categoria") or {}).get("descricao") if isinstance(item.get("categoria"), dict) else item.get("categoria") or "",
        "contato_id": str(contato.get("id") or ""),
        "contato_nome": contato.get("nome") or "",
        "valor": float(item.get("valor") or 0),
        "data_emissao": item.get("dataEmissao") or item.get("data") or "",
        "data_vencimento": item.get("dataVencimento") or "",
        "data_pagamento": item.get("dataPagamento") or "",
        "situacao": item.get("situacao") or item.get("situacaoTitulo") or "",
        "status": item.get("status") or "",
        "raw_json": json.dumps(item, ensure_ascii=False),
    }

def upsert_conta(tabela: str, item: dict):
    data = _extract(item)
    q = f"""
    INSERT INTO {tabela} (
        id_bling, numero_documento, descricao, categoria, contato_id, contato_nome,
        valor, data_emissao, data_vencimento, data_pagamento, situacao, status, raw_json, updated_at
    ) VALUES (
        :id_bling, :numero_documento, :descricao, :categoria, :contato_id, :contato_nome,
        :valor, :data_emissao, :data_vencimento, :data_pagamento, :situacao, :status, :raw_json, datetime('now')
    )
    ON CONFLICT(id_bling) DO UPDATE SET
        numero_documento=excluded.numero_documento,
        descricao=excluded.descricao,
        categoria=excluded.categoria,
        contato_id=excluded.contato_id,
        contato_nome=excluded.contato_nome,
        valor=excluded.valor,
        data_emissao=excluded.data_emissao,
        data_vencimento=excluded.data_vencimento,
        data_pagamento=excluded.data_pagamento,
        situacao=excluded.situacao,
        status=excluded.status,
        raw_json=excluded.raw_json,
        updated_at=datetime('now')
    """
    con = _conn()
    con.execute(q, data)
    con.commit()
    con.close()
