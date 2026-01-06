"""
Teste da API - Verificar o que está sendo retornado
"""
import requests
import json

API_URL = "http://localhost:8000"

print("="*80)
print("🔍 TESTANDO ENDPOINT DA API")
print("="*80)

# Teste 1: Buscar todas as partidas
print("\n1️⃣ Buscando todas as partidas (limit=1000)...")
response = requests.get(f"{API_URL}/api/matches?limit=1000")
if response.status_code == 200:
    matches = response.json()
    print(f"✅ Total retornado: {len(matches)}")
    
    # Contar finalizadas vs agendadas
    finished = sum(1 for m in matches if m.get('goals_home') is not None and m.get('goals_away') is not None)
    scheduled = len(matches) - finished
    
    print(f"   Finalizadas: {finished}")
    print(f"   Agendadas: {scheduled}")
    
    # Mostrar exemplos
    print("\n📋 Primeiras 5 partidas:")
    for m in matches[:5]:
        status_icon = "✅" if m.get('goals_home') is not None else "📅"
        print(f"   {status_icon} ID {m.get('id'):4d} | {m.get('team_home'):20s} vs {m.get('team_away'):20s} | goals: {m.get('goals_home')}, {m.get('goals_away')}")
else:
    print(f"❌ Erro: {response.status_code}")

print("\n" + "="*80)
