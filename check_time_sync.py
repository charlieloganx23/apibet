"""
Verificador de status e horários
Mostra como está a correlação entre horário local e horário do site
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from database_rapidapi import get_db
from models_rapidapi import Match

def check_time_sync():
    """Verifica correlação de horários"""
    
    local_time = datetime.now()
    site_time = local_time + timedelta(hours=4)
    
    print("\n" + "="*80)
    print("🕐 VERIFICAÇÃO DE HORÁRIOS")
    print("="*80)
    print(f"⏰ Horário LOCAL do computador: {local_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌐 Horário do SITE Bet365:     {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📊 Diferença:                  +4 horas")
    print("="*80 + "\n")
    
    with get_db() as db:
        # Total de partidas
        total = db.query(func.count(Match.id)).scalar()
        
        # Por status
        scheduled = db.query(func.count(Match.id)).filter(Match.status == 'scheduled').scalar()
        live = db.query(func.count(Match.id)).filter(Match.status == 'live').scalar()
        expired = db.query(func.count(Match.id)).filter(Match.status == 'expired').scalar()
        finished = db.query(func.count(Match.id)).filter(Match.status == 'finished').scalar()
        
        print("📊 RESUMO DAS PARTIDAS:")
        print(f"   Total no banco: {total}")
        print(f"   📅 Agendados: {scheduled}")
        print(f"   🔴 Ao vivo: {live}")
        print(f"   ⏰ Expirados (aguardando resultado): {expired}")
        print(f"   ✅ Finalizados (com resultado): {finished}")
        print()
        
        # Próximas 5 partidas
        print("🎮 PRÓXIMAS 5 PARTIDAS:")
        next_matches = db.query(Match).filter(
            Match.status.in_(['scheduled', 'live'])
        ).order_by(Match.scheduled_time).limit(5).all()
        
        for match in next_matches:
            status_icon = "🔴" if match.status == 'live' else "📅"
            print(f"   {status_icon} {match.scheduled_time} - {match.league.upper()}")
            print(f"      {match.team_home} vs {match.team_away}")
            print(f"      Odds: Casa {match.odd_home} | Empate {match.odd_draw} | Fora {match.odd_away}")
            print()
        
        # Últimas 5 finalizadas
        print("✅ ÚLTIMAS 5 PARTIDAS FINALIZADAS:")
        last_finished = db.query(Match).filter(
            Match.status == 'finished'
        ).order_by(Match.id.desc()).limit(5).all()
        
        if last_finished:
            for match in last_finished:
                winner = ""
                if match.result == 'home':
                    winner = f"🏆 {match.team_home} venceu"
                elif match.result == 'away':
                    winner = f"🏆 {match.team_away} venceu"
                else:
                    winner = "🤝 Empate"
                
                print(f"   ✅ {match.scheduled_time} - {match.league.upper()}")
                print(f"      {match.team_home} {match.goals_home} x {match.goals_away} {match.team_away}")
                print(f"      {winner}")
                print()
        else:
            print("   Nenhuma partida finalizada ainda")
            print()
        
        # Partidas expiradas
        if expired > 0:
            print(f"⏰ PARTIDAS EXPIRADAS (aguardando resultado): {expired}")
            expired_matches = db.query(Match).filter(
                Match.status == 'expired'
            ).order_by(Match.scheduled_time).limit(5).all()
            
            for match in expired_matches:
                print(f"   ⏰ {match.scheduled_time} - {match.league.upper()}")
                print(f"      {match.team_home} vs {match.team_away}")
                print()

if __name__ == "__main__":
    check_time_sync()
