"""
Limpar partidas antigas sem resultado
Remove partidas que já passaram há muito tempo e não têm resultado
"""
from datetime import datetime, timedelta
from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    site_time = datetime.now() + timedelta(hours=4)
    
    print("="*80)
    print("🧹 LIMPEZA DE PARTIDAS ANTIGAS")
    print("="*80)
    print(f"⏰ Horário do site: {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Buscar partidas sem resultado
    old_matches = []
    for match in db.query(Match).filter(Match.goals_home.is_(None)).all():
        if not match.scheduled_time:
            continue
        
        try:
            parts = match.scheduled_time.split('.')
            if len(parts) != 2:
                continue
            
            match_hour = int(parts[0])
            match_minute = int(parts[1])
            
            # Calcular se passou há mais de 6 horas
            match_minutes = match_hour * 60 + match_minute
            site_minutes = site_time.hour * 60 + site_time.minute
            
            diff = site_minutes - match_minutes
            
            # Se a diferença é muito grande (passou há mais de 6h), remover
            if diff > 360 or diff < -720:  # Mais de 6 horas de diferença
                old_matches.append(match)
        except:
            continue
    
    print(f"\n📋 Partidas antigas encontradas: {len(old_matches)}")
    
    if len(old_matches) > 0:
        print("\n🗑️  Removendo partidas antigas:")
        for m in old_matches[:10]:  # Mostrar as 10 primeiras
            print(f"   ❌ ID {m.id:4d} | {m.scheduled_time:5s} | {m.league:7s} | {m.team_home} vs {m.team_away}")
        
        if len(old_matches) > 10:
            print(f"   ... e mais {len(old_matches) - 10} partidas")
        
        # Confirmar
        resposta = input(f"\n⚠️  Deseja remover {len(old_matches)} partidas antigas? (s/n): ")
        
        if resposta.lower() == 's':
            for match in old_matches:
                db.delete(match)
            db.commit()
            print(f"\n✅ {len(old_matches)} partidas removidas com sucesso!")
        else:
            print("\n❌ Operação cancelada")
    else:
        print("\n✅ Nenhuma partida antiga encontrada")
    
    print("="*80)
