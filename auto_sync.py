# auto_sync.py
import schedule
import time
import os
import subprocess

def run_sync():
    print(" Rodando sincronização automática...")
    # Executa o comando Python como subprocesso
    subprocess.run(["python", "-m", "src.services.sync"])
    print(" Sincronização concluída.")

# Agendar a execução a cada 1 hora
schedule.every(1).hours.do(run_sync)

print(" Iniciando agendador de sincronização (a cada 1 hora)...")
run_sync()  # Roda logo na primeira vez

# Loop infinito
while True:
    schedule.run_pending()
    time.sleep(60)
