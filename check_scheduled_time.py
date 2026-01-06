from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    matches = db.query(Match).order_by(Match.id.desc()).limit(5).all()
    print("Primeiras 5 partidas:")
    for m in matches:
        print(f"ID {m.id} | scheduled_time={m.scheduled_time} | hour={m.hour} | minute={m.minute} | {m.team_home} vs {m.team_away}")
