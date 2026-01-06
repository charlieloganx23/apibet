import requests
import json

API_URL = "http://localhost:8000"

print("🔍 Buscando partida: Buenos Aires vs Bogota (1:22)")
print("=" * 60)

# Buscar todas as partidas
response = requests.get(f"{API_URL}/api/matches?limit=500")
matches = response.json()

print(f"✅ Total de partidas retornadas: {len(matches)}")

# Procurar a partida específica
found = False
for match in matches:
    if "Buenos Aires" in match.get("team_home", "") and "Bogota" in match.get("team_away", ""):
        found = True
        print(f"\n🎯 PARTIDA ENCONTRADA:")
        print(f"   ID: {match['id']}")
        print(f"   Liga: {match['league']}")
        print(f"   Horário: {match['hour']}:{match['minute']}")
        print(f"   Time Casa: {match['team_home']}")
        print(f"   Time Fora: {match['team_away']}")
        print(f"   Status: {match['status']}")
        print(f"   Resultado: {match.get('result', 'Não disponível')}")
        print(f"   Gols Casa: {match.get('goals_home', 'N/A')}")
        print(f"   Gols Fora: {match.get('goals_away', 'N/A')}")
        print(f"   Total Gols: {match.get('total_goals', 'N/A')}")
        print(f"   Odds: Casa={match['odd_home']}, Empate={match['odd_draw']}, Fora={match['odd_away']}")

if not found:
    print("\n❌ Partida não encontrada!")
    print("\n📋 Mostrando partidas da liga 'super' próximas ao horário 1:22:")
    for match in matches:
        if match['league'] == 'super':
            hour = int(match['hour']) if match['hour'] else 0
            minute = int(match['minute']) if match['minute'] else 0
            if hour == 1 and 20 <= minute <= 25:
                print(f"   • {hour}:{minute:02d} - {match['team_home']} vs {match['team_away']} - Status: {match['status']}")
