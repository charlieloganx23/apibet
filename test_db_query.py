"""
Testar query diretamente no banco
"""
from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    # Sem filtros
    total = db.query(Match).count()
    print(f"Total no banco: {total}")
    
    # Com ordem desc
    matches = db.query(Match).order_by(Match.id.desc()).limit(10).all()
    print(f"\nPrimeiras 10 partidas (order by id desc):")
    for m in matches:
        print(f"  ID {m.id} | {m.scheduled_time} | {m.league} | {m.team_home} vs {m.team_away}")
        print(f"     goals_home={m.goals_home}, goals_away={m.goals_away}")
