"""
Adicionar resultados manualmente às partidas antigas para demonstração
"""
from database_rapidapi import get_db
from models_rapidapi import Match
from datetime import datetime, timedelta
import random

with get_db() as db:
    site_time = datetime.now() + timedelta(hours=4)
    
    print("="*80)
    print("⚽ ADICIONANDO RESULTADOS MANUALMENTE")
    print("="*80)
    print(f"🌐 Horário do SITE: {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Buscar partidas das 16:48-17:11 que já passaram (mais de 10 minutos)
    cutoff_time = site_time - timedelta(minutes=10)
    
    matches_to_update = []
    for match in db.query(Match).all():
        if not match.scheduled_time:
            continue
        
        try:
            parts = match.scheduled_time.split('.')
            if len(parts) != 2:
                continue
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            match_time = site_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if match_time > site_time:
                match_time = match_time - timedelta(days=1)
            
            # Se passou mais de 10 minutos e não tem resultado
            if match_time < cutoff_time and match.goals_home is None:
                matches_to_update.append({
                    'match': match,
                    'time': match_time
                })
        except:
            continue
    
    print(f"📋 Encontradas {len(matches_to_update)} partidas antigas sem resultado")
    print()
    
    # Adicionar resultados aleatórios realistas
    updated = 0
    for item in matches_to_update[:15]:  # Atualizar até 15 partidas
        m = item['match']
        
        # Gerar placar realista (0-4 gols, mais comum 1-2 gols)
        goals_home = random.choices([0, 1, 2, 3, 4], weights=[15, 35, 30, 15, 5])[0]
        goals_away = random.choices([0, 1, 2, 3], weights=[20, 35, 30, 15])[0]
        
        m.goals_home = goals_home
        m.goals_away = goals_away
        m.total_goals = goals_home + goals_away
        
        if goals_home > goals_away:
            m.result = 'home'
        elif goals_away > goals_home:
            m.result = 'away'
        else:
            m.result = 'draw'
        
        m.status = 'finished'
        
        print(f"   ✅ {m.scheduled_time} | {m.league:7s} | {m.team_home} {goals_home}x{goals_away} {m.team_away}")
        updated += 1
    
    db.commit()
    
    print()
    print(f"✅ {updated} partidas atualizadas com resultados!")
    print("="*80)
