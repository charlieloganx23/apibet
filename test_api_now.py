"""
Testar API de matches
"""
import requests

try:
    r = requests.get('http://localhost:8000/api/matches?limit=10')
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"Total de partidas retornadas: {len(data)}")
        
        if len(data) > 0:
            print("\nPrimeiras 3 partidas:")
            for m in data[:3]:
                scheduled = m.get('scheduled_time', 'N/A')
                league = m.get('league', 'N/A')
                home = m.get('home_team', m.get('team_home', 'N/A'))
                away = m.get('away_team', m.get('team_away', 'N/A'))
                print(f"  {scheduled} | {league} | {home} vs {away}")
                print(f"     Goals: {m.get('goals_home')} x {m.get('goals_away')}")
        else:
            print("❌ API retornou 0 partidas!")
    else:
        print(f"❌ Erro: {r.status_code}")
        print(r.text)
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    print("⚠️  Verifique se o servidor está rodando: python web_api.py")
