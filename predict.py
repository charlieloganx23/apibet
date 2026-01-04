"""
Script para fazer predições usando modelo treinado
"""

import logging
import sys
from ml_model import GoalsPredictionModel
from database_rapidapi import get_db
from models_rapidapi import Match

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


def predict_upcoming_matches():
    """Faz predições para partidas agendadas"""
    
    # Carrega modelo
    model = GoalsPredictionModel()
    try:
        model.load()
    except FileNotFoundError:
        logger.error("❌ Modelo não encontrado!")
        logger.info("   Execute primeiro: python train_model.py")
        return
    
    # Busca partidas agendadas
    with get_db() as db:
        upcoming = db.query(Match).filter(
            Match.status == "scheduled"
        ).order_by(Match.match_date).limit(10).all()
        
        if not upcoming:
            logger.info("ℹ️  Nenhuma partida agendada encontrada")
            return
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🔮 PREDIÇÕES PARA {len(upcoming)} PRÓXIMAS PARTIDAS")
        logger.info(f"{'='*80}\n")
        
        for match in upcoming:
            # Prepara dados da partida
            match_data = {
                'league': match.league,
                'odd_home': match.odd_home,
                'odd_draw': match.odd_draw,
                'odd_away': match.odd_away,
                'odd_over_25': match.odd_over_25,
                'odd_under_25': match.odd_under_25,
                'odd_both_score_yes': match.odd_both_score_yes,
                'odd_both_score_no': match.odd_both_score_no,
                'odd_exact_goals_0': match.odd_exact_goals_0,
                'odd_exact_goals_1': match.odd_exact_goals_1,
                'odd_exact_goals_2': match.odd_exact_goals_2,
                'odd_exact_goals_3': match.odd_exact_goals_3,
            }
            
            # Faz predição
            prediction = model.predict(match_data)
            
            # Exibe resultado
            logger.info(f"🏆 {match.league.upper():10s} | {match.hour}:{match.minute}")
            logger.info(f"   {match.team_home} vs {match.team_away}")
            logger.info(f"   ")
            logger.info(f"   📊 PREDIÇÃO:")
            logger.info(f"      Total de Gols: {prediction['predicted_total_goals']} gols")
            logger.info(f"      Resultado: {prediction['predicted_result'].upper()}")
            logger.info(f"      Confiança: {prediction['confidence']:.1%}")
            logger.info(f"   ")
            logger.info(f"   🎲 ODDS:")
            logger.info(f"      Casa: {match.odd_home:.2f} | Empate: {match.odd_draw:.2f} | Fora: {match.odd_away:.2f}")
            logger.info(f"      Over 2.5: {match.odd_over_25:.2f} | Under 2.5: {match.odd_under_25:.2f}")
            logger.info(f"")
            logger.info(f"   📈 Probabilidades:")
            for result, prob in prediction['result_probabilities'].items():
                logger.info(f"      {result.upper():10s}: {prob:.1%}")
            logger.info(f"\n{'-'*80}\n")


def main():
    predict_upcoming_matches()


if __name__ == "__main__":
    main()
