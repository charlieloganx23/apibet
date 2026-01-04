"""
API REST com FastAPI para servir dados de Futebol Virtual
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db_session, init_db
from models import VirtualMatch, VirtualMatchMarket, ScraperLog
from config import API_HOST, API_PORT

# Inicializa FastAPI
app = FastAPI(
    title="Bet365 Virtual Football API",
    description="API para consultar resultados de Futebol Virtual",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schemas Pydantic
class MatchResponse(BaseModel):
    id: int
    match_id: str
    competition: Optional[str]
    home_team: str
    away_team: str
    home_score_ht: Optional[int]
    away_score_ht: Optional[int]
    home_score_ft: Optional[int]
    away_score_ft: Optional[int]
    status: Optional[str]
    match_time: Optional[str]
    match_date: datetime
    created_at: datetime
    updated_at: datetime
    source_url: Optional[str]
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_matches: int
    live_matches: int
    finished_matches: int
    last_update: Optional[datetime]


class ScraperLogResponse(BaseModel):
    id: int
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    matches_found: int
    matches_new: int
    matches_updated: int
    
    class Config:
        from_attributes = True


# Rotas
@app.on_event("startup")
async def startup_event():
    """Inicializa o banco de dados ao iniciar"""
    init_db()


@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "message": "Bet365 Virtual Football API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/matches", response_model=List[MatchResponse])
async def get_matches(
    competition: Optional[str] = Query(None, description="Filtrar por competição"),
    status: Optional[str] = Query(None, description="Filtrar por status (live/finished)"),
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    limit: int = Query(100, le=1000, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna lista de partidas com filtros opcionais
    """
    query = db.query(VirtualMatch)
    
    if competition:
        query = query.filter(VirtualMatch.competition == competition)
    
    if status:
        query = query.filter(VirtualMatch.status == status)
    
    if date_from:
        query = query.filter(VirtualMatch.match_date >= date_from)
    
    if date_to:
        query = query.filter(VirtualMatch.match_date <= date_to)
    
    query = query.order_by(VirtualMatch.match_date.desc())
    query = query.offset(offset).limit(limit)
    
    matches = query.all()
    return matches


@app.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Retorna detalhes de uma partida específica
    """
    match = db.query(VirtualMatch).filter(VirtualMatch.match_id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    return match


@app.get("/matches/live/current", response_model=List[MatchResponse])
async def get_live_matches(
    db: Session = Depends(get_db_session)
):
    """
    Retorna partidas ao vivo
    """
    matches = db.query(VirtualMatch).filter(
        VirtualMatch.status == 'live'
    ).order_by(VirtualMatch.match_date.desc()).all()
    
    return matches


@app.get("/results/recent")
async def get_recent_results(
    hours: int = Query(24, description="Últimas N horas"),
    competition: Optional[str] = Query(None, description="Filtrar por competição"),
    db: Session = Depends(get_db_session)
):
    """
    Retorna resultados recentes
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(VirtualMatch).filter(
        VirtualMatch.match_date >= since,
        VirtualMatch.status == 'finished'
    )
    
    if competition:
        query = query.filter(VirtualMatch.competition == competition)
    
    matches = query.order_by(VirtualMatch.match_date.desc()).all()
    
    return matches


@app.get("/competitions")
async def get_competitions(db: Session = Depends(get_db_session)):
    """
    Retorna lista de competições disponíveis
    """
    competitions = db.query(VirtualMatch.competition).distinct().all()
    return {"competitions": [c[0] for c in competitions if c[0]]}


@app.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db_session)):
    """
    Retorna estatísticas gerais
    """
    total = db.query(VirtualMatch).count()
    live = db.query(VirtualMatch).filter(VirtualMatch.status == 'live').count()
    finished = db.query(VirtualMatch).filter(VirtualMatch.status == 'finished').count()
    
    last_match = db.query(VirtualMatch).order_by(
        VirtualMatch.updated_at.desc()
    ).first()
    
    return {
        "total_matches": total,
        "live_matches": live,
        "finished_matches": finished,
        "last_update": last_match.updated_at if last_match else None
    }


@app.get("/scraper/logs", response_model=List[ScraperLogResponse])
async def get_scraper_logs(
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db_session)
):
    """
    Retorna logs de execução do scraper
    """
    logs = db.query(ScraperLog).order_by(
        ScraperLog.started_at.desc()
    ).limit(limit).all()
    
    return logs


@app.get("/scraper/status")
async def get_scraper_status(db: Session = Depends(get_db_session)):
    """
    Retorna status do último scraping
    """
    last_log = db.query(ScraperLog).order_by(
        ScraperLog.started_at.desc()
    ).first()
    
    if not last_log:
        return {"status": "never_run"}
    
    return {
        "last_run": last_log.started_at,
        "status": last_log.status,
        "matches_found": last_log.matches_found,
        "matches_new": last_log.matches_new,
        "matches_updated": last_log.matches_updated,
        "error": last_log.error_message
    }


@app.post("/scraper/run")
async def trigger_scraper():
    """
    Dispara execução manual do scraper
    ⚠️ Em produção, proteger com autenticação
    """
    from scraper import run_scraper
    import threading
    
    # Executa em thread separada para não bloquear
    thread = threading.Thread(target=run_scraper)
    thread.start()
    
    return {"message": "Scraper iniciado em background"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
