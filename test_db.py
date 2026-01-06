import sys
from database_rapidapi import get_db
from models_rapidapi import Match

try:
    with get_db() as db:
        matches = db.query(Match).limit(5).all()
        print(f"✅ Banco OK! {len(matches)} partidas encontradas")
        
        if matches:
            m = matches[0]
            print(f"\n📊 Exemplo de partida:")
            print(f"  ID: {m.id}")
            print(f"  Liga: {m.league}")
            print(f"  Times: {m.home_team} vs {m.away_team}")
            print(f"  Data: {m.match_date}")
            print(f"  Hora: {m.hour}:{m.minute}")
            
            # Testar se tem todos os campos necessários
            print(f"\n🔍 Campos:")
            print(f"  predicted_winner: {m.predicted_winner}")
            print(f"  predicted_score: {m.predicted_score}")
            print(f"  confidence: {m.confidence}")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
