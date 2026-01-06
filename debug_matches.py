"""
Debug - verificar partidas no banco
"""
from datetime import datetime, timedelta
from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    now_local = datetime.now()
    site_time = now_local + timedelta(hours=4)
    
    print("="*80)
    print("🔍 DEBUG - ANÁLISE DAS PARTIDAS")
    print("="*80)
    print(f"⏰ Horário LOCAL: {now_local.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌐 Horário do SITE: {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*80)
    
    # Pegar as primeiras 20 partidas finalizadas
    finished = db.query(Match).filter(Match.goals_home.isnot(None)).order_by(Match.id).limit(20).all()
    
    print(f"\n📊 PRIMEIRAS 20 PARTIDAS FINALIZADAS:")
    for m in finished:
        print(f"   ID {m.id:4d} | {m.scheduled_time:5s} | {m.league:7s} | {m.team_home} vs {m.team_away}")
        print(f"           Resultado: {m.goals_home}x{m.goals_away}")
        
        # Calcular quanto tempo passou
        try:
            parts = m.scheduled_time.split('.')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                
                match_time = site_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Se hora da partida > hora atual, é de ontem
                if match_time > site_time:
                    match_time = match_time - timedelta(days=1)
                
                hours_ago = (site_time - match_time).total_seconds() / 3600
                print(f"           ⏱️  Passou há {hours_ago:.1f} horas")
        except:
            pass
    
    print("\n" + "="*80)
