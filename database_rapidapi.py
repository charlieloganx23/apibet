"""
Configuração do banco de dados para o novo modelo (RapidAPI)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from config import DATABASE_URL
from models_rapidapi import Base

# Usar banco de dados separado para RapidAPI
RAPIDAPI_DATABASE_URL = DATABASE_URL.replace("bet365_virtual.db", "bet365_rapidapi.db")

# Criar engine
engine = create_engine(
    RAPIDAPI_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in RAPIDAPI_DATABASE_URL else {},
    echo=False  # True para debug SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado!")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para obter sessão do banco de dados
    
    Usage:
        with get_db() as db:
            matches = db.query(Match).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Retorna sessão do banco de dados (para uso com dependency injection)
    Lembre-se de fechar a sessão após o uso!
    
    Usage:
        db = get_db_session()
        try:
            matches = db.query(Match).all()
        finally:
            db.close()
    """
    return SessionLocal()
