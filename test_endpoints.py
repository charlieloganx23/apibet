"""Testa os endpoints que estão dando erro"""
import sys
import traceback
from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import func

print("🔍 Testando endpoint /api/analytics/overview...")
try:
    with get_db() as db:
    
        # Total de partidas
        total_matches = db.query(Match).count()
        print(f"✅ Total de partidas: {total_matches}")
        
        # Partidas finalizadas
        finished_matches = db.query(Match).filter(
            Match.status == 'finished'
        ).count()
        print(f"✅ Partidas finalizadas: {finished_matches}")
        
        # Busca partidas com resultado
        matches_with_result = db.query(Match).filter(
            Match.result.isnot(None),
            Match.status == 'finished'
        ).all()
        print(f"✅ Partidas com resultado: {len(matches_with_result)}")
        
        # Testa acesso aos campos
        if matches_with_result:
            match = matches_with_result[0]
            print(f"✅ Exemplo: {match.team_home} vs {match.team_away}")
            print(f"   Odds: {match.odd_home}, {match.odd_draw}, {match.odd_away}")
            print(f"   Resultado: {match.result}")
            print(f"   Gols: {match.goals_home} x {match.goals_away}")
        
        # Testa agregação por liga
        league_stats = db.query(
            Match.league,
            func.count(Match.id).label('count'),
            func.count(func.case((Match.status == 'finished', 1))).label('finished')
        ).group_by(Match.league).all()
        
        print(f"✅ Estatísticas por liga: {len(league_stats)} ligas")
        for stat in league_stats:
            print(f"   {stat.league}: {stat.count} total, {stat.finished} finalizadas")
        
        # Testa média de odds
        avg_odds = db.query(
            func.avg(Match.odd_home).label('home'),
            func.avg(Match.odd_draw).label('draw'),
            func.avg(Match.odd_away).label('away')
        ).first()
        
        print(f"✅ Média de odds: Casa={avg_odds.home:.2f}, Empate={avg_odds.draw:.2f}, Fora={avg_odds.away:.2f}")
        
        print("\n✅ Teste /api/analytics/overview: PASSOU!")
    
except Exception as e:
    print(f"\n❌ ERRO no teste analytics:")
    print(f"   {type(e).__name__}: {str(e)}")
    traceback.print_exc()

print("\n" + "="*60)
print("🔍 Testando endpoint /api/recommendations...")
try:
    with get_db() as db:
    
        # Busca partidas agendadas
        upcoming = db.query(Match).filter(
            Match.status == 'scheduled'
        ).limit(10).all()
        
        print(f"✅ Partidas agendadas: {len(upcoming)}")
        
        if upcoming:
            match = upcoming[0]
            print(f"✅ Exemplo: {match.team_home} vs {match.team_away}")
            print(f"   Status: {match.status}")
            print(f"   Horário: {match.hour}:{match.minute}")
            print(f"   Odds: Casa={match.odd_home}, Empate={match.odd_draw}, Fora={match.odd_away}")
            
            # Testa lógica de recomendação
            odds_list = [
                ('home', match.odd_home),
                ('draw', match.odd_draw),
                ('away', match.odd_away)
            ]
            valid_odds = [(name, odd) for name, odd in odds_list if odd and odd > 0]
            
            if valid_odds:
                predicted_winner, min_odd = min(valid_odds, key=lambda x: x[1])
                implied_prob = 1 / min_odd if min_odd > 0 else 0
                confidence = implied_prob * 100
                
                print(f"   Favorito: {predicted_winner} (odd={min_odd:.2f}, confiança={confidence:.1f}%)")
        
        print("\n✅ Teste /api/recommendations: PASSOU!")
    
except Exception as e:
    print(f"\n❌ ERRO no teste recommendations:")
    print(f"   {type(e).__name__}: {str(e)}")
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Todos os testes concluídos!")
