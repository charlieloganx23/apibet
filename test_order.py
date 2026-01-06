"""
Teste de ordenação das partidas
"""
from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import func

with get_db() as db:
    total = db.query(func.count(Match.id)).scalar()
    finished = db.query(func.count(Match.id)).filter(Match.total_goals.isnot(None)).scalar()
    scheduled = db.query(func.count(Match.id)).filter(Match.total_goals.is_(None)).scalar()
    
    print("="*80)
    print("📊 VERIFICAÇÃO DE ORDENAÇÃO")
    print("="*80)
    print(f"Total de partidas: {total}")
    print(f"Finalizadas: {finished}")
    print(f"Agendadas: {scheduled}")
    print()
    
    print("🏆 ÚLTIMAS 10 PARTIDAS FINALIZADAS (ID decrescente - mais recentes):")
    for m in db.query(Match).filter(Match.total_goals.isnot(None)).order_by(Match.id.desc()).limit(10):
        print(f"  ID {m.id:4d} | {m.scheduled_time or 'N/A':5s} | {m.league:7s} | {m.team_home:20s} {m.goals_home}x{m.goals_away} {m.team_away}")
    
    print()
    print("📅 PRÓXIMAS 10 PARTIDAS AGENDADAS (ID decrescente):")
    for m in db.query(Match).filter(Match.total_goals.is_(None)).order_by(Match.id.desc()).limit(10):
        status_icon = "🔴" if m.status == 'live' else "⏰" if m.status == 'expired' else "📅"
        print(f"  ID {m.id:4d} | {m.scheduled_time or 'N/A':5s} | {m.league:7s} | {status_icon} {m.team_home} vs {m.team_away}")
