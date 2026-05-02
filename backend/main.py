import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select, text
from redis import Redis
from rq import Queue
from dotenv import load_dotenv

import worker_mercadolivre
# Futuros workers serão importados aqui:
# import worker_amazon
# import worker_shopee

load_dotenv()

# --- MODELO ROBUSTO OMNIEXTRACT ---
class ProdutoMinerado(SQLModel, table=True):
    __tablename__ = "produtos"
    id: Optional[int] = Field(default=None, primary_key=True)
    termo_busca: str
    titulo: str
    link: Optional[str] = None
    preco_a_vista: float
    preco_prazo: Optional[float] = 0.0
    max_parcelas: Optional[int] = 1
    valor_parcela: Optional[float] = 0.0
    taxa_juros: Optional[bool] = False
    status_estoque: Optional[str] = "disponivel"
    is_oportunidade: Optional[bool] = False
    data_mineracao: datetime = Field(default_factory=datetime.utcnow)

# --- CONFIGURAÇÃO DA INFRA ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI(title="OmniExtract API - Enterprise")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

redis_conn = Redis(host='localhost', port=6380)
q = Queue(connection=redis_conn)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTAS DA API ---

@app.get("/produtos/", response_model=List[ProdutoMinerado])
def listar_produtos():
    """Entrega os produtos para o seu Painel Frontend"""
    with Session(engine) as session:
        statement = select(ProdutoMinerado).order_by(ProdutoMinerado.id.desc())
        return session.exec(statement).all()

# --- A PORTA DE ENTRADA PRO ROBÔ SALVAR OS DADOS ---
@app.post("/produtos/")
def salvar_produto(produto: ProdutoMinerado):
    """Recebe um produto do Worker e salva no Banco de Dados PostgreSQL"""
    with Session(engine) as session:
        session.add(produto)
        session.commit()
        return {"status": "Produto Salvo com sucesso!"}

@app.post("/buscar")
async def disparar_robo(payload: dict):
    """Aciona o robô em segundo plano via Redis Queue"""
    termo = payload.get("termo")
    site = payload.get("site", "")
    
    if not termo:
        raise HTTPException(status_code=400, detail="Digite um termo de busca")
        
    # Limpeza inteligente: Transforma "Mercado Livre", " MERCADO LIVRE " em "mercadolivre"
    site_formatado = str(site).lower().replace(" ", "").strip()
    
    # Roteador de Sites
    if site_formatado == "mercadolivre":
        job = q.enqueue(worker_mercadolivre.extrair_mercado_livre, termo)
        return {"status": "🤖 Robô acionado para o Mercado Livre!", "job_id": job.get_id()}
        
    elif site_formatado == "amazon":
        return {"status": "🤖 Em breve: Robô da Amazon será acionado!", "job_id": "futuro"}
        
    elif site_formatado == "shopee":
        return {"status": "🤖 Em breve: Robô da Shopee será acionado!", "job_id": "futuro"}
        
    return {"status": "erro", "msg": f"Site '{site}' ainda não suportado na nossa base."}

@app.get("/health/db")
def check_db():
    with Session(engine) as session:
        session.exec(text("SELECT 1"))
        return {"status": "online", "database": "PostgreSQL Pronto"}
