import schedule
import time
from sync import sync_contas_pagar, sync_contas_receber

def job():
    print("🔄 Iniciando sincronização...")
    sync_contas_pagar()
    sync_contas_receber()
    print(" Sincronização concluída!")

schedule.every(1).hours.do(job)

print(" Scheduler iniciado (roda a cada 1h)")
while True:
    schedule.run_pending()
    time.sleep(60)
