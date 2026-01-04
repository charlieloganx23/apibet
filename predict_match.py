"""
Predição para jogo específico baseado em odds
"""

from database_rapidapi import get_db
from models_rapidapi import Match

def predict_match(hour, minute):
    """Faz predição para um jogo específico"""
    
    with get_db() as db:
        match = db.query(Match).filter(
            Match.hour == str(hour),
            Match.minute == str(minute).zfill(2),
            Match.status == "scheduled"
        ).first()
        
        if not match:
            print(f"❌ Nenhuma partida encontrada às {hour}:{minute}")
            return
        
        print(f"\n{'='*80}")
        print(f"🔮 PREDIÇÃO DE PARTIDA")
        print(f"{'='*80}\n")
        
        print(f"⏰ Horário: {match.hour}:{match.minute}")
        print(f"🏆 Liga: {match.league.upper()}")
        print(f"⚽ Partida: {match.team_home} vs {match.team_away}")
        
        # Probabilidades implícitas
        prob_home = (1 / match.odd_home) if match.odd_home else 0
        prob_draw = (1 / match.odd_draw) if match.odd_draw else 0
        prob_away = (1 / match.odd_away) if match.odd_away else 0
        prob_over_25 = (1 / match.odd_over_25) if match.odd_over_25 else 0
        prob_under_25 = (1 / match.odd_under_25) if match.odd_under_25 else 0
        prob_both_yes = (1 / match.odd_both_score_yes) if match.odd_both_score_yes else 0
        prob_both_no = (1 / match.odd_both_score_no) if match.odd_both_score_no else 0
        
        # Normaliza probabilidades (soma das 3 deve dar ~100%)
        total = prob_home + prob_draw + prob_away
        prob_home_norm = (prob_home / total) * 100 if total > 0 else 0
        prob_draw_norm = (prob_draw / total) * 100 if total > 0 else 0
        prob_away_norm = (prob_away / total) * 100 if total > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"📊 ODDS DO MERCADO")
        print(f"{'='*80}\n")
        
        print(f"🏠 Casa ({match.team_home}):")
        print(f"   Odd: {match.odd_home:.2f}")
        print(f"   Probabilidade: {prob_home_norm:.1f}%")
        
        print(f"\n🤝 Empate:")
        print(f"   Odd: {match.odd_draw:.2f}")
        print(f"   Probabilidade: {prob_draw_norm:.1f}%")
        
        print(f"\n✈️  Fora ({match.team_away}):")
        print(f"   Odd: {match.odd_away:.2f}")
        print(f"   Probabilidade: {prob_away_norm:.1f}%")
        
        print(f"\n{'='*80}")
        print(f"⚽ MERCADO DE GOLS")
        print(f"{'='*80}\n")
        
        print(f"📈 Over 2.5 gols:")
        print(f"   Odd: {match.odd_over_25:.2f}")
        print(f"   Probabilidade: {prob_over_25*100:.1f}%")
        
        print(f"\n📉 Under 2.5 gols:")
        print(f"   Odd: {match.odd_under_25:.2f}")
        print(f"   Probabilidade: {prob_under_25*100:.1f}%")
        
        print(f"\n🎯 Ambas marcam SIM:")
        print(f"   Odd: {match.odd_both_score_yes:.2f}")
        print(f"   Probabilidade: {prob_both_yes*100:.1f}%")
        
        print(f"\n🚫 Ambas marcam NÃO:")
        print(f"   Odd: {match.odd_both_score_no:.2f}")
        print(f"   Probabilidade: {prob_both_no*100:.1f}%")
        
        # Determina resultado mais provável
        print(f"\n{'='*80}")
        print(f"🎯 PREDIÇÃO FINAL")
        print(f"{'='*80}\n")
        
        # Resultado
        if prob_home_norm > prob_draw_norm and prob_home_norm > prob_away_norm:
            resultado_pred = f"Vitória da CASA ({match.team_home})"
            conf_resultado = prob_home_norm
        elif prob_away_norm > prob_home_norm and prob_away_norm > prob_draw_norm:
            resultado_pred = f"Vitória de FORA ({match.team_away})"
            conf_resultado = prob_away_norm
        else:
            resultado_pred = "EMPATE"
            conf_resultado = prob_draw_norm
        
        # Gols
        if prob_over_25 > prob_under_25:
            gols_pred = "OVER 2.5 gols (3+ gols)"
            conf_gols = prob_over_25 * 100
        else:
            gols_pred = "UNDER 2.5 gols (0-2 gols)"
            conf_gols = prob_under_25 * 100
        
        # Ambas marcam
        if prob_both_yes > prob_both_no:
            ambas_pred = "SIM - Ambos times devem marcar"
            conf_ambas = prob_both_yes * 100
        else:
            ambas_pred = "NÃO - Pelo menos um time não marca"
            conf_ambas = prob_both_no * 100
        
        print(f"1️⃣  RESULTADO:")
        print(f"   Predição: {resultado_pred}")
        print(f"   Confiança: {conf_resultado:.1f}%")
        
        print(f"\n2️⃣  TOTAL DE GOLS:")
        print(f"   Predição: {gols_pred}")
        print(f"   Confiança: {conf_gols:.1f}%")
        
        print(f"\n3️⃣  AMBAS MARCAM:")
        print(f"   Predição: {ambas_pred}")
        print(f"   Confiança: {conf_ambas:.1f}%")
        
        # Placar mais provável (baseado em odds de resultado correto)
        print(f"\n{'='*80}")
        print(f"🎲 PLACARES MAIS PROVÁVEIS")
        print(f"{'='*80}\n")
        
        placares = []
        if match.odd_correct_1_0_home:
            placares.append(("1-0 (Casa)", 1/match.odd_correct_1_0_home * 100))
        if match.odd_correct_2_0_home:
            placares.append(("2-0 (Casa)", 1/match.odd_correct_2_0_home * 100))
        if match.odd_correct_2_1_home:
            placares.append(("2-1 (Casa)", 1/match.odd_correct_2_1_home * 100))
        if match.odd_correct_0_0:
            placares.append(("0-0 (Empate)", 1/match.odd_correct_0_0 * 100))
        if match.odd_correct_1_1:
            placares.append(("1-1 (Empate)", 1/match.odd_correct_1_1 * 100))
        if match.odd_correct_2_2:
            placares.append(("2-2 (Empate)", 1/match.odd_correct_2_2 * 100))
        if match.odd_correct_1_0_away:
            placares.append(("0-1 (Fora)", 1/match.odd_correct_1_0_away * 100))
        if match.odd_correct_2_0_away:
            placares.append(("0-2 (Fora)", 1/match.odd_correct_2_0_away * 100))
        if match.odd_correct_2_1_away:
            placares.append(("1-2 (Fora)", 1/match.odd_correct_2_1_away * 100))
        
        placares.sort(key=lambda x: x[1], reverse=True)
        
        for idx, (placar, prob) in enumerate(placares[:5], 1):
            print(f"   {idx}. {placar:20s} - {prob:.1f}%")
        
        # Recomendações
        print(f"\n{'='*80}")
        print(f"💡 RECOMENDAÇÕES DE APOSTAS")
        print(f"{'='*80}\n")
        
        recomendacoes = []
        
        # Alta confiança em resultado
        if conf_resultado > 45:
            recomendacoes.append(f"✅ {resultado_pred} (confiança alta: {conf_resultado:.1f}%)")
        
        # Alta confiança em gols
        if conf_gols > 60:
            recomendacoes.append(f"✅ {gols_pred} (confiança alta: {conf_gols:.1f}%)")
        
        # Ambas marcam com alta confiança
        if conf_ambas > 60:
            recomendacoes.append(f"✅ {ambas_pred} (confiança: {conf_ambas:.1f}%)")
        
        # Jogo equilibrado
        if max(prob_home_norm, prob_draw_norm, prob_away_norm) < 40:
            recomendacoes.append("⚠️  Jogo EQUILIBRADO - resultado incerto, evite apostas em resultado final")
        
        # Value bets (odds altas com probabilidade razoável)
        if match.odd_home > 3.0 and prob_home_norm > 30:
            recomendacoes.append(f"💰 Casa tem VALUE (odd {match.odd_home:.2f} com {prob_home_norm:.1f}% probabilidade)")
        if match.odd_away > 3.0 and prob_away_norm > 30:
            recomendacoes.append(f"💰 Fora tem VALUE (odd {match.odd_away:.2f} com {prob_away_norm:.1f}% probabilidade)")
        
        if recomendacoes:
            for rec in recomendacoes:
                print(f"{rec}")
        else:
            print("ℹ️  Sem recomendações fortes - odds equilibradas")
        
        print(f"\n{'='*80}\n")
        
        # Características da liga
        print(f"📋 CARACTERÍSTICAS DA {match.league.upper()}:")
        
        with get_db() as db2:
            liga_matches = db2.query(Match).filter(
                Match.league == match.league,
                Match.status == "scheduled"
            ).all()
            
            under_count = sum(1 for m in liga_matches if m.odd_under_25 and m.odd_over_25 and (1/m.odd_under_25) > (1/m.odd_over_25))
            total_liga = len(liga_matches)
            
            if total_liga > 0:
                under_pct = (under_count / total_liga) * 100
                if under_pct > 60:
                    print(f"   🛡️  Liga DEFENSIVA - {under_pct:.0f}% das partidas favorecem Under 2.5")
                elif under_pct < 40:
                    print(f"   ⚡ Liga OFENSIVA - {100-under_pct:.0f}% das partidas favorecem Over 2.5")
                else:
                    print(f"   ⚖️  Liga EQUILIBRADA em termos de gols")
        
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        time_str = sys.argv[1]
        hour, minute = time_str.split(":")
        predict_match(hour, minute)
    else:
        # Padrão: jogo das 20:35
        predict_match("20", "35")
