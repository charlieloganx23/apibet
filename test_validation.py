import sys
sys.path.insert(0, r'c:\Users\darkf\OneDrive\Documentos\apibet')

from database_rapidapi import get_db
from models_rapidapi import Match

print("🧪 TESTANDO LÓGICA DE VALIDAÇÃO...\n")

try:
    with get_db() as db:
        # Buscar partidas finalizadas
        finished = db.query(Match).filter(
            Match.result.isnot(None),
            Match.status == 'finished'
        ).all()
        
        print(f"✅ Partidas finalizadas com resultado: {len(finished)}\n")
        
        if len(finished) == 0:
            print("⚠️ PROBLEMA: Nenhuma partida finalizada encontrada!")
            print("   Verificando status das partidas...")
            
            all_matches = db.query(Match).limit(10).all()
            for m in all_matches:
                print(f"   ID {m.id}: status={m.status}, result={m.result}")
        else:
            # Validar predições
            stats = {
                'total': len(finished),
                'correct_winner': 0,
                'correct_over_under': 0
            }
            
            print("📊 Validando predições...\n")
            
            for match in finished[:5]:  # Mostra apenas 5 exemplos
                # Predição baseada em odds (menor odd = favorito)
                odds = [
                    (match.odd_home, 'home'),
                    (match.odd_draw, 'draw'),
                    (match.odd_away, 'away')
                ]
                
                valid_odds = [(o, r) for o, r in odds if o is not None]
                if valid_odds:
                    predicted_winner = min(valid_odds, key=lambda x: x[0])[1]
                    
                    correct = "✅" if predicted_winner == match.result else "❌"
                    print(f"{correct} {match.team_home} vs {match.team_away}")
                    print(f"   Predição: {predicted_winner} (odds: {match.odd_home}/{match.odd_draw}/{match.odd_away})")
                    print(f"   Real: {match.result} (placar: {match.goals_home}-{match.goals_away})")
                    
                    if predicted_winner == match.result:
                        stats['correct_winner'] += 1
            
            # Validar todos
            for match in finished:
                odds = [
                    (match.odd_home, 'home'),
                    (match.odd_draw, 'draw'),
                    (match.odd_away, 'away')
                ]
                
                valid_odds = [(o, r) for o, r in odds if o is not None]
                if valid_odds:
                    predicted_winner = min(valid_odds, key=lambda x: x[0])[1]
                    if predicted_winner == match.result:
                        stats['correct_winner'] += 1
                
                # Over/Under 2.5
                if match.total_goals is not None:
                    if match.odd_over_25 and match.odd_under_25:
                        predicted_over = match.odd_over_25 < match.odd_under_25
                        actual_over = match.total_goals > 2.5
                        if predicted_over == actual_over:
                            stats['correct_over_under'] += 1
            
            accuracy_winner = (stats['correct_winner'] / stats['total'] * 100) if stats['total'] > 0 else 0
            accuracy_over = (stats['correct_over_under'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            print(f"\n📈 RESULTADO FINAL:")
            print(f"   Total: {stats['total']} partidas")
            print(f"   Acertos vencedor: {stats['correct_winner']} ({accuracy_winner:.1f}%)")
            print(f"   Acertos over/under: {stats['correct_over_under']} ({accuracy_over:.1f}%)")
            
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
