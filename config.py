"""
Configurações da aplicação
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bet365_virtual.db")

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "dev-secret-key-change-in-production")

# Scraper
SCRAPER_MODE = os.getenv("SCRAPER_MODE", "rapidapi")  # 'rapidapi' (recomendado) ou 'selenium'
SCRAPER_INTERVAL_MINUTES = int(os.getenv("SCRAPER_INTERVAL_MINUTES", 5))
SCRAPER_HEADLESS = os.getenv("SCRAPER_HEADLESS", "False").lower() == "true"
SCRAPER_MANUAL_MODE = os.getenv("SCRAPER_MANUAL_MODE", "True").lower() == "true"  # Modo híbrido: permite ação manual
SCRAPER_MANUAL_TIMEOUT = int(os.getenv("SCRAPER_MANUAL_TIMEOUT", 300))  # Segundos para aguardar ação manual (5 min)
SCRAPER_USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Bet365
BET365_URL = os.getenv("BET365_URL", "https://www.bet365.com/#/AVR/B146/R^1/")
BET365_RESULTS_URL = os.getenv("BET365_RESULTS_URL", "https://extra.bet365.com/results")

# RapidAPI Configuration (Futebol Virtual Bet365)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "af63b68123msh7d090c49720fb63p1b3fe2jsn8898d9df2786")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "futebol-virtual-bet3651.p.rapidapi.com")
RAPIDAPI_LEAGUES = ["express", "copa", "super", "euro", "premier"]  # Todas as ligas disponíveis

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# Virtual Football Competitions
COMPETITIONS = [
    "CAMPEONATO MUNDIAL",
    "PREMIERSHIP",
    "SUPERLIGA"
]
