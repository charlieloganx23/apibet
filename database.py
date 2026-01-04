"""
Conexão com o banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import DATABASE_URL
from models import Base
from loguru import logger


# Engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True para debug SQL
    pool_pre_ping=True,
    pool_recycle=3600
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise


@contextmanager
def get_db() -> Session:
    """Context manager para sessões do banco de dados"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na transação do banco: {e}")
        raise
    finally:
        db.close()


def get_db_session():
    """Dependência para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
