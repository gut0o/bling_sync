from database import init_db
from scheduler import job

if __name__ == "__main__":
    init_db()
    job()  # roda manualmente uma vez pra testar
