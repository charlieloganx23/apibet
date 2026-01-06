"""
Verificar dados diretamente no banco
"""
from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    # Verificar partida ID 138
    match = db.query(Match).filter(Match.id == 138).first()
    
    print("="*80)
    print("🔍 VERIFICAÇÃO DE DADOS NO BANCO")
    print("="*80)
    print(f"ID: {match.id}")
    print(f"Team Home: {match.team_home}")
    print(f"Team Away: {match.team_away}")
    print(f"Scheduled Time: {match.scheduled_time}")
    print(f"Goals Home: {match.goals_home}")
    print(f"Goals Away: {match.goals_away}")
    print(f"Total Goals: {match.total_goals}")
    print(f"Result: {match.result}")
    print(f"Status: {match.status}")
    
    # Verificar se tem o atributo
    print(f"\nHasattr goals_home: {hasattr(match, 'goals_home')}")
    print(f"Hasattr goals_away: {hasattr(match, 'goals_away')}")
    
    # Verificar todas as colunas
    print(f"\nTodas as colunas do modelo:")
    for col in match.__table__.columns:
        print(f"  - {col.name}: {getattr(match, col.name, 'N/A')}")
