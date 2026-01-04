"""
Script de teste para explorar a RapidAPI - Futebol Virtual Bet365
Testa todos os endpoints e mostra a estrutura dos dados retornados
"""

import json
import logging
from rapid_api_client import RapidAPIClient

# Configurar logging para ver detalhes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def save_json(data: dict, filename: str):
    """Salva dados em arquivo JSON para análise"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"💾 Dados salvos em: {filename}")


def test_endpoint(client: RapidAPIClient, endpoint_name: str, league: str = "euro"):
    """Testa um endpoint específico"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🧪 TESTANDO: {endpoint_name.upper()} - Liga: {league}")
    logger.info(f"{'='*60}\n")
    
    if endpoint_name == "last-updated":
        data = client.get_last_updated(league=league)
    elif endpoint_name == "next-matchs":
        data = client.get_next_matches(league=league)
    elif endpoint_name == "matchs":
        data = client.get_matches(league=league)
    else:
        logger.error(f"❌ Endpoint desconhecido: {endpoint_name}")
        return None
    
    if data:
        logger.info(f"✅ Sucesso! Dados recebidos:")
        logger.info(f"   Tipo: {type(data)}")
        
        if isinstance(data, dict):
            logger.info(f"   Chaves: {list(data.keys())}")
            
            # Mostra preview dos dados
            preview = json.dumps(data, indent=2, ensure_ascii=False)
            if len(preview) > 500:
                logger.info(f"   Preview (primeiros 500 chars):")
                logger.info(preview[:500] + "...")
            else:
                logger.info(f"   Dados completos:")
                logger.info(preview)
        
        elif isinstance(data, list):
            logger.info(f"   Total de itens: {len(data)}")
            if len(data) > 0:
                logger.info(f"   Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
        
        # Salva em arquivo
        filename = f"rapidapi_{endpoint_name.replace('-', '_')}_{league}.json"
        save_json(data, filename)
        
        return data
    else:
        logger.error(f"❌ Falha ao obter dados de {endpoint_name}")
        return None


def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes da RapidAPI - Futebol Virtual Bet365\n")
    
    # Chave da API (da sua página RapidAPI)
    API_KEY = "af63b68123msh7d090c49720fb63p1b3fe2jsn8898d9df2786"
    
    # Criar cliente
    client = RapidAPIClient(api_key=API_KEY)
    
    # Liga para testar (você pode mudar)
    test_league = "euro"
    
    # Testar cada endpoint
    endpoints = ["last-updated", "next-matchs", "matchs"]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            data = test_endpoint(client, endpoint, league=test_league)
            results[endpoint] = data
        except Exception as e:
            logger.error(f"❌ Erro ao testar {endpoint}: {e}", exc_info=True)
            results[endpoint] = None
    
    # Resumo final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RESUMO DOS TESTES")
    logger.info(f"{'='*60}\n")
    
    for endpoint, data in results.items():
        status = "✅ Sucesso" if data else "❌ Falha"
        logger.info(f"{endpoint:20s} - {status}")
    
    # Teste com todas as ligas (opcional - pode demorar)
    logger.info(f"\n{'='*60}")
    logger.info("🌍 TESTANDO TODAS AS LIGAS - /next-matchs")
    logger.info(f"{'='*60}\n")
    
    all_leagues_data = client.get_all_leagues_data(endpoint="next-matchs")
    
    for league, data in all_leagues_data.items():
        status = "✅" if data else "❌"
        logger.info(f"{status} Liga: {league:10s} - Dados: {'Sim' if data else 'Não'}")
    
    # Salva resultado consolidado
    save_json(all_leagues_data, "rapidapi_all_leagues_next_matchs.json")
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ Testes concluídos!")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
