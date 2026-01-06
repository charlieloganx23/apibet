import requests

r = requests.get('http://localhost:8000/api/matches?limit=3')
print(f"Status: {r.status_code}")
print(f"Total: {len(r.json())}")

if r.json():
    m = r.json()[0]
    print(f"\nPrimeira partida:")
    print(f"  ID: {m['id']}")
    print(f"  Liga: {m['league']}")
    print(f"  Horário: {m['scheduled_time']}")
    print(f"  Times: {m['team_home']} vs {m['team_away']}")
    print(f"  Status: {m['status']}")
    print(f"  Goals: {m['goals_home']} x {m['goals_away']}")
