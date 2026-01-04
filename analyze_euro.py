"""
Análise de padrões em partidas da Euro Cup
Baseado nas odds (análise de mercado)
"""

import pandas as pd
from database_rapidapi import get_db
from models_rapidapi import Match

def analyze_euro_matches():
    """Analisa padrões nas partidas da Euro Cup"""
    
    with get_db() as db:
        # Busca partidas agendadas da Euro
        euro_matches = db.query(Match).filter(
            Match.league == "euro",
            Match.status == "scheduled"
        ).order_by(Match.match_date).all()
        
        if not euro_matches:
            print("❌ Nenhuma partida da Euro Cup encontrada")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 ANÁLISE DE PADRÕES - EURO CUP")
        print(f"{'='*80}\n")
        print(f"Total de partidas agendadas: {len(euro_matches)}\n")
        
        # Converte para DataFrame para análise
        data = []
        for m in euro_matches:
            # Calcula probabilidades implícitas
            prob_home = (1 / m.odd_home) if m.odd_home else 0
            prob_draw = (1 / m.odd_draw) if m.odd_draw else 0
            prob_away = (1 / m.odd_away) if m.odd_away else 0
            prob_over_25 = (1 / m.odd_over_25) if m.odd_over_25 else 0
            prob_under_25 = (1 / m.odd_under_25) if m.odd_under_25 else 0
            
            # Determina favorito
            if prob_home > prob_draw and prob_home > prob_away:
                favorito = "Casa"
                prob_favorito = prob_home
            elif prob_away > prob_home and prob_away > prob_draw:
                favorito = "Fora"
                prob_favorito = prob_away
            else:
                favorito = "Empate"
                prob_favorito = prob_draw
            
            # Predição de gols
            if prob_over_25 > prob_under_25:
                pred_gols = "Over 2.5"
                conf_gols = prob_over_25
            else:
                pred_gols = "Under 2.5"
                conf_gols = prob_under_25
            
            data.append({
                'time': f"{m.hour}:{m.minute}",
                'home': m.team_home,
                'away': m.team_away,
                'odd_home': m.odd_home,
                'odd_draw': m.odd_draw,
                'odd_away': m.odd_away,
                'odd_over_25': m.odd_over_25,
                'odd_under_25': m.odd_under_25,
                'prob_home': prob_home,
                'prob_draw': prob_draw,
                'prob_away': prob_away,
                'prob_over_25': prob_over_25,
                'prob_under_25': prob_under_25,
                'favorito': favorito,
                'prob_favorito': prob_favorito,
                'pred_gols': pred_gols,
                'conf_gols': conf_gols,
                'odd_both_yes': m.odd_both_score_yes,
                'odd_both_no': m.odd_both_score_no
            })
        
        df = pd.DataFrame(data)
        
        # ===== ANÁLISE GERAL =====
        print("🎯 PADRÕES IDENTIFICADOS:\n")
        
        # Distribuição de favoritos
        print("1️⃣  FAVORITOS:")
        fav_counts = df['favorito'].value_counts()
        for fav, count in fav_counts.items():
            pct = (count / len(df)) * 100
            print(f"   • {fav}: {count} partidas ({pct:.1f}%)")
        
        # Expectativa de gols
        print(f"\n2️⃣  EXPECTATIVA DE GOLS:")
        gols_counts = df['pred_gols'].value_counts()
        for pred, count in gols_counts.items():
            pct = (count / len(df)) * 100
            print(f"   • {pred}: {count} partidas ({pct:.1f}%)")
        
        # Estatísticas de odds
        print(f"\n3️⃣  ESTATÍSTICAS DE ODDS:")
        print(f"   • Odd Casa (média): {df['odd_home'].mean():.2f}")
        print(f"   • Odd Empate (média): {df['odd_draw'].mean():.2f}")
        print(f"   • Odd Fora (média): {df['odd_away'].mean():.2f}")
        print(f"   • Odd Over 2.5 (média): {df['odd_over_25'].mean():.2f}")
        print(f"   • Odd Under 2.5 (média): {df['odd_under_25'].mean():.2f}")
        
        # Probabilidades médias
        print(f"\n4️⃣  PROBABILIDADES IMPLÍCITAS (Médias):")
        print(f"   • Casa vencer: {df['prob_home'].mean():.1%}")
        print(f"   • Empate: {df['prob_draw'].mean():.1%}")
        print(f"   • Fora vencer: {df['prob_away'].mean():.1%}")
        print(f"   • Over 2.5 gols: {df['prob_over_25'].mean():.1%}")
        print(f"   • Under 2.5 gols: {df['prob_under_25'].mean():.1%}")
        
        # ===== PRÓXIMAS PARTIDAS COM PREDIÇÕES =====
        print(f"\n{'='*80}")
        print(f"🔮 PRÓXIMAS 5 PARTIDAS COM PREDIÇÕES BASEADAS EM ODDS")
        print(f"{'='*80}\n")
        
        for idx, row in df.head(5).iterrows():
            print(f"⚽ {row['time']} | {row['home']} vs {row['away']}")
            print(f"   Odds: Casa {row['odd_home']:.2f} | Empate {row['odd_draw']:.2f} | Fora {row['odd_away']:.2f}")
            print(f"   ")
            print(f"   📊 PREDIÇÃO:")
            print(f"      Favorito: {row['favorito']} (confiança: {row['prob_favorito']:.1%})")
            print(f"      Gols: {row['pred_gols']} (confiança: {row['conf_gols']:.1%})")
            
            # Recomendação de apostas baseada em value
            recommendations = []
            
            # Value betting: quando probabilidade implícita indica valor
            if row['prob_favorito'] > 0.60:
                recommendations.append(f"✅ {row['favorito']} tem alta probabilidade")
            
            if row['conf_gols'] > 0.65:
                recommendations.append(f"✅ {row['pred_gols']} tem alta confiança")
            
            # Ambas marcam
            prob_both_yes = (1 / row['odd_both_yes']) if row['odd_both_yes'] else 0
            prob_both_no = (1 / row['odd_both_no']) if row['odd_both_no'] else 0
            
            if prob_both_no > 0.60:
                recommendations.append("✅ Baixa probabilidade de ambas marcarem")
            elif prob_both_yes > 0.55:
                recommendations.append("✅ Boa probabilidade de ambas marcarem")
            
            if recommendations:
                print(f"   ")
                print(f"   💡 INSIGHTS:")
                for rec in recommendations:
                    print(f"      {rec}")
            
            print(f"\n{'-'*80}\n")
        
        # ===== PADRÕES GERAIS DA LIGA =====
        print(f"\n{'='*80}")
        print(f"📈 CARACTERÍSTICAS DA EURO CUP")
        print(f"{'='*80}\n")
        
        # Jogos equilibrados vs desequilibrados
        equilibrados = len(df[df['prob_favorito'] < 0.50])
        desequilibrados = len(df) - equilibrados
        
        print(f"🎲 EQUILÍBRIO DAS PARTIDAS:")
        print(f"   • Partidas equilibradas: {equilibrados} ({equilibrados/len(df)*100:.1f}%)")
        print(f"   • Partidas com favorito claro: {desequilibrados} ({desequilibrados/len(df)*100:.1f}%)")
        
        # Tendência de gols
        over_dominant = len(df[df['pred_gols'] == 'Over 2.5'])
        under_dominant = len(df[df['pred_gols'] == 'Under 2.5'])
        
        print(f"\n⚽ TENDÊNCIA DE GOLS:")
        if under_dominant > over_dominant * 1.5:
            print(f"   🛡️  Liga DEFENSIVA - Favorece Under 2.5 gols")
            print(f"      ({under_dominant/len(df)*100:.1f}% das partidas)")
        elif over_dominant > under_dominant * 1.5:
            print(f"   ⚡ Liga OFENSIVA - Favorece Over 2.5 gols")
            print(f"      ({over_dominant/len(df)*100:.1f}% das partidas)")
        else:
            print(f"   ⚖️  Liga EQUILIBRADA em termos de gols")
        
        print(f"\n{'='*80}\n")
        
        # Retorna DataFrame para uso futuro
        return df


if __name__ == "__main__":
    df = analyze_euro_matches()
