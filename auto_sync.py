"""
Sistema de Sincronização Automática
Executa todas as tarefas de atualização em sequência:
1. Atualiza status das partidas (usando offset +4h)
2. Coleta novos jogos via scraper
3. Coleta resultados de jogos finalizados
4. Atualiza status novamente após coleta

IMPORTANTE: Horário local + 4h = Horário do site Bet365
Se no seu PC é 12:22, no site são 16:22
"""

import logging
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database_rapidapi import get_db
from models_rapidapi import Match
from scraper_rapidapi import RapidAPIScraper
from results_collector import ResultsCollector
from config import RAPIDAPI_LEAGUES

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_match_statuses(db: Session) -> Dict[str, int]:
    """
    Atualiza status de todas as partidas baseado no horário do site (+4h)
    
    Returns:
        Dicionário com contadores de status
    """
    logger.info("🕐 Atualizando status das partidas...")
    
    # Horário do site (local + 4h)
    site_time = datetime.now() + timedelta(hours=4)
    logger.info(f"   Horário local: {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"   Horário do site: {site_time.strftime('%H:%M:%S')}")
    
    # Busca todas as partidas sem resultado
    matches = db.query(Match).filter(
        Match.result == None
    ).all()
    
    scheduled = 0
    live = 0
    expired = 0
    finished = 0
    
    for match in matches:
        try:
            # Parse horário da partida
            if not match.scheduled_time:
                continue
            
            # Formato: "HH:MM" ou "H:MM"
            time_parts = match.scheduled_time.split(':')
            if len(time_parts) != 2:
                continue
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            # Cria datetime da partida no horário do site
            match_datetime = site_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Se o horário da partida já passou hoje, pode ser amanhã
            if match_datetime < site_time:
                # Verifica se a diferença é maior que 12 horas (provavelmente é amanhã)
                time_diff = (site_time - match_datetime).total_seconds() / 60
                if time_diff > 720:  # 12 horas
                    match_datetime = match_datetime + timedelta(days=1)
            
            # Calcula diferença em minutos
            time_diff_minutes = (match_datetime - site_time).total_seconds() / 60
            
            # Define status baseado na diferença
            old_status = match.status
            
            if time_diff_minutes > 120:  # Mais de 2h no futuro
                match.status = "scheduled"
                scheduled += 1
            elif time_diff_minutes > -30:  # Entre 2h antes e 30min depois
                match.status = "live"
                live += 1
            else:  # Mais de 30min atrás
                if match.goals_home is not None and match.goals_away is not None:
                    match.status = "finished"
                    finished += 1
                else:
                    match.status = "expired"
                    expired += 1
            
            # Log mudanças
            if old_status != match.status:
                logger.debug(
                    f"   {match.team_home} vs {match.team_away} ({match.scheduled_time}): "
                    f"{old_status} → {match.status}"
                )
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar partida {match.id}: {e}")
            continue
    
    db.commit()
    
    logger.info(f"   ✅ Status atualizados:")
    logger.info(f"      📅 Agendados: {scheduled}")
    logger.info(f"      🔴 Ao vivo: {live}")
    logger.info(f"      ⏰ Expirados: {expired}")
    logger.info(f"      ✅ Finalizados: {finished}")
    
    return {
        "scheduled": scheduled,
        "live": live,
        "expired": expired,
        "finished": finished
    }


def run_full_sync(leagues: list = None) -> Dict:
    """
    Executa sincronização completa:
    1. Atualiza status
    2. Coleta novos jogos
    3. Coleta resultados
    4. Atualiza status novamente
    
    Args:
        leagues: Lista de ligas (None = todas)
    
    Returns:
        Estatísticas completas
    """
    if leagues is None:
        leagues = RAPIDAPI_LEAGUES
    
    logger.info("\n" + "="*80)
    logger.info("🔄 INICIANDO SINCRONIZAÇÃO AUTOMÁTICA")
    logger.info(f"   Ligas: {', '.join(leagues)}")
    logger.info(f"   Horário local: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info(f"   Horário do site: {(datetime.now() + timedelta(hours=4)).strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("="*80 + "\n")
    
    stats = {}
    
    try:
        # 1. Atualiza status inicial
        logger.info("📌 PASSO 1/4: Atualizando status das partidas...")
        with get_db() as db:
            stats['status_before'] = update_match_statuses(db)
        
        # 2. Coleta novos jogos
        logger.info("\n📌 PASSO 2/4: Coletando novos jogos...")
        scraper = RapidAPIScraper()
        stats['scraper'] = scraper.scrape_all_leagues(leagues)
        
        # 3. Coleta resultados
        logger.info("\n📌 PASSO 3/4: Coletando resultados...")
        collector = ResultsCollector()
        stats['results'] = collector.collect_all_results(leagues)
        
        # 4. Atualiza status final
        logger.info("\n📌 PASSO 4/4: Atualizando status final...")
        with get_db() as db:
            stats['status_after'] = update_match_statuses(db)
        
        # Resumo final
        logger.info("\n" + "="*80)
        logger.info("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO")
        logger.info("="*80)
        logger.info("\n📊 RESUMO:")
        logger.info(f"   Novos jogos coletados: {stats['scraper'].get('new_matches', 0)}")
        logger.info(f"   Jogos atualizados: {stats['scraper'].get('updated_matches', 0)}")
        logger.info(f"   Resultados coletados: {stats['results'].get('matches_updated', 0)}")
        logger.info(f"   Jogos expirados: {stats['status_after'].get('expired', 0)}")
        logger.info(f"   Jogos finalizados: {stats['status_after'].get('finished', 0)}")
        logger.info("="*80 + "\n")
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ ERRO NA SINCRONIZAÇÃO: {e}")
        raise


if __name__ == "__main__":
    """
    Executa sincronização completa
    
    Uso:
        python auto_sync.py
    """
    try:
        stats = run_full_sync()
        print("\n✅ Sincronização automática concluída!")
        print(f"📊 Estatísticas salvas em: {stats}")
        
    except Exception as e:
        print(f"\n❌ Erro na sincronização: {e}")
        exit(1)
