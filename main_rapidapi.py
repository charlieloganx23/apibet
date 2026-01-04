"""
Script principal para usar o novo scraper RapidAPI
Substitui o main.py antigo (Selenium) por versão muito mais eficiente!
"""

import sys
import time
import logging
from datetime import datetime

from database_rapidapi import init_db, get_db
from scraper_rapidapi import run_rapidapi_scraper
from results_collector import run_results_collector
from models_rapidapi import Match, ScraperLog
from config import SCRAPER_INTERVAL_MINUTES, RAPIDAPI_LEAGUES

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def show_statistics():
    """Mostra estatísticas do banco de dados"""
    with get_db() as db:
        total_matches = db.query(Match).count()
        finished_matches = db.query(Match).filter(Match.status == "finished").count()
        scheduled_matches = db.query(Match).filter(Match.status == "scheduled").count()
        total_logs = db.query(ScraperLog).count()
        
        # Partidas por liga
        logger.info(f"\n{'='*60}")
        logger.info("📊 ESTATÍSTICAS DO BANCO DE DADOS")
        logger.info(f"{'='*60}")
        logger.info(f"   Total de partidas: {total_matches}")
        logger.info(f"   • Finalizadas (com resultado): {finished_matches}")
        logger.info(f"   • Agendadas (sem resultado): {scheduled_matches}")
        logger.info(f"   Total de execuções: {total_logs}")
        
        for league in RAPIDAPI_LEAGUES:
            count = db.query(Match).filter(Match.league == league).count()
            finished = db.query(Match).filter(
                Match.league == league,
                Match.status == "finished"
            ).count()
            logger.info(f"   Liga {league:8s}: {count} partidas ({finished} finalizadas)")
        
        # Última execução
        last_log = db.query(ScraperLog).order_by(ScraperLog.started_at.desc()).first()
        if last_log:
            logger.info(f"\n   Última execução:")
            logger.info(f"   • Status: {last_log.status}")
            logger.info(f"   • Partidas: {last_log.matches_found}")
            logger.info(f"   • Novas: {last_log.matches_new}")
            logger.info(f"   • Data: {last_log.started_at}")
        
        logger.info(f"{'='*60}\n")


def run_results_collection(leagues=None):
    """
    Coleta resultados de partidas finalizadas
    
    Args:
        leagues: Lista de ligas (None = todas)
    """
    logger.info("🏆 Modo: Coleta de resultados históricos\n")
    
    result = run_results_collector(leagues=leagues)
    
    show_statistics()
    
    return result


def run_once(leagues=None):
    """
    Executa coleta uma única vez
    
    Args:
        leagues: Lista de ligas (None = todas)
    """
    logger.info("🎯 Modo: Execução única\n")
    
    result = run_rapidapi_scraper(leagues=leagues)
    
    show_statistics()
    
    return result


def run_continuous(leagues=None):
    """
    Executa coleta continuamente com intervalo configurado
    Coleta tanto próximas partidas quanto resultados históricos
    
    Args:
        leagues: Lista de ligas (None = todas)
    """
    logger.info(f"♾️  Modo: Execução contínua (intervalo: {SCRAPER_INTERVAL_MINUTES} minutos)\n")
    logger.info("   Coleta próximas partidas + resultados históricos")
    logger.info("   Pressione Ctrl+C para parar\n")
    
    execution_count = 0
    
    try:
        while True:
            execution_count += 1
            logger.info(f"🔄 Execução #{execution_count}")
            
            # 1. Coleta próximas partidas (com odds)
            logger.info("📋 Etapa 1/2: Coletando próximas partidas...")
            result_next = run_rapidapi_scraper(leagues=leagues)
            
            # 2. Coleta resultados históricos
            logger.info("\n📋 Etapa 2/2: Coletando resultados históricos...")
            result_hist = run_results_collector(leagues=leagues)
            
            # Resumo combinado
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ CICLO COMPLETO #{execution_count}")
            logger.info(f"   Próximas: {result_next['matches_found']} ({result_next['matches_new']} novas)")
            logger.info(f"   Resultados: {result_hist['results_found']} ({result_hist['matches_updated']} atualizadas)")
            logger.info(f"{'='*60}\n")
            
            if execution_count % 5 == 0:  # Mostra stats a cada 5 execuções
                show_statistics()
            
            logger.info(f"⏸️  Aguardando {SCRAPER_INTERVAL_MINUTES} minutos até próxima execução...\n")
            time.sleep(SCRAPER_INTERVAL_MINUTES * 60)
            
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Execução interrompida pelo usuário")
        show_statistics()


def main():
    """Função principal"""
    
    # Banner
    logger.info("\n" + "="*60)
    logger.info("🚀 SCRAPER RAPIDAPI - FUTEBOL VIRTUAL BET365")
    logger.info("="*60 + "\n")
    
    # Inicializa banco de dados
    logger.info("🗄️  Inicializando banco de dados...")
    init_db()
    logger.info("✅ Banco de dados pronto!\n")
    
    # Verifica argumentos
    if len(sys.argv) < 2:
        logger.error("❌ Modo de execução não especificado!")
        logger.info("\nUso:")
        logger.info("  python main_rapidapi.py once              # Coleta próximas partidas")
        logger.info("  python main_rapidapi.py results           # Coleta resultados históricos")
        logger.info("  python main_rapidapi.py continuous        # Executa continuamente")
        logger.info("  python main_rapidapi.py once euro,copa    # Ligas específicas")
        logger.info("  python main_rapidapi.py stats             # Mostra estatísticas")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    # Ligas específicas (opcional)
    leagues = None
    if len(sys.argv) > 2:
        leagues = [l.strip() for l in sys.argv[2].split(",")]
        logger.info(f"🎯 Ligas selecionadas: {', '.join(leagues)}\n")
    
    # Executa modo apropriado
    if mode == "once":
        run_once(leagues=leagues)
    
    elif mode == "results":
        run_results_collection(leagues=leagues)
    
    elif mode == "continuous":
        run_continuous(leagues=leagues)
    
    elif mode == "stats":
        show_statistics()
    
    else:
        logger.error(f"❌ Modo inválido: {mode}")
        logger.info("   Modos disponíveis: once, results, continuous, stats")
        sys.exit(1)


if __name__ == "__main__":
    main()
