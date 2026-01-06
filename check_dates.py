import sys
sys.path.insert(0, r'c:\Users\darkf\OneDrive\Documentos\apibet')

from database_rapidapi import get_db
from models_rapidapi import Match

print("🔍 VERIFICANDO DATAS DAS PARTIDAS...\n")

try:
    with get_db() as db:
        # Busca amostras
        samples = db.query(Match).limit(10).all()
        
        print(f"📋 Amostras de partidas:\n")
        for m in samples:
            print(f"ID: {m.id}")
            print(f"   {m.team_home} vs {m.team_away}")
            print(f"   Liga: {m.league}")
            print(f"   Status: {m.status}")
            print(f"   match_date: {m.match_date}")
            print(f"   scheduled_time: {m.scheduled_time}")
            print(f"   hour: {m.hour}, minute: {m.minute}")
            print(f"   scraped_at: {m.scraped_at}")
            print()
            
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
