import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    print(f"🔌 Conectando ao WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado com sucesso!")
            
            # Receber mensagem de conexão
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Mensagem recebida: {data}")
            
            # Enviar ping
            print("🏓 Enviando ping...")
            await websocket.send("ping")
            
            # Receber pong
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Resposta: {data}")
            
            print("✅ WebSocket funcionando corretamente!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
