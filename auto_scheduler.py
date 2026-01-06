"""
Agendador Automático - Sincronização Periódica
Executa auto_sync.py automaticamente a cada intervalo definido

Uso:
    python auto_scheduler.py           # Executa a cada 30 minutos
    python auto_scheduler.py --interval 15  # Executa a cada 15 minutos
"""

import schedule
import time
import argparse
from datetime import datetime, timedelta
import logging

from auto_sync import run_full_sync

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scheduled_sync():
    """Função que será executada periodicamente"""
    local_time = datetime.now()
    site_time = local_time + timedelta(hours=4)
    
    logger.info("\n" + "="*80)
    logger.info(f"⏰ SINCRONIZAÇÃO AUTOMÁTICA INICIADA")
    logger.info(f"   Horário local: {local_time.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info(f"   Horário do site: {site_time.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("="*80 + "\n")
    
    try:
        stats = run_full_sync()
        
        logger.info("\n✅ Sincronização automática concluída com sucesso!")
        logger.info(f"   Novos jogos: {stats['scraper'].get('matches_new', 0)}")
        logger.info(f"   Jogos atualizados: {stats['scraper'].get('matches_updated', 0)}")
        logger.info(f"   Resultados coletados: {stats['results'].get('matches_updated', 0)}")
        
    except Exception as e:
        logger.error(f"\n❌ Erro na sincronização automática: {e}")


def run_scheduler(interval_minutes: int = 30):
    """
    Inicia o agendador
    
    Args:
        interval_minutes: Intervalo entre sincronizações (padrão: 30 minutos)
    """
    logger.info("\n" + "="*80)
    logger.info("🤖 AGENDADOR AUTOMÁTICO INICIADO")
    logger.info(f"   Intervalo: A cada {interval_minutes} minutos")
    logger.info(f"   Correlação de horário: Local + 4h = Site Bet365")
    logger.info("="*80 + "\n")
    
    # Agenda execução periódica
    schedule.every(interval_minutes).minutes.do(scheduled_sync)
    
    # Executa uma vez ao iniciar
    logger.info("🚀 Executando sincronização inicial...")
    scheduled_sync()
    
    # Loop infinito
    logger.info(f"\n⏰ Próxima sincronização em {interval_minutes} minutos...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Agendador automático de sincronização'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Intervalo entre sincronizações em minutos (padrão: 30)'
    )
    
    args = parser.parse_args()
    
    try:
        run_scheduler(interval_minutes=args.interval)
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Agendador interrompido pelo usuário")
        logger.info("   Até a próxima! 👋")
    except Exception as e:
        logger.error(f"\n❌ Erro fatal no agendador: {e}")
        exit(1)
