import sys
sys.path.insert(0, r'c:\Users\darkf\OneDrive\Documentos\apibet')

from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import func
from sqlalchemy.sql import case

print("🔍 Testando endpoint analytics diretamente...\n")

try:
    with get_db() as db:
        print("✅ Conexão com banco estabelecida")
        
        # Total de partidas
        total_matches = db.query(Match).count()
        print(f"📊 Total de partidas: {total_matches}")
        
        # Partidas finalizadas
        finished_matches = db.query(Match).filter(Match.status == 'finished').count()
        print(f"✅ Partidas finalizadas: {finished_matches}")
        
        # Testa a query de league_stats (pode ser o problema)
        print("\n🔍 Testando agregação por liga...")
        league_stats = db.query(
            Match.league,
            func.count(Match.id).label('count'),
            func.sum(case((Match.status == 'finished', 1), else_=0)).label('finished')
        ).group_by(Match.league).all()
        
        print(f"✅ {len(league_stats)} ligas encontradas")
        for stat in league_stats[:3]:
            print(f"  - {stat.league}: {stat.count} partidas ({stat.finished} finalizadas)")
        
        # Testa média de odds
        print("\n🔍 Testando média de odds...")
        avg_odds = db.query(
            func.avg(Match.odd_home).label('home'),
            func.avg(Match.odd_draw).label('draw'),
            func.avg(Match.odd_away).label('away')
        ).first()
        
        print(f"✅ Média odds - Casa: {avg_odds.home}, Empate: {avg_odds.draw}, Fora: {avg_odds.away}")
        
        # Testa matches com resultado
        print("\n🔍 Testando matches com resultado...")
        matches_with_result = db.query(Match).filter(
            Match.result.isnot(None),
            Match.status == 'finished'
        ).all()
        
        print(f"✅ {len(matches_with_result)} partidas com resultado")
        
        if len(matches_with_result) > 0:
            match = matches_with_result[0]
            print(f"\n📋 Exemplo: {match.team_home} vs {match.team_away}")
            print(f"   Odds: {match.odd_home} / {match.odd_draw} / {match.odd_away}")
            print(f"   Resultado: {match.result}")
            print(f"   Placar: {match.goals_home} x {match.goals_away}")
        
        print("\n✅ TODOS OS TESTES PASSARAM!")
        
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
