"""
Scheduler para executar scraper automaticamente
"""
import schedule
import time
from loguru import logger
from datetime import datetime

from config import SCRAPER_INTERVAL_MINUTES
from scraper import run_scraper
from database import init_db


def scheduled_scraping():
    """Função que será executada periodicamente"""
    logger.info(f"Iniciando scraping agendado - {datetime.now()}")
    try:
        result = run_scraper()
        logger.info(f"Scraping concluído: {result.status}")
    except Exception as e:
        logger.error(f"Erro no scraping agendado: {e}")


def run_scheduler():
    """Inicia o scheduler"""
    logger.info(f"Iniciando scheduler - Intervalo: {SCRAPER_INTERVAL_MINUTES} minutos")
    
    # Inicializa banco
    init_db()
    
    # Agenda execução
    schedule.every(SCRAPER_INTERVAL_MINUTES).minutes.do(scheduled_scraping)
    
    # Executa uma vez ao iniciar
    logger.info("Executando scraping inicial...")
    scheduled_scraping()
    
    # Loop infinito
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto


if __name__ == "__main__":
    from loguru import logger
    from config import LOG_FILE, LOG_LEVEL
    
    # Configura logging
    logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="30 days",
        level=LOG_LEVEL
    )
    
    run_scheduler()
