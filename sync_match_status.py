"""
Script para sincronizar status das partidas baseado em horário atual
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_rapidapi import Match
from datetime import datetime, timedelta
import random

# Conectar ao banco CORRETO
engine = create_engine('sqlite:///bet365_rapidapi.db')
Session = sessionmaker(bind=engine)
session = Session()

print("🔄 Sincronizando status das partidas...")
print(f"⏰ Horário atual: {datetime.now().strftime('%H:%M')}")

# Pegar hora atual
now = datetime.now()
current_time_minutes = now.hour * 60 + now.minute

# Buscar partidas sem resultado
matches_without_result = session.query(Match).filter(
    Match.result.is_(None),
    Match.status == 'scheduled'
).all()

print(f"\n📊 Partidas sem resultado: {len(matches_without_result)}")

# Verificar quais deveriam estar finalizadas (passou 2h do horário)
expired_matches = []
for match in matches_without_result:
    # Garantir que hour e minute são inteiros
    try:
        hour = int(match.hour) if match.hour else 0
        minute = int(match.minute) if match.minute else 0
        match_time_minutes = hour * 60 + minute
        time_diff_minutes = current_time_minutes - match_time_minutes
        
        # Se passou mais de 2 horas (120 minutos)
        if time_diff_minutes > 120:
            expired_matches.append(match)
    except (ValueError, TypeError) as e:
        print(f"⚠️ Erro ao processar partida {match.id}: {e}")
        continue

print(f"⏰ Partidas com horário vencido (>2h): {len(expired_matches)}")

if expired_matches:
    print("\n📋 Partidas que deveriam ter resultado:")
    for match in expired_matches[:10]:  # Mostrar primeiras 10
        print(f"   • {match.hour:02d}:{match.minute:02d} - {match.league} - {match.team_home} vs {match.team_away}")
    
    # Perguntar se quer gerar resultados simulados
    print(f"\n💡 Encontradas {len(expired_matches)} partidas com horário passado")
    response = input("Deseja gerar resultados simulados para estas partidas? (s/n): ")
    
    if response.lower() == 's':
        print("\n🎲 Gerando resultados simulados...")
        updated = 0
        
        for match in expired_matches:
            # Determinar vencedor baseado nas odds (favorito tem mais chance)
            odds = [match.odd_home, match.odd_draw, match.odd_away]
            min_odd = min(odds)
            
            # Favorito tem 60% de chance, empate 20%, azarão 20%
            rand = random.random()
            
            if min_odd == match.odd_home:
                # Casa é favorito
                if rand < 0.6:
                    result = 'home'
                    score_home = random.randint(1, 4)
                    score_away = random.randint(0, score_home - 1)
                elif rand < 0.8:
                    result = 'draw'
                    score = random.randint(0, 3)
                    score_home = score
                    score_away = score
                else:
                    result = 'away'
                    score_away = random.randint(1, 4)
                    score_home = random.randint(0, score_away - 1)
            elif min_odd == match.odd_draw:
                # Empate é favorito
                if rand < 0.6:
                    result = 'draw'
                    score = random.randint(0, 3)
                    score_home = score
                    score_away = score
                elif rand < 0.8:
                    result = 'home'
                    score_home = random.randint(1, 3)
                    score_away = random.randint(0, 3)
                else:
                    result = 'away'
                    score_away = random.randint(1, 3)
                    score_home = random.randint(0, 3)
            else:
                # Fora é favorito
                if rand < 0.6:
                    result = 'away'
                    score_away = random.randint(1, 4)
                    score_home = random.randint(0, score_away - 1)
                elif rand < 0.8:
                    result = 'draw'
                    score = random.randint(0, 3)
                    score_home = score
                    score_away = score
                else:
                    result = 'home'
                    score_home = random.randint(1, 4)
                    score_away = random.randint(0, score_home - 1)
            
            # Atualizar partida
            match.result = result
            match.goals_home = score_home
            match.goals_away = score_away
            match.total_goals = score_home + score_away
            match.status = 'finished'
            
            updated += 1
        
        session.commit()
        print(f"✅ {updated} partidas atualizadas com resultados simulados!")
        
        # Mostrar estatísticas
        finished_count = session.query(Match).filter(Match.status == 'finished').count()
        scheduled_count = session.query(Match).filter(Match.status == 'scheduled').count()
        total_count = session.query(Match).count()
        
        print(f"\n📊 Estatísticas atualizadas:")
        print(f"   • Total: {total_count}")
        print(f"   • Finalizadas: {finished_count}")
        print(f"   • Agendadas: {scheduled_count}")
    else:
        print("❌ Operação cancelada")
else:
    print("\n✅ Nenhuma partida com horário vencido encontrada")

# Mostrar últimas partidas finalizadas
print("\n🏆 Últimas 5 partidas finalizadas:")
last_finished = session.query(Match).filter(
    Match.status == 'finished'
).order_by(Match.hour.desc(), Match.minute.desc()).limit(5).all()

for match in last_finished:
    hour = int(match.hour) if match.hour else 0
    minute = int(match.minute) if match.minute else 0
    goals_home = match.goals_home if match.goals_home is not None else 0
    goals_away = match.goals_away if match.goals_away is not None else 0
    print(f"   • {hour:02d}:{minute:02d} - {match.league} - {match.team_home} {goals_home}x{goals_away} {match.team_away}")

session.close()
