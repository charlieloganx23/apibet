"""
Coletor de resultados históricos via RapidAPI
Atualiza partidas no banco com placares finais para treinar ML
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from rapid_api_client import RapidAPIClient
from models_rapidapi import Match, ScraperLog
from database_rapidapi import get_db
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, RAPIDAPI_LEAGUES

logger = logging.getLogger(__name__)


class ResultsCollector:
    """Coleta resultados históricos de partidas finalizadas"""
    
    def __init__(self):
        self.client = RapidAPIClient(
            api_key=RAPIDAPI_KEY,
            api_host=RAPIDAPI_HOST
        )
    
    def _parse_score(self, score_str: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse placar no formato "0-1" para (goals_home, goals_away)
        
        Args:
            score_str: String do placar (ex: "2-1", "0-0")
        
        Returns:
            Tupla (goals_home, goals_away) ou (None, None) se inválido
        """
        if not score_str:
            return (None, None)
        
        match = re.match(r'^(\d+)-(\d+)$', score_str.strip())
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        return (None, None)
    
    def _determine_result(self, goals_home: int, goals_away: int) -> str:
        """
        Determina resultado da partida
        
        Args:
            goals_home: Gols do time da casa
            goals_away: Gols do time visitante
        
        Returns:
            'home', 'away' ou 'draw'
        """
        if goals_home > goals_away:
            return 'home'
        elif goals_away > goals_home:
            return 'away'
        else:
            return 'draw'
    
    def _update_match_with_result(
        self, 
        match: Match, 
        result_data: Dict,
        db: Session
    ) -> bool:
        """
        Atualiza partida existente com resultado
        
        Args:
            match: Objeto Match do banco
            result_data: Dados do resultado da API
            db: Sessão do banco
        
        Returns:
            True se atualizado com sucesso
        """
        try:
            # Parse placar final
            score_ft = result_data.get("resultadoFt") or result_data.get("resultado")
            goals_home, goals_away = self._parse_score(score_ft)
            
            if goals_home is None or goals_away is None:
                logger.warning(f"❌ Placar inválido para partida {match.external_id}: {score_ft}")
                return False
            
            # Parse placar 1º tempo
            score_ht = result_data.get("resultadoHt", "")
            goals_home_ht, goals_away_ht = self._parse_score(score_ht)
            
            # Atualiza match
            match.goals_home = goals_home
            match.goals_away = goals_away
            match.total_goals = goals_home + goals_away
            match.result = self._determine_result(goals_home, goals_away)
            match.status = "finished"
            
            # Metadados adicionais (se disponíveis)
            if "primeiroMarcar" in result_data:
                # Poderia adicionar campo no modelo se necessário
                pass
            
            logger.debug(f"   ✓ Atualizada: {match.team_home} {goals_home}-{goals_away} {match.team_away}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar partida {match.external_id}: {e}")
            return False
    
    def collect_league_results(
        self, 
        league: str, 
        db: Session,
        activate_odds: bool = False
    ) -> Tuple[int, int]:
        """
        Coleta resultados de uma liga específica
        
        Args:
            league: Nome da liga
            db: Sessão do banco
            activate_odds: Se True, inclui odds (mais lento)
        
        Returns:
            Tupla (total_encontrados, atualizados)
        """
        logger.info(f"📊 Coletando resultados da liga: {league}")
        
        # Busca partidas finalizadas
        data = self.client.get_matches(league=league)
        
        if not data or not data.get("status"):
            logger.error(f"❌ Erro ao obter resultados de {league}")
            return (0, 0)
        
        results_data = data.get("matchs", [])
        total_found = len(results_data)
        updated_count = 0
        
        logger.info(f"   Resultados encontrados: {total_found}")
        
        for result_data in results_data:
            try:
                external_id = result_data.get("id")
                
                # Busca partida no banco
                match = db.query(Match).filter(
                    Match.external_id == external_id
                ).first()
                
                if match:
                    # Atualiza com resultado
                    if self._update_match_with_result(match, result_data, db):
                        updated_count += 1
                else:
                    # Partida não estava no banco (pode criar se quiser)
                    logger.debug(f"   ⚠️ Partida {external_id} não encontrada no banco")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar resultado {result_data.get('id')}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"   ✅ Liga {league}: {updated_count}/{total_found} partidas atualizadas")
        
        return (total_found, updated_count)
    
    def collect_all_results(self, leagues: Optional[List[str]] = None) -> Dict:
        """
        Coleta resultados de todas as ligas
        
        Args:
            leagues: Lista de ligas (None = todas)
        
        Returns:
            Estatísticas da coleta
        """
        if leagues is None:
            leagues = RAPIDAPI_LEAGUES
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🏆 COLETANDO RESULTADOS HISTÓRICOS")
        logger.info(f"   Ligas: {', '.join(leagues)}")
        logger.info(f"{'='*60}\n")
        
        total_found = 0
        total_updated = 0
        errors = []
        
        with get_db() as db:
            for league in leagues:
                try:
                    found, updated = self.collect_league_results(league, db)
                    total_found += found
                    total_updated += updated
                    
                except Exception as e:
                    error_msg = f"Erro na liga {league}: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
        
        # Resumo
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ COLETA DE RESULTADOS FINALIZADA")
        logger.info(f"   Resultados encontrados: {total_found}")
        logger.info(f"   Partidas atualizadas: {total_updated}")
        if errors:
            logger.warning(f"   ⚠️ Erros: {len(errors)}")
        logger.info(f"{'='*60}\n")
        
        return {
            "results_found": total_found,
            "matches_updated": total_updated,
            "errors": errors
        }


def run_results_collector(leagues: Optional[List[str]] = None) -> Dict:
    """
    Função conveniente para executar o coletor de resultados
    
    Args:
        leagues: Lista de ligas (None = todas)
    
    Returns:
        Estatísticas da coleta
    """
    collector = ResultsCollector()
    return collector.collect_all_results(leagues)
