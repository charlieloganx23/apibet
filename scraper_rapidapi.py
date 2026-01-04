"""
Scraper usando RapidAPI - Futebol Virtual Bet365
Sem CAPTCHA, sem Selenium, dados estruturados em JSON!
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from rapid_api_client import RapidAPIClient
from models_rapidapi import Match, ScraperLog, Base
from database_rapidapi import get_db
from config import (
    RAPIDAPI_KEY,
    RAPIDAPI_HOST,
    RAPIDAPI_LEAGUES
)

logger = logging.getLogger(__name__)


class RapidAPIScraper:
    """Scraper usando RapidAPI - muito mais eficiente que Selenium!"""
    
    def __init__(self):
        self.client = RapidAPIClient(
            api_key=RAPIDAPI_KEY,
            api_host=RAPIDAPI_HOST
        )
    
    def _parse_odds_value(self, value: str) -> Optional[float]:
        """Converte string de odd para float"""
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _extract_match_data(self, match_data: Dict, league: str) -> Dict:
        """
        Extrai e normaliza dados de uma partida
        
        Args:
            match_data: Dados brutos da API
            league: Liga da partida
        
        Returns:
            Dicionário com dados normalizados
        """
        odds = match_data.get("odds", {})
        
        return {
            "external_id": match_data.get("id"),
            "league": league,
            "team_home": match_data.get("timeA"),
            "team_away": match_data.get("timeB"),
            "hour": match_data.get("hora"),
            "minute": match_data.get("minuto"),
            "scheduled_time": match_data.get("horario"),
            
            # Odds - Resultado Final
            "odd_home": self._parse_odds_value(odds.get("odd_resultado_final_casa")),
            "odd_draw": self._parse_odds_value(odds.get("odd_resultado_final_empate")),
            "odd_away": self._parse_odds_value(odds.get("odd_resultado_final_fora")),
            
            # Odds - Over/Under
            "odd_over_05": self._parse_odds_value(odds.get("odd_over_0.5")),
            "odd_under_05": self._parse_odds_value(odds.get("odd_under_0.5")),
            "odd_over_15": self._parse_odds_value(odds.get("odd_over_1.5")),
            "odd_under_15": self._parse_odds_value(odds.get("odd_under_1.5")),
            "odd_over_25": self._parse_odds_value(odds.get("odd_over_2.5")),
            "odd_under_25": self._parse_odds_value(odds.get("odd_under_2.5")),
            "odd_over_35": self._parse_odds_value(odds.get("odd_over_3.5")),
            "odd_under_35": self._parse_odds_value(odds.get("odd_under_3.5")),
            
            # Odds - Ambas Marcam
            "odd_both_score_yes": self._parse_odds_value(odds.get("odd_ambas_sim")),
            "odd_both_score_no": self._parse_odds_value(odds.get("odd_ambas_nao")),
            
            # Odds - Resultado Correto
            "odd_correct_1_0_home": self._parse_odds_value(odds.get("odd_resultado_correto_casa_1-0")),
            "odd_correct_0_0": self._parse_odds_value(odds.get("odd_resultado_correto_empate_0-0")),
            "odd_correct_1_0_away": self._parse_odds_value(odds.get("odd_resultado_correto_fora_1-0")),
            "odd_correct_2_0_home": self._parse_odds_value(odds.get("odd_resultado_correto_casa_2-0")),
            "odd_correct_1_1": self._parse_odds_value(odds.get("odd_resultado_correto_empate_1-1")),
            "odd_correct_2_0_away": self._parse_odds_value(odds.get("odd_resultado_correto_fora_2-0")),
            "odd_correct_2_1_home": self._parse_odds_value(odds.get("odd_resultado_correto_casa_2-1")),
            "odd_correct_2_2": self._parse_odds_value(odds.get("odd_resultado_correto_empate_2-2")),
            "odd_correct_2_1_away": self._parse_odds_value(odds.get("odd_resultado_correto_fora_2-1")),
            
            # Odds - Dupla Hipótese
            "odd_double_home_draw": self._parse_odds_value(odds.get("odd_dupla_hipotese_casa_ou_empate")),
            "odd_double_away_draw": self._parse_odds_value(odds.get("odd_dupla_hipotese_fora_ou_empate")),
            "odd_double_home_away": self._parse_odds_value(odds.get("odd_dupla_hipotese_casa_ou_fora")),
            
            # Odds - Total de Gols Exatos
            "odd_exact_goals_0": self._parse_odds_value(odds.get("odd_total_gols_extatos_0")),
            "odd_exact_goals_1": self._parse_odds_value(odds.get("odd_total_gols_extatos_1")),
            "odd_exact_goals_2": self._parse_odds_value(odds.get("odd_total_gols_extatos_2")),
            "odd_exact_goals_3": self._parse_odds_value(odds.get("odd_total_gols_extatos_3")),
            "odd_exact_goals_4": self._parse_odds_value(odds.get("odd_total_gols_extatos_4")),
            "odd_exact_goals_5": self._parse_odds_value(odds.get("odd_total_gols_extatos_5")),
            
            # Odds - Intervalo
            "odd_halftime_home": self._parse_odds_value(odds.get("odd_intervalo_resultado_casa")),
            "odd_halftime_draw": self._parse_odds_value(odds.get("odd_intervalo_resultado_empate")),
            "odd_halftime_away": self._parse_odds_value(odds.get("odd_intervalo_resultado_fora")),
            
            # Odds - Gols por Time
            "odd_home_goals_0": self._parse_odds_value(odds.get("odd_time_gols_casa_0")),
            "odd_home_goals_1": self._parse_odds_value(odds.get("odd_time_gols_casa_1")),
            "odd_home_goals_2": self._parse_odds_value(odds.get("odd_time_gols_casa_2")),
            "odd_home_goals_3": self._parse_odds_value(odds.get("odd_time_gols_casa_3")),
            "odd_away_goals_0": self._parse_odds_value(odds.get("odd_time_gols_fora_0")),
            "odd_away_goals_1": self._parse_odds_value(odds.get("odd_time_gols_fora_1")),
            "odd_away_goals_2": self._parse_odds_value(odds.get("odd_time_gols_fora_2")),
            "odd_away_goals_3": self._parse_odds_value(odds.get("odd_time_gols_fora_3")),
            
            # Odds - Handicap Asiático
            "odd_handicap_home": self._parse_odds_value(odds.get("odd_handicap_asiatico_casa")),
            "odd_handicap_away": self._parse_odds_value(odds.get("odd_handicap_asiatico_fora")),
            
            # JSON completo das odds (para análises futuras)
            "odds_json": odds,
            
            # Metadados
            "status": "scheduled",
            "scraped_at": datetime.utcnow()
        }
    
    def scrape_league(self, league: str, db: Session) -> Tuple[int, int, int]:
        """
        Coleta dados de uma liga específica
        
        Args:
            league: Nome da liga (express, copa, super, euro, premier)
            db: Sessão do banco de dados
        
        Returns:
            Tupla (total_encontradas, novas, atualizadas)
        """
        logger.info(f"📊 Coletando dados da liga: {league}")
        
        # Busca próximas partidas
        data = self.client.get_next_matches(league=league)
        
        if not data or not data.get("status"):
            logger.error(f"❌ Erro ao obter dados de {league}")
            return (0, 0, 0)
        
        matches_data = data.get("matchs", [])
        total_found = len(matches_data)
        new_count = 0
        updated_count = 0
        
        logger.info(f"   Partidas encontradas: {total_found}")
        
        for match_data in matches_data:
            try:
                external_id = match_data.get("id")
                
                # Verifica se partida já existe
                existing_match = db.query(Match).filter(
                    Match.external_id == external_id
                ).first()
                
                # Extrai dados normalizados
                match_dict = self._extract_match_data(match_data, league)
                
                if existing_match:
                    # Atualiza partida existente (odds podem mudar)
                    for key, value in match_dict.items():
                        if key != "scraped_at":  # Mantém scraped_at original
                            setattr(existing_match, key, value)
                    updated_count += 1
                    logger.debug(f"   ↻ Atualizada: {match_dict['team_home']} vs {match_dict['team_away']}")
                else:
                    # Cria nova partida
                    new_match = Match(**match_dict)
                    db.add(new_match)
                    new_count += 1
                    logger.debug(f"   ✓ Nova: {match_dict['team_home']} vs {match_dict['team_away']}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar partida {match_data.get('id')}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"   ✅ Liga {league}: {new_count} novas, {updated_count} atualizadas")
        
        return (total_found, new_count, updated_count)
    
    def scrape_all_leagues(self, leagues: Optional[List[str]] = None) -> Dict:
        """
        Coleta dados de todas as ligas (ou lista especificada)
        
        Args:
            leagues: Lista de ligas para coletar (None = todas)
        
        Returns:
            Dicionário com estatísticas da coleta
        """
        if leagues is None:
            leagues = RAPIDAPI_LEAGUES
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 INICIANDO COLETA - RapidAPI")
        logger.info(f"   Ligas: {', '.join(leagues)}")
        logger.info(f"{'='*60}\n")
        
        # Cria log da execução
        log = ScraperLog(
            status="running",
            leagues_scraped=",".join(leagues),
            scraper_mode="rapidapi",
            started_at=datetime.utcnow()
        )
        
        total_found = 0
        total_new = 0
        total_updated = 0
        errors = []
        
        with get_db() as db:
            db.add(log)
            db.commit()
            db.refresh(log)
            
            # Coleta cada liga
            for league in leagues:
                try:
                    found, new, updated = self.scrape_league(league, db)
                    total_found += found
                    total_new += new
                    total_updated += updated
                    
                except Exception as e:
                    error_msg = f"Erro na liga {league}: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
            
            # Atualiza log
            log.status = "success" if not errors else ("partial" if total_found > 0 else "error")
            log.matches_found = total_found
            log.matches_new = total_new
            log.matches_updated = total_updated
            log.error_message = "; ".join(errors) if errors else None
            log.finished_at = datetime.utcnow()
            
            db.commit()
            
            # Captura dados do log antes de fechar sessão
            log_data = {
                "status": log.status,
                "leagues": leagues,
                "matches_found": log.matches_found,
                "matches_new": log.matches_new,
                "matches_updated": log.matches_updated,
                "errors": errors
            }
        
        # Resumo (fora do with, log já está detached mas temos log_data)
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ COLETA FINALIZADA")
        logger.info(f"   Partidas encontradas: {log_data['matches_found']}")
        logger.info(f"   Novas: {log_data['matches_new']}")
        logger.info(f"   Atualizadas: {log_data['matches_updated']}")
        if log_data["errors"]:
            logger.warning(f"   ⚠️ Erros: {len(log_data['errors'])}")
        logger.info(f"{'='*60}\n")
        
        return log_data


def run_rapidapi_scraper(leagues: Optional[List[str]] = None) -> Dict:
    """
    Função conveniente para executar o scraper
    
    Args:
        leagues: Lista de ligas (None = todas)
    
    Returns:
        Estatísticas da coleta
    """
    scraper = RapidAPIScraper()
    return scraper.scrape_all_leagues(leagues)
