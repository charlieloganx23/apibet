"""
Script principal para iniciar a aplicação
"""
import sys
from loguru import logger
from config import LOG_FILE, LOG_LEVEL, API_HOST, API_PORT

# Configura logging
logger.remove()  # Remove handler padrão
logger.add(sys.stdout, level=LOG_LEVEL)
logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="30 days",
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bet365 Virtual Football Scraper & API")
    parser.add_argument(
        'mode',
        choices=['api', 'scraper', 'once', 'init-db'],
        help='Modo de execução: api (inicia API), scraper (scheduler automático), once (scraping único), init-db (cria tabelas)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'init-db':
        logger.info("Inicializando banco de dados...")
        from database import init_db
        init_db()
        logger.info("✓ Banco de dados inicializado!")
        
    elif args.mode == 'once':
        logger.info("Executando scraping único...")
        from database import init_db
        from scraper import run_scraper
        init_db()
        result = run_scraper()
        # Captura valores antes da sessão fechar
        status = result.status
        matches_found = result.matches_found
        matches_new = result.matches_new
        matches_updated = result.matches_updated
        
        logger.info(f"✓ Scraping concluído: {status}")
        logger.info(f"  - Partidas encontradas: {matches_found}")
        logger.info(f"  - Novas: {matches_new}")
        logger.info(f"  - Atualizadas: {matches_updated}")
        
    elif args.mode == 'scraper':
        logger.info("Iniciando scheduler de scraping automático...")
        from scheduler import run_scheduler
        run_scheduler()
        
    elif args.mode == 'api':
        logger.info(f"Iniciando API REST em {API_HOST}:{API_PORT}...")
        from database import init_db
        import uvicorn
        from api import app
        
        init_db()
        uvicorn.run(app, host=API_HOST, port=API_PORT, log_level=LOG_LEVEL.lower())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Aplicação encerrada pelo usuário")
    except Exception as e:
        logger.exception(f"❌ Erro fatal: {e}")
        sys.exit(1)
