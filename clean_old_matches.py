"""
Limpar partidas antigas - mantém apenas últimas 24 horas
Remove TODAS as partidas (com ou sem resultado) que passaram há mais de 24 horas
"""
from datetime import datetime, timedelta
from database_rapidapi import get_db
from models_rapidapi import Match

with get_db() as db:
    now_local = datetime.now()
    site_time = now_local + timedelta(hours=4)
    cutoff_time = site_time - timedelta(minutes=30)  # 30 minutos atrás
    
    print("="*80)
    print("🧹 LIMPEZA DE PARTIDAS ANTIGAS - ÚLTIMOS 30MIN")
    print("="*80)
    print(f"⏰ Horário LOCAL: {now_local.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌐 Horário do SITE: {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"⏱️  Limite (30min atrás): {cutoff_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("\n🔧 Modo: Remover TODAS as partidas antigas (com ou sem resultado)")
    
    # Buscar TODAS as partidas (com ou sem resultado)
    all_matches = db.query(Match).all()
    
    old_matches = []
    for match in all_matches:
        if not match.scheduled_time:
            continue
        
        try:
            # Parse do scheduled_time (formato: "HH.MM")
            parts = match.scheduled_time.split('.')
            if len(parts) != 2:
                continue
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            # Criar datetime para a partida (assumindo hoje ou ontem)
            match_time = site_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Se a hora da partida é maior que a hora atual, assumimos que é de ontem
            if match_time > site_time:
                match_time = match_time - timedelta(days=1)
            
            # Verificar se passou do limite (30min)
            if match_time < cutoff_time:
                hours_ago = (site_time - match_time).total_seconds() / 3600
                has_result = (match.goals_home is not None and match.goals_away is not None)
                result_str = f"{match.goals_home}x{match.goals_away}" if has_result else "Sem resultado"
                
                old_matches.append({
                    'match': match,
                    'time': match_time,
                    'hours_ago': hours_ago,
                    'result': result_str
                })
        except Exception as e:
            continue
    
    print(f"\n📋 Partidas antigas encontradas: {len(old_matches)}")
    
    if len(old_matches) > 0:
        print("\n🗑️  Partidas a serem removidas:")
        for item in old_matches[:15]:  # Mostrar as 15 primeiras
            m = item['match']
            print(f"   ❌ ID {m.id:4d} | {m.scheduled_time:5s} | {m.league:7s} | {m.team_home} vs {m.team_away}")
            print(f"      ⏱️  {item['result']} | Passou há {item['hours_ago']:.1f} horas")
        
        if len(old_matches) > 15:
            print(f"   ... e mais {len(old_matches) - 15} partidas")
        
        # Confirmar
        resposta = input(f"\n⚠️  Deseja remover {len(old_matches)} partidas antigas? (s/n): ")
        
        if resposta.lower() == 's':
            for item in old_matches:
                db.delete(item['match'])
            db.commit()
            
            # Verificar quantas partidas restaram
            remaining = db.query(Match).count()
            print(f"\n✅ {len(old_matches)} partidas removidas com sucesso!")
            print(f"📊 Partidas restantes no banco: {remaining}")
        else:
            print("\n❌ Operação cancelada")
    else:
        print("\n✅ Nenhuma partida antiga encontrada")
    
    print("="*80)
