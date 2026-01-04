"""
Script para visualizar dados coletados do banco RapidAPI
"""

from database_rapidapi import get_db
from models_rapidapi import Match, ScraperLog
from sqlalchemy import func

def show_sample_matches():
    """Mostra amostra de partidas coletadas"""
    with get_db() as db:
        # Partidas agendadas
        scheduled = db.query(Match).filter(Match.status == "scheduled").limit(3).all()
        
        # Partidas finalizadas
        finished = db.query(Match).filter(Match.status == "finished").limit(3).all()
        
        print("\n" + "="*80)
        print("📊 AMOSTRA DE PARTIDAS COLETADAS")
        print("="*80 + "\n")
        
        if scheduled:
            print("🔮 PARTIDAS AGENDADAS (Próximas):")
            print("-" * 80)
            for match in scheduled:
                print(f"🏆 {match.league.upper()} | {match.scheduled_time}")
                print(f"   {match.team_home} vs {match.team_away}")
                print(f"   Odds: Casa {match.odd_home} | Empate {match.odd_draw} | Fora {match.odd_away}")
                print(f"   Over 2.5: {match.odd_over_25} | Under 2.5: {match.odd_under_25}")
                print()
        
        if finished:
            print("\n✅ PARTIDAS FINALIZADAS (Com resultado):")
            print("-" * 80)
            for match in finished:
                print(f"🏆 {match.league.upper()} | {match.scheduled_time}")
                print(f"   {match.team_home} {match.goals_home} x {match.goals_away} {match.team_away}")
                print(f"   Total de gols: {match.total_goals} | Resultado: {match.result}")
                print(f"   Odds eram: Casa {match.odd_home} | Empate {match.odd_draw} | Fora {match.odd_away}")
                print()
        
        if not scheduled and not finished:
            print("   Nenhuma partida encontrada no banco de dados.")
            print()


def show_odds_analysis():
    """Análise estatística das odds"""
    with get_db() as db:
        print("\n" + "="*80)
        print("📈 ANÁLISE DE ODDS - PADRÕES IDENTIFICADOS")
        print("="*80 + "\n")
        
        # Média de odds por liga
        for league in ["express", "copa", "super", "euro", "premier"]:
            avg_home = db.query(func.avg(Match.odd_home)).filter(Match.league == league).scalar()
            avg_draw = db.query(func.avg(Match.odd_draw)).filter(Match.league == league).scalar()
            avg_away = db.query(func.avg(Match.odd_away)).filter(Match.league == league).scalar()
            avg_over_25 = db.query(func.avg(Match.odd_over_25)).filter(Match.league == league).scalar()
            
            print(f"🏆 Liga {league.upper()}:")
            print(f"   Odd média Casa: {avg_home:.2f}")
            print(f"   Odd média Empate: {avg_draw:.2f}")
            print(f"   Odd média Fora: {avg_away:.2f}")
            print(f"   Odd média Over 2.5: {avg_over_25:.2f}")
            print()


def show_goals_probability():
    """Calcula probabilidade implícita de gols baseada nas odds"""
    with get_db() as db:
        matches = db.query(Match).limit(10).all()
        
        print("\n" + "="*80)
        print("⚽ PROBABILIDADE IMPLÍCITA DE GOLS (baseada em odds)")
        print("="*80 + "\n")
        
        for match in matches:
            # Probabilidade implícita: 1 / odd * 100
            if match.odd_over_25 and match.odd_under_25:
                prob_over_25 = (1 / match.odd_over_25) * 100
                prob_under_25 = (1 / match.odd_under_25) * 100
                
                print(f"{match.team_home} vs {match.team_away} ({match.league})")
                print(f"   Prob. Over 2.5 gols: {prob_over_25:.1f}%")
                print(f"   Prob. Under 2.5 gols: {prob_under_25:.1f}%")
                
                # Previsão simples baseada em probabilidade
                if prob_over_25 > prob_under_25:
                    print(f"   ➡️ PREVISÃO: Mais de 2.5 gols (confiança: {prob_over_25:.1f}%)")
                else:
                    print(f"   ➡️ PREVISÃO: Menos de 2.5 gols (confiança: {prob_under_25:.1f}%)")
                print()


if __name__ == "__main__":
    show_sample_matches()
    show_odds_analysis()
    show_goals_probability()
