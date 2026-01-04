"""
Modelos do banco de dados
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VirtualMatch(Base):
    """Modelo para armazenar partidas de Futebol Virtual"""
    __tablename__ = "virtual_matches"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação da partida
    match_id = Column(String(100), unique=True, index=True, nullable=False)
    competition = Column(String(100), index=True)  # Mundial, Premiership, Superliga
    
    # Times
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    
    # Resultados
    home_score_ht = Column(Integer)  # Half Time
    away_score_ht = Column(Integer)
    home_score_ft = Column(Integer)  # Full Time
    away_score_ft = Column(Integer)
    
    # Status da partida
    status = Column(String(20))  # live, finished, scheduled
    match_time = Column(String(10))  # Tempo de jogo (ex: 45', 90')
    
    # Datas
    match_date = Column(DateTime, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Dados adicionais (mercados, odds, etc.)
    additional_data = Column(JSON, nullable=True)
    
    # URL de referência
    source_url = Column(String(500))

    def __repr__(self):
        return f"<VirtualMatch {self.home_team} {self.home_score_ft}x{self.away_score_ft} {self.away_team}>"


class VirtualMatchMarket(Base):
    """Modelo para armazenar mercados específicos do Futebol Virtual"""
    __tablename__ = "virtual_match_markets"

    id = Column(Integer, primary_key=True, index=True)
    
    match_id = Column(String(100), index=True, nullable=False)
    
    # Tipo de mercado
    market_type = Column(String(100), nullable=False)  # over_under, both_teams_score, etc.
    market_name = Column(String(200))
    
    # Resultado do mercado
    market_result = Column(String(50))
    market_value = Column(Float)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<VirtualMatchMarket {self.match_id} - {self.market_type}>"


class ScraperLog(Base):
    """Log de execuções do scraper"""
    __tablename__ = "scraper_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    
    status = Column(String(20))  # success, error, partial
    matches_found = Column(Integer, default=0)
    matches_new = Column(Integer, default=0)
    matches_updated = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Renomeado de 'metadata' (nome reservado)

    def __repr__(self):
        return f"<ScraperLog {self.started_at} - {self.status}>"
