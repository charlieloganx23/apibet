"""
🚀 ApiBet - Sistema de Inicialização Unificado
Inicia API, Dashboard e abre o navegador automaticamente
"""
import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Exibe cabeçalho do sistema"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎯 ApiBet - Sistema de Predições de Futebol Virtual{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def check_port(port):
    """Verifica se a porta está disponível"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def start_api():
    """Inicia o servidor FastAPI"""
    print(f"{Colors.YELLOW}⏳ Iniciando API FastAPI...{Colors.RESET}")
    
    if not check_port(8000):
        print(f"{Colors.RED}❌ Porta 8000 já está em uso!{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Encerrando processo anterior...{Colors.RESET}")
        # Tenta encerrar processo na porta 8000
        if os.name == 'nt':
            os.system('netstat -ano | findstr :8000 > nul && for /f "tokens=5" %a in (\'netstat -ano ^| findstr :8000\') do taskkill /F /PID %a > nul 2>&1')
        time.sleep(2)
    
    # Inicia API em background
    if os.name == 'nt':
        # Windows
        api_process = subprocess.Popen(
            ['python', '-m', 'uvicorn', 'web_api:app', '--reload', '--port', '8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Linux/Mac
        api_process = subprocess.Popen(
            ['python', '-m', 'uvicorn', 'web_api:app', '--reload', '--port', '8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Aguarda a API iniciar
    for i in range(10):
        time.sleep(1)
        if not check_port(8000):
            print(f"{Colors.GREEN}✅ API iniciada: http://localhost:8000{Colors.RESET}")
            return api_process
        print(f"{Colors.YELLOW}.{Colors.RESET}", end='', flush=True)
    
    print(f"\n{Colors.RED}❌ Erro ao iniciar API{Colors.RESET}")
    return None

def start_dashboard():
    """Inicia o servidor HTTP do dashboard"""
    print(f"\n{Colors.YELLOW}⏳ Iniciando Dashboard...{Colors.RESET}")
    
    if not check_port(3000):
        print(f"{Colors.RED}❌ Porta 3000 já está em uso!{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Encerrando processo anterior...{Colors.RESET}")
        if os.name == 'nt':
            os.system('netstat -ano | findstr :3000 > nul && for /f "tokens=5" %a in (\'netstat -ano ^| findstr :3000\') do taskkill /F /PID %a > nul 2>&1')
        time.sleep(2)
    
    # Inicia Dashboard em background
    if os.name == 'nt':
        dashboard_process = subprocess.Popen(
            ['python', 'serve_dashboard.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        dashboard_process = subprocess.Popen(
            ['python', 'serve_dashboard.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Aguarda o Dashboard iniciar
    for i in range(10):
        time.sleep(1)
        if not check_port(3000):
            print(f"{Colors.GREEN}✅ Dashboard iniciado: http://localhost:3000{Colors.RESET}")
            return dashboard_process
        print(f"{Colors.YELLOW}.{Colors.RESET}", end='', flush=True)
    
    print(f"\n{Colors.RED}❌ Erro ao iniciar Dashboard{Colors.RESET}")
    return None

def open_browser():
    """Abre o navegador automaticamente"""
    print(f"\n{Colors.YELLOW}🌐 Abrindo navegador...{Colors.RESET}")
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:3000/dashboard.html')
        print(f"{Colors.GREEN}✅ Navegador aberto{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao abrir navegador: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Abra manualmente: http://localhost:3000/dashboard.html{Colors.RESET}")

def show_status():
    """Exibe status do sistema"""
    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ Sistema ApiBet Online!{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"""
{Colors.BOLD}🔗 URLs:{Colors.RESET}
   • Dashboard: {Colors.BLUE}http://localhost:3000/dashboard.html{Colors.RESET}
   • API Docs:  {Colors.BLUE}http://localhost:8000/docs{Colors.RESET}
   • WebSocket: {Colors.BLUE}ws://localhost:8000/ws{Colors.RESET}

{Colors.BOLD}📊 Funcionalidades:{Colors.RESET}
   • Predições de partidas com ML
   • WebSocket tempo real
   • Analytics e gráficos
   • Recomendações de apostas
   • Export CSV
   • Logs de scraper

{Colors.BOLD}🎮 Comandos disponíveis:{Colors.RESET}
   • python main_rapidapi.py once    - Executar scraper
   • python main_rapidapi.py stats   - Ver estatísticas
   • python predict_match.py 21:00   - Fazer predição

{Colors.BOLD}⚠️ Para encerrar:{Colors.RESET}
   • Pressione {Colors.RED}CTRL+C{Colors.RESET} nesta janela
   • Ou feche as janelas dos servidores
    """)
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def main():
    """Função principal"""
    try:
        print_header()
        
        # Verifica se está na pasta correta
        if not Path('web_api.py').exists():
            print(f"{Colors.RED}❌ Erro: Execute este script na pasta do projeto!{Colors.RESET}")
            sys.exit(1)
        
        # Inicia os servidores
        api_process = start_api()
        if not api_process:
            print(f"{Colors.RED}❌ Falha ao iniciar API. Verifique os logs.{Colors.RESET}")
            sys.exit(1)
        
        dashboard_process = start_dashboard()
        if not dashboard_process:
            print(f"{Colors.RED}❌ Falha ao iniciar Dashboard. Verifique os logs.{Colors.RESET}")
            api_process.terminate()
            sys.exit(1)
        
        # Abre navegador
        open_browser()
        
        # Exibe status
        show_status()
        
        # Mantém o script rodando
        print(f"{Colors.YELLOW}🔄 Sistema rodando... Pressione CTRL+C para encerrar{Colors.RESET}\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}🛑 Encerrando sistema...{Colors.RESET}")
            
            # Encerra processos
            if api_process:
                api_process.terminate()
                print(f"{Colors.GREEN}✅ API encerrada{Colors.RESET}")
            
            if dashboard_process:
                dashboard_process.terminate()
                print(f"{Colors.GREEN}✅ Dashboard encerrado{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}✅ Sistema encerrado com sucesso!{Colors.RESET}\n")
            sys.exit(0)
    
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro fatal: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
