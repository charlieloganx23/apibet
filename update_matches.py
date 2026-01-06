"""
Script rápido para atualizar partidas sem fechar o sistema
"""
import sys
from scraper_rapidapi import run_rapidapi_scraper
from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import func

print("🔄 Atualizando partidas...")
print("=" * 60)

# Contagem antes
with get_db() as db:
    before = db.query(Match).count()
    print(f"📊 Partidas no banco antes: {before}")

# Executar scraper
try:
    result = run_rapidapi_scraper()
    print(f"\n✅ Scraper executado!")
    print(f"   Partidas encontradas: {result.get('matches_found', 0)}")
    print(f"   Partidas novas: {result.get('matches_new', 0)}")
    print(f"   Partidas atualizadas: {result.get('matches_updated', 0)}")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Contagem depois
with get_db() as db:
    after = db.query(Match).count()
    print(f"\n📊 Partidas no banco depois: {after}")
    print(f"   Diferença: +{after - before}")
    
    # Últimas partidas adicionadas
    print(f"\n📋 Últimas 5 partidas por liga:")
    from config import RAPIDAPI_LEAGUES
    for league in RAPIDAPI_LEAGUES:
        last = db.query(Match).filter(Match.league == league).order_by(Match.id.desc()).first()
        if last:
            print(f"   {league:8s}: {last.team_home} vs {last.team_away} - {last.hour}:{last.minute}")

print("\n" + "=" * 60)
print("✅ Atualização concluída!")
