"""
Script para treinar e testar o modelo de ML
"""

import logging
from ml_model import GoalsPredictionModel
from database_rapidapi import init_db

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Treina e salva o modelo"""
    
    # Inicializa DB
    init_db()
    
    # Cria instância do modelo
    model = GoalsPredictionModel()
    
    try:
        # Treina modelo
        metrics = model.train(test_size=0.2, random_state=42)
        
        # Salva modelo
        model.save()
        
        logger.info("\n✅ Treinamento concluído!")
        logger.info(f"   MAE (gols): {metrics['mae_goals']:.2f}")
        logger.info(f"   Acurácia (gols exatos): {metrics['accuracy_goals']:.2%}")
        logger.info(f"   Acurácia (resultado): {metrics['accuracy_result']:.2%}")
        
    except ValueError as e:
        logger.error(f"\n❌ ERRO: {str(e)}")
        logger.info("\n💡 SOLUÇÃO:")
        logger.info("   1. Execute: python main_rapidapi.py continuous")
        logger.info("   2. Aguarde algumas horas para coletar dados históricos")
        logger.info("   3. Tente treinar o modelo novamente")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
