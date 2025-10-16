from sqlalchemy import Column, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ContaPagar(Base):
    __tablename__ = "contas_pagar"
    id = Column(String, primary_key=True)
    descricao = Column(String)
    valor = Column(Float)
    vencimento = Column(DateTime)
    pagamento = Column(DateTime, nullable=True)
    status = Column(String)
    atualizado_em = Column(DateTime, default=datetime.utcnow)

class ContaReceber(Base):
    __tablename__ = "contas_receber"
    id = Column(String, primary_key=True)
    descricao = Column(String)
    valor = Column(Float)
    vencimento = Column(DateTime)
    pagamento = Column(DateTime, nullable=True)
    status = Column(String)
    atualizado_em = Column(DateTime, default=datetime.utcnow)
