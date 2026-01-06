import sys
sys.path.insert(0, r'c:\Users\darkf\OneDrive\Documentos\apibet')

from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import func

print("🔍 VERIFICANDO DADOS NO BANCO...\n")

try:
    with get_db() as db:
        # Total de partidas
        total = db.query(Match).count()
        print(f"📊 Total de partidas: {total}")
        
        # Partidas por status
        statuses = db.query(Match.status, func.count(Match.id)).group_by(Match.status).all()
        print(f"\n📋 Partidas por status:")
        for status, count in statuses:
            print(f"   {status}: {count}")
        
        # Partidas com resultado
        with_result = db.query(Match).filter(Match.result.isnot(None)).count()
        print(f"\n✅ Partidas com resultado definido: {with_result}")
        
        # Partidas com placar
        with_score = db.query(Match).filter(
            Match.goals_home.isnot(None),
            Match.goals_away.isnot(None)
        ).count()
        print(f"⚽ Partidas com placar: {with_score}")
        
        # Amostras de partidas finalizadas
        finished = db.query(Match).filter(Match.status == 'finished').limit(5).all()
        print(f"\n📝 Amostras de partidas finalizadas ({len(finished)}):")
        for m in finished:
            print(f"   {m.team_home} vs {m.team_away}")
            print(f"   Status: {m.status}, Resultado: {m.result}")
            print(f"   Placar: {m.goals_home} x {m.goals_away}")
            print()
        
        # Amostras de partidas com resultado mas status != finished
        weird = db.query(Match).filter(
            Match.result.isnot(None),
            Match.status != 'finished'
        ).limit(5).all()
        
        if weird:
            print(f"\n⚠️ Partidas COM resultado mas status != 'finished' ({len(weird)}):")
            for m in weird:
                print(f"   {m.team_home} vs {m.team_away}")
                print(f"   Status: {m.status}, Resultado: {m.result}")
                print(f"   Placar: {m.goals_home} x {m.goals_away}")
                print()
        
        # Verifica campos de predição
        print("🔮 Verificando campos de predição no modelo:")
        sample = db.query(Match).first()
        if sample:
            print(f"   Campos disponíveis: {[col for col in dir(sample) if not col.startswith('_')]}")
            
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
