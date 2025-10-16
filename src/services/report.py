# report.py
import sqlite3
from datetime import datetime

DB_PATH = "bling.db"

def run_query(q, params=()):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(q, params)
    rows = cur.fetchall()
    con.close()
    return rows

def total_a_pagar_hoje():
    q = """
    SELECT IFNULL(SUM(valor),0) AS total
    FROM contas_pagar
    WHERE situacao LIKE 'ABER%' AND date(data_vencimento) = date('now');
    """
    return run_query(q)[0]["total"]

def total_a_receber_hoje():
    q = """
    SELECT IFNULL(SUM(valor),0) AS total
    FROM contas_receber
    WHERE situacao LIKE 'ABER%' AND date(data_vencimento) = date('now');
    """
    return run_query(q)[0]["total"]

def devedores():
    q = """
    SELECT contato_nome, SUM(valor) AS total
    FROM contas_receber
    WHERE situacao LIKE 'ABER%' AND date(data_vencimento) < date('now')
    GROUP BY contato_nome
    ORDER BY total DESC;
    """
    return run_query(q)

def resumo_semana():
    q = """
    SELECT 'pagar' AS tipo, IFNULL(SUM(valor),0) AS total
    FROM contas_pagar
    WHERE date(data_vencimento) BETWEEN date('now','-6 day') AND date('now')
    UNION ALL
    SELECT 'receber', IFNULL(SUM(valor),0)
    FROM contas_receber
    WHERE date(data_vencimento) BETWEEN date('now','-6 day') AND date('now');
    """
    return run_query(q)

if __name__ == "__main__":
    print(" RELATÓRIO FINANCEIRO\n")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f" A pagar hoje: R$ {total_a_pagar_hoje():.2f}")
    print(f" A receber hoje: R$ {total_a_receber_hoje():.2f}\n")

    print(" Resumo últimos 7 dias:")
    for r in resumo_semana():
        print(f" - {r['tipo'].capitalize()}: R$ {r['total']:.2f}")

    print("\n Devedores em aberto:")
    for r in devedores():
        print(f" - {r['contato_nome'] or '(sem nome)'}: R$ {r['total']:.2f}")
