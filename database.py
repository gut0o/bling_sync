# database.py — versão SQLite pura (sem SQLAlchemy, sem models.py)
import sqlite3, json, os
from pathlib import Path
from datetime import datetime

DB_PATH = os.getenv("BLING_DB_PATH", "bling.db")

def _conn():
    return sqlite3.connect(DB_PATH)

def _ensure_dir():
    p = Path(DB_PATH)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)

def _recreate_if_corrupted():
    # Renomeia arquivo inválido e recria
    try:
        if Path(DB_PATH).exists():
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            Path(DB_PATH).rename(f"{DB_PATH}.corrupted-{ts}")
    except Exception:
        pass

def migrate():
    """Cria tabelas e índices. Se o arquivo estiver corrompido, recria."""
    _ensure_dir()
    try:
        con = _conn()
        cur = con.cursor()

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
            situacao TEXT,
            status TEXT,
            raw_json TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        """)

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
        );
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_pagar_venc ON contas_pagar(data_vencimento);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_receber_venc ON contas_receber(data_vencimento);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pagar_sit ON contas_pagar(situacao);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_receber_sit ON contas_receber(situacao);")

        con.commit(); con.close()
    except sqlite3.DatabaseError:
        # arquivo não é DB válido -> renomeia e tenta novamente
        _recreate_if_corrupted()
        con = _conn(); con.close()
        return migrate()

def _extract(item: dict):
    contato = item.get("contato") or {}
    categoria = item.get("categoria")
    categoria_desc = categoria.get("descricao") if isinstance(categoria, dict) else (categoria or "")
    return {
        "id_bling": str(item.get("id") or item.get("numero") or ""),
        "numero_documento": item.get("numeroDocumento") or item.get("numero") or "",
        "descricao": item.get("descricao") or item.get("historico") or "",
        "categoria": categoria_desc,
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
        updated_at=datetime('now');
    """
    con = _conn()
    con.execute(q, data)
    con.commit()
    con.close()
