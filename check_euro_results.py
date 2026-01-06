from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    euro_finished = db.query(Match).filter(
        Match.league == 'euro',
        Match.goals_home.isnot(None)
    ).order_by(Match.scheduled_time).all()
    
    print(f"Partidas da Euro Cup finalizadas: {len(euro_finished)}")
    print()
    for m in euro_finished:
        print(f"{m.scheduled_time} | {m.team_home} {m.goals_home}x{m.goals_away} {m.team_away} | Status: {m.status}")
