"""
Modelos de banco de dados expandidos para dados da RapidAPI
Inclui todas as odds para análise de padrões e machine learning
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Match(Base):
    """
    Modelo expandido para partidas com todas as odds da RapidAPI
    Permite análise histórica e previsão de padrões
    """
    __tablename__ = "matches"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # ID da RapidAPI
    league = Column(String, index=True)  # express, copa, super, euro, premier
    
    # Times
    team_home = Column(String)
    team_away = Column(String)
    
    # Horário
    hour = Column(String)
    minute = Column(String)
    scheduled_time = Column(String)  # "19.53"
    
    # Resultado (preenchido após partida finalizar)
    goals_home = Column(Integer, nullable=True)
    goals_away = Column(Integer, nullable=True)
    total_goals = Column(Integer, nullable=True)
    result = Column(String, nullable=True)  # 'home', 'away', 'draw'
    
    # Odds - Resultado Final
    odd_home = Column(Float)
    odd_draw = Column(Float)
    odd_away = Column(Float)
    
    # Odds - Over/Under (Total de Gols)
    odd_over_05 = Column(Float, nullable=True)
    odd_under_05 = Column(Float, nullable=True)
    odd_over_15 = Column(Float, nullable=True)
    odd_under_15 = Column(Float, nullable=True)
    odd_over_25 = Column(Float, nullable=True)
    odd_under_25 = Column(Float, nullable=True)
    odd_over_35 = Column(Float, nullable=True)
    odd_under_35 = Column(Float, nullable=True)
    
    # Odds - Ambas Marcam
    odd_both_score_yes = Column(Float, nullable=True)
    odd_both_score_no = Column(Float, nullable=True)
    
    # Odds - Resultado Correto (mais comuns)
    odd_correct_1_0_home = Column(Float, nullable=True)
    odd_correct_0_0 = Column(Float, nullable=True)
    odd_correct_1_0_away = Column(Float, nullable=True)
    odd_correct_2_0_home = Column(Float, nullable=True)
    odd_correct_1_1 = Column(Float, nullable=True)
    odd_correct_2_0_away = Column(Float, nullable=True)
    odd_correct_2_1_home = Column(Float, nullable=True)
    odd_correct_2_2 = Column(Float, nullable=True)
    odd_correct_2_1_away = Column(Float, nullable=True)
    
    # Odds - Dupla Hipótese
    odd_double_home_draw = Column(Float, nullable=True)
    odd_double_away_draw = Column(Float, nullable=True)
    odd_double_home_away = Column(Float, nullable=True)
    
    # Odds - Total de Gols Exatos
    odd_exact_goals_0 = Column(Float, nullable=True)
    odd_exact_goals_1 = Column(Float, nullable=True)
    odd_exact_goals_2 = Column(Float, nullable=True)
    odd_exact_goals_3 = Column(Float, nullable=True)
    odd_exact_goals_4 = Column(Float, nullable=True)
    odd_exact_goals_5 = Column(Float, nullable=True)
    
    # Odds - Intervalo (1º Tempo)
    odd_halftime_home = Column(Float, nullable=True)
    odd_halftime_draw = Column(Float, nullable=True)
    odd_halftime_away = Column(Float, nullable=True)
    
    # Odds - Gols por Time
    odd_home_goals_0 = Column(Float, nullable=True)
    odd_home_goals_1 = Column(Float, nullable=True)
    odd_home_goals_2 = Column(Float, nullable=True)
    odd_home_goals_3 = Column(Float, nullable=True)
    odd_away_goals_0 = Column(Float, nullable=True)
    odd_away_goals_1 = Column(Float, nullable=True)
    odd_away_goals_2 = Column(Float, nullable=True)
    odd_away_goals_3 = Column(Float, nullable=True)
    
    # Odds - Handicap Asiático
    odd_handicap_home = Column(Float, nullable=True)
    odd_handicap_away = Column(Float, nullable=True)
    
    # JSON com TODAS as odds (backup completo para análises futuras)
    odds_json = Column(JSON, nullable=True)
    
    # Metadados
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    match_date = Column(DateTime, nullable=True)  # Data/hora real da partida
    status = Column(String, default="scheduled")  # scheduled, live, finished
    
    # Relacionamento
    scraper_log_id = Column(Integer, ForeignKey("scraper_logs.id"), nullable=True)
    scraper_log = relationship("ScraperLog", back_populates="matches")
    
    def __repr__(self):
        return f"<Match {self.external_id}: {self.team_home} vs {self.team_away} ({self.league})>"


class ScraperLog(Base):
    """
    Log de execuções do scraper
    """
    __tablename__ = "scraper_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)  # success, error, partial
    matches_found = Column(Integer, default=0)
    matches_new = Column(Integer, default=0)
    matches_updated = Column(Integer, default=0)
    leagues_scraped = Column(String, nullable=True)  # "express,copa,euro"
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    scraper_mode = Column(String, default="rapidapi")  # rapidapi ou selenium
    
    # Relacionamento
    matches = relationship("Match", back_populates="scraper_log")
    
    def __repr__(self):
        return f"<ScraperLog {self.id}: {self.status} - {self.matches_found} matches>"


class PredictionModel(Base):
    """
    Modelo para armazenar previsões de machine learning
    """
    __tablename__ = "prediction_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, unique=True, index=True)
    model_type = Column(String)  # 'regression', 'classification', etc
    target = Column(String)  # 'total_goals', 'result', 'over_2.5', etc
    accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_trained_at = Column(DateTime, nullable=True)
    training_samples = Column(Integer, default=0)
    features_used = Column(JSON, nullable=True)  # Lista de features usadas
    model_params = Column(JSON, nullable=True)  # Parâmetros do modelo
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<PredictionModel {self.model_name}: {self.target} - Acc: {self.accuracy}>"


class Prediction(Base):
    """
    Previsões feitas para partidas futuras
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), index=True)
    model_id = Column(Integer, ForeignKey("prediction_models.id"))
    
    # Previsão
    predicted_total_goals = Column(Float, nullable=True)
    predicted_result = Column(String, nullable=True)  # 'home', 'away', 'draw'
    confidence = Column(Float, nullable=True)  # 0-1
    
    # Validação (após partida)
    actual_total_goals = Column(Integer, nullable=True)
    actual_result = Column(String, nullable=True)
    prediction_correct = Column(Boolean, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Prediction match={self.match_id}: {self.predicted_total_goals} gols>"
