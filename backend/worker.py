import os
from redis import Redis
from rq import Worker, Queue
from dotenv import load_dotenv

# Carrega as configurações do seu .env
load_dotenv()

if __name__ == '__main__':
    # Conectamos ao Redis na porta 6380 (vimos que ele está lá no seu Docker)
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6380/0")
    redis_conn = Redis.from_url(redis_url)
    
    print("👷 Worker OmniExtract em prontidão (Porta 6380)...")
    print("Aguardando ordens para minerar o Mercado Livre...")
    
    # Criamos o operário passando a conexão diretamente para evitar erros de importação
    worker = Worker(['default'], connection=redis_conn)
    worker.work()
