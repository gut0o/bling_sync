# mock_data.py
import sqlite3, random, datetime

DB_PATH = "bling.db"
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

nomes = ["Cliente A", "Cliente B", "Fornecedor X", "Fornecedor Y"]
situacoes = ["ABERTA", "BAIXADA"]

def add_mock(tabela, tipo):
    for i in range(5):
        id_bling = f"{tipo}_{i}"
        descricao = f"{tipo.capitalize()} teste {i}"
        valor = round(random.uniform(50, 500), 2)
        data_venc = (datetime.date.today() + datetime.timedelta(days=random.randint(-3, 3))).isoformat()
        situacao = random.choice(situacoes)
        nome = random.choice(nomes)

        cur.execute(f"""
        INSERT OR IGNORE INTO {tabela} (id_bling, descricao, contato_nome, valor, data_vencimento, situacao)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (id_bling, descricao, nome, valor, data_venc, situacao))

add_mock("contas_pagar", "pagar")
add_mock("contas_receber", "receber")

con.commit()
con.close()
print("✅ Dados de teste inseridos no banco!")
