"""
Verificar se os dados estão atualizados
"""
from datetime import datetime, timedelta
from database_rapidapi import get_db
from models_rapidapi import Match
from sqlalchemy import func, desc

with get_db() as db:
    # Horários
    local_time = datetime.now()
    site_time = local_time + timedelta(hours=4)
    
    print("="*80)
    print("🕐 VERIFICAÇÃO DE ATUALIZAÇÃO DOS DADOS")
    print("="*80)
    print(f"⏰ Horário LOCAL: {local_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌐 Horário do SITE: {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*80)
    
    # Última atualização
    last_scraped = db.query(func.max(Match.scraped_at)).scalar()
    if last_scraped:
        time_since = datetime.now() - last_scraped
        print(f"\n📅 Última atualização dos dados: {last_scraped.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏱️  Tempo desde última atualização: {int(time_since.total_seconds()/60)} minutos atrás")
    
    # Total de partidas
    total = db.query(func.count(Match.id)).scalar()
    finished = db.query(func.count(Match.id)).filter(
        Match.goals_home.isnot(None),
        Match.goals_away.isnot(None)
    ).scalar()
    scheduled = total - finished
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total: {total}")
    print(f"   ✅ Finalizadas: {finished}")
    print(f"   📅 Agendadas: {scheduled}")
    
    # Últimas 10 partidas no banco (por ID)
    print(f"\n🆕 ÚLTIMAS 10 PARTIDAS INSERIDAS (por ID):")
    for m in db.query(Match).order_by(Match.id.desc()).limit(10):
        status_icon = "✅" if m.goals_home is not None else "📅"
        goals = f"{m.goals_home}x{m.goals_away}" if m.goals_home is not None else "vs"
        print(f"   {status_icon} ID {m.id:4d} | {m.scheduled_time:5s} | {m.league:7s} | {m.team_home} {goals} {m.team_away}")
    
    # Próximas 5 partidas por horário
    print(f"\n⏭️  PRÓXIMAS 5 PARTIDAS (por horário):")
    all_scheduled = db.query(Match).filter(
        Match.goals_home.is_(None)
    ).all()
    
    # Ordenar manualmente por horário
    def get_time_minutes(match):
        if match.scheduled_time:
            parts = match.scheduled_time.split('.')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        return 0
    
    sorted_matches = sorted(all_scheduled, key=get_time_minutes)
    
    for m in sorted_matches[:5]:
        match_time = get_time_minutes(m)
        site_time_minutes = site_time.hour * 60 + site_time.minute
        diff = match_time - site_time_minutes
        
        if diff < 0:
            diff_str = f"passou há {abs(diff)} min"
        else:
            diff_str = f"em {diff} min"
        
        print(f"   📅 {m.scheduled_time:5s} ({diff_str:20s}) | {m.league:7s} | {m.team_home} vs {m.team_away}")
    
    # Últimas 5 finalizadas
    print(f"\n🏆 ÚLTIMAS 5 FINALIZADAS:")
    for m in db.query(Match).filter(
        Match.goals_home.isnot(None)
    ).order_by(Match.id.desc()).limit(5):
        print(f"   ✅ ID {m.id:4d} | {m.scheduled_time:5s} | {m.league:7s} | {m.team_home} {m.goals_home}x{m.goals_away} {m.team_away}")
    
    print("\n" + "="*80)
    
    # Verificar se precisa sincronizar
    if last_scraped:
        time_since_minutes = int(time_since.total_seconds()/60)
        if time_since_minutes > 30:
            print("⚠️  RECOMENDAÇÃO: Execute a sincronização (dados com mais de 30 min)")
            print("   Comando: python auto_sync.py")
        else:
            print("✅ Dados estão relativamente atualizados")
    
    print("="*80)
