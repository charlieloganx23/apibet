"""
Script para atualizar resultado de partida
"""
from database_rapidapi import get_db
from models_rapidapi import Match

# Buscar partida
with get_db() as db:
    match = db.query(Match).filter(
        Match.team_home == "Polônia",
        Match.team_away == "Geórgia",
        Match.hour == "3",
        Match.minute == "14"
    ).first()
    
    if match:
        print(f"✅ Partida encontrada: {match.team_home} vs {match.team_away}")
        print(f"   ID: {match.id}")
        
        # Atualizar resultado
        match.goals_home = 2
        match.goals_away = 0
        match.total_goals = 2
        match.result = "home"
        match.status = "finished"
        
        db.commit()
        print(f"\n✅ Resultado atualizado:")
        print(f"   Placar: {match.goals_home}x{match.goals_away}")
        print(f"   Vencedor: {match.result}")
        print(f"   Status: {match.status}")
    else:
        print("❌ Partida não encontrada")
        print("\nBuscando partidas similares...")
        matches = db.query(Match).filter(
            Match.team_home.like("%Polônia%")
        ).all()
        for m in matches:
            print(f"   {m.team_home} vs {m.team_away} - {m.hour}:{m.minute}")
