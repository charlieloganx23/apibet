from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import desc
from datetime import datetime

with get_db() as db:
    # Últimas partidas da EURO
    print(f"\n{'='*60}")
    print(f"⚽ ÚLTIMAS PARTIDAS DA EURO CUP")
    print(f"{'='*60}\n")
    
    euro_matches = db.query(Match).filter(
        Match.league == 'euro',
        Match.status == 'scheduled'
    ).order_by(desc(Match.scraped_at)).limit(6).all()
    
    if euro_matches:
        # Ordena por horário
        euro_sorted = sorted(euro_matches, key=lambda x: (x.hour, x.minute))
        
        for m in euro_sorted:
            print(f"{m.hour}:{m.minute} | {m.team_home} vs {m.team_away}")
        
        print(f"\nÚltima atualização: {euro_matches[0].scraped_at}")
        print(f"Horário atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostra todas as próximas partidas por horário
    print(f"\n{'='*60}")
    print(f"📅 PRÓXIMAS PARTIDAS (todas as ligas)")
    print(f"{'='*60}\n")
    
    upcoming = db.query(Match).filter(
        Match.status == 'scheduled'
    ).order_by(Match.hour, Match.minute).limit(10).all()
    
    for m in upcoming:
        print(f"{m.hour}:{m.minute} | {m.league:8s} | {m.team_home} vs {m.team_away}")
    
    print(f"\n{'='*60}\n")
