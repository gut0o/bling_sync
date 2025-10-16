# scheduler.py
import time, traceback
from sync import main as run_sync

def job():
    try:
        print("\n  Rodando sync...")
        run_sync()
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    # loop simples de 1h
    while True:
        job()
        print("Aguardando 1h para a próxima execução...")
        time.sleep(60 * 60)
