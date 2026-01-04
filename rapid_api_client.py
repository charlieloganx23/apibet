"""
Cliente para interação com a RapidAPI - Futebol Virtual Bet365
Endpoints disponíveis:
- /last-updated: Última atualização
- /next-matchs: Próximas partidas
- /matchs: Partidas em geral
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RapidAPIClient:
    """Cliente para API do Futebol Virtual Bet365 na RapidAPI"""
    
    BASE_URL = "https://futebol-virtual-bet3651.p.rapidapi.com"
    
    # Ligas disponíveis segundo a documentação
    AVAILABLE_LEAGUES = ["express", "copa", "super", "euro", "premier"]
    
    def __init__(self, api_key: str, api_host: str = "futebol-virtual-bet3651.p.rapidapi.com"):
        """
        Inicializa o cliente da RapidAPI
        
        Args:
            api_key: Chave de API da RapidAPI (X-RapidAPI-Key)
            api_host: Host da API (X-RapidAPI-Host)
        """
        self.api_key = api_key
        self.api_host = api_host
        
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api_host,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def _make_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Optional[Dict]:
        """
        Faz requisição à API
        
        Args:
            endpoint: Endpoint da API (ex: '/last-updated')
            data: Dados do body (form-data)
            method: Método HTTP (POST)
        
        Returns:
            Resposta JSON ou None em caso de erro
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.info(f"🌐 Requisição: {method} {endpoint}")
            logger.debug(f"   Payload: {data}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                data=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✓ Status: {response.status_code}")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Erro HTTP: {e}")
            if response is not None:
                try:
                    logger.error(f"   Response: {response.text}")
                except:
                    logger.error(f"   Response: (não disponível)")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout na requisição para {endpoint}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição: {e}")
            return None
            
        except ValueError as e:
            logger.error(f"❌ Erro ao parsear JSON: {e}")
            logger.error(f"   Response text: {response.text if response else 'N/A'}")
            return None
    
    def get_last_updated(
        self, 
        league: str = "euro", 
        home: str = "bet365", 
        sport_id: int = 1
    ) -> Optional[Dict]:
        """
        Obtém última atualização da liga
        
        Args:
            league: Nome da liga ("express", "copa", "super", "euro", "premier")
            home: Casa de apostas (padrão: "bet365")
            sport_id: ID do esporte (1 = Futebol Virtual)
        
        Returns:
            Dados da última atualização ou None
        """
        if league not in self.AVAILABLE_LEAGUES:
            logger.warning(f"⚠️ Liga '{league}' pode não ser válida. Disponíveis: {self.AVAILABLE_LEAGUES}")
        
        data = {
            "league": league,
            "home": home,
            "sport_id": sport_id
        }
        
        return self._make_request("/last-updated", data)
    
    def get_next_matches(
        self, 
        league: str = "euro", 
        home: str = "bet365", 
        sport_id: int = 1
    ) -> Optional[Dict]:
        """
        Obtém próximas partidas da liga
        
        Args:
            league: Nome da liga ("express", "copa", "super", "euro", "premier")
            home: Casa de apostas (padrão: "bet365")
            sport_id: ID do esporte (1 = Futebol Virtual)
        
        Returns:
            Lista de próximas partidas ou None
        """
        if league not in self.AVAILABLE_LEAGUES:
            logger.warning(f"⚠️ Liga '{league}' pode não ser válida. Disponíveis: {self.AVAILABLE_LEAGUES}")
        
        data = {
            "league": league,
            "home": home,
            "sport_id": sport_id
        }
        
        return self._make_request("/next-matchs", data)
    
    def get_matches(
        self, 
        league: str = "euro", 
        home: str = "bet365", 
        sport_id: int = 1
    ) -> Optional[Dict]:
        """
        Obtém partidas da liga
        
        Args:
            league: Nome da liga ("express", "copa", "super", "euro", "premier")
            home: Casa de apostas (padrão: "bet365")
            sport_id: ID do esporte (1 = Futebol Virtual)
        
        Returns:
            Lista de partidas ou None
        """
        if league not in self.AVAILABLE_LEAGUES:
            logger.warning(f"⚠️ Liga '{league}' pode não ser válida. Disponíveis: {self.AVAILABLE_LEAGUES}")
        
        data = {
            "league": league,
            "home": home,
            "sport_id": sport_id
        }
        
        return self._make_request("/matchs", data)
    
    def get_all_leagues_data(
        self, 
        endpoint: str = "next-matchs",
        home: str = "bet365",
        sport_id: int = 1
    ) -> Dict[str, Optional[Dict]]:
        """
        Obtém dados de todas as ligas disponíveis
        
        Args:
            endpoint: Endpoint a chamar ('last-updated', 'next-matchs', 'matchs')
            home: Casa de apostas
            sport_id: ID do esporte
        
        Returns:
            Dicionário com {liga: dados} para cada liga
        """
        logger.info(f"📊 Coletando dados de todas as ligas no endpoint /{endpoint}")
        
        results = {}
        
        for league in self.AVAILABLE_LEAGUES:
            logger.info(f"   → Liga: {league}")
            
            if endpoint == "last-updated":
                data = self.get_last_updated(league, home, sport_id)
            elif endpoint == "next-matchs":
                data = self.get_next_matches(league, home, sport_id)
            elif endpoint == "matchs":
                data = self.get_matches(league, home, sport_id)
            else:
                logger.error(f"❌ Endpoint inválido: {endpoint}")
                data = None
            
            results[league] = data
        
        return results
