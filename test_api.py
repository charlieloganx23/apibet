"""
Exemplo de uso da API via Python
"""
import requests
from datetime import datetime, timedelta
import json


API_BASE_URL = "http://localhost:8000"


def test_api():
    """Testa os endpoints da API"""
    
    print("=" * 50)
    print("TESTE DA API - BET365 VIRTUAL FOOTBALL")
    print("=" * 50)
    
    # 1. Status da API
    print("\n1. Verificando status da API...")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"✓ Status: {response.status_code}")
    print(f"  Resposta: {response.json()}")
    
    # 2. Estatísticas gerais
    print("\n2. Estatísticas gerais...")
    response = requests.get(f"{API_BASE_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Total de partidas: {stats['total_matches']}")
        print(f"  Partidas ao vivo: {stats['live_matches']}")
        print(f"  Partidas finalizadas: {stats['finished_matches']}")
        print(f"  Última atualização: {stats['last_update']}")
    
    # 3. Competições disponíveis
    print("\n3. Competições disponíveis...")
    response = requests.get(f"{API_BASE_URL}/competitions")
    if response.status_code == 200:
        competitions = response.json()
        print(f"✓ Competições: {competitions}")
    
    # 4. Partidas recentes
    print("\n4. Últimas 5 partidas...")
    response = requests.get(f"{API_BASE_URL}/matches?limit=5")
    if response.status_code == 200:
        matches = response.json()
        print(f"✓ Encontradas {len(matches)} partidas:")
        for match in matches:
            print(f"  - {match['home_team']} vs {match['away_team']}")
            print(f"    Status: {match['status']} | Data: {match['match_date']}")
    
    # 5. Partidas ao vivo
    print("\n5. Partidas ao vivo...")
    response = requests.get(f"{API_BASE_URL}/matches/live/current")
    if response.status_code == 200:
        live_matches = response.json()
        print(f"✓ {len(live_matches)} partidas ao vivo")
        for match in live_matches:
            score = f"{match['home_score_ft'] or 0}x{match['away_score_ft'] or 0}"
            print(f"  - {match['home_team']} {score} {match['away_team']}")
    
    # 6. Resultados das últimas 24 horas
    print("\n6. Resultados das últimas 24h...")
    response = requests.get(f"{API_BASE_URL}/results/recent?hours=24")
    if response.status_code == 200:
        results = response.json()
        print(f"✓ {len(results)} resultados encontrados")
    
    # 7. Status do scraper
    print("\n7. Status do scraper...")
    response = requests.get(f"{API_BASE_URL}/scraper/status")
    if response.status_code == 200:
        status = response.json()
        print(f"✓ Status: {status}")
    
    # 8. Logs do scraper
    print("\n8. Últimos logs do scraper...")
    response = requests.get(f"{API_BASE_URL}/scraper/logs?limit=3")
    if response.status_code == 200:
        logs = response.json()
        print(f"✓ {len(logs)} logs encontrados")
        for log in logs:
            print(f"  - {log['started_at']}: {log['status']}")
            print(f"    Encontradas: {log['matches_found']}, Novas: {log['matches_new']}")
    
    # 9. Filtrar por competição
    print("\n9. Filtrar por competição (exemplo)...")
    response = requests.get(
        f"{API_BASE_URL}/matches",
        params={"competition": "CAMPEONATO MUNDIAL", "limit": 3}
    )
    if response.status_code == 200:
        matches = response.json()
        print(f"✓ {len(matches)} partidas do Mundial encontradas")
    
    # 10. Disparar scraper (se necessário)
    print("\n10. Disparar scraper manualmente...")
    print("   (Comentado - descomente se quiser testar)")
    # response = requests.post(f"{API_BASE_URL}/scraper/run")
    # print(f"  {response.json()}")
    
    print("\n" + "=" * 50)
    print("TESTES CONCLUÍDOS!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: API não está rodando!")
        print("Inicie a API com: python main.py api")
    except Exception as e:
        print(f"❌ Erro: {e}")
