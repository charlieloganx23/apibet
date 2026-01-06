"""
Servidor HTTP simples para servir o dashboard
Resolve problema de WebSocket com file:// protocol
"""
import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "web"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Adiciona headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 70)
        print(f"🌐 Dashboard servidor rodando em: http://localhost:{PORT}")
        print(f"📂 Servindo arquivos de: {DIRECTORY}/")
        print(f"🔗 Abra no navegador: http://localhost:{PORT}/dashboard.html")
        print("=" * 70)
        print("\nPressione CTRL+C para parar o servidor")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Servidor HTTP encerrado")
