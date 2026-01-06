import requests
import json

try:
    print("🔍 Testando endpoint /api/matches...")
    response = requests.get('http://localhost:8000/api/matches?limit=5')
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📊 Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Sucesso! {len(data)} partidas retornadas")
        if data:
            print(f"\n📋 Primeira partida:")
            print(json.dumps(data[0], indent=2))
    else:
        print(f"\n❌ Erro {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Erro na requisição: {e}")
    import traceback
    traceback.print_exc()
