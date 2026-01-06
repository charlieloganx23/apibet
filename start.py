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
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ Erro ao verificar porta {port}: {e}{Colors.RESET}")
        return True

def kill_process_on_port(port):
    """Encerra processos usando uma porta específica"""
    if os.name == 'nt':
        try:
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                pids = set()
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit() and pid != '0':
                            pids.add(pid)
                
                for pid in pids:
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                    print(f"{Colors.YELLOW}  • Processo {pid} encerrado{Colors.RESET}")
                
                time.sleep(2)
                return True
        except Exception as e:
            print(f"{Colors.YELLOW}  • Erro ao encerrar processo: {e}{Colors.RESET}")
    return False

def start_api():
    """Inicia o servidor FastAPI"""
    print(f"{Colors.YELLOW}⏳ Iniciando API FastAPI...{Colors.RESET}")
    
    if not check_port(8000):
        print(f"{Colors.RED}❌ Porta 8000 já está em uso!{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Encerrando processo anterior...{Colors.RESET}")
        kill_process_on_port(8000)
    
    # Inicia API em background (sem capturar output para não bloquear)
    if os.name == 'nt':
        # Windows
        api_process = subprocess.Popen(
            ['python', '-m', 'uvicorn', 'web_api:app', '--reload', '--port', '8000'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Linux/Mac
        api_process = subprocess.Popen(
            ['python', '-m', 'uvicorn', 'web_api:app', '--reload', '--port', '8000']
        )
    
    # Aguarda a API iniciar (dá tempo para os imports do Python)
    print(f"{Colors.YELLOW}  Aguardando API iniciar{Colors.RESET}", end='', flush=True)
    time.sleep(2)  # Delay inicial para imports
    for i in range(15):
        time.sleep(1)
        if not check_port(8000):
            print(f"\n{Colors.GREEN}✅ API iniciada: http://localhost:8000{Colors.RESET}")
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
        kill_process_on_port(3000)
    
    # Inicia Dashboard em background (sem capturar output para não bloquear)
    if os.name == 'nt':
        dashboard_process = subprocess.Popen(
            ['python', 'serve_dashboard.py'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        dashboard_process = subprocess.Popen(
            ['python', 'serve_dashboard.py']
        )
    
    # Aguarda o Dashboard iniciar (dá tempo para os imports do Python)
    print(f"{Colors.YELLOW}  Aguardando Dashboard iniciar{Colors.RESET}", end='', flush=True)
    time.sleep(2)  # Delay inicial para imports
    for i in range(15):
        time.sleep(1)
        if not check_port(3000):
            print(f"\n{Colors.GREEN}✅ Dashboard iniciado: http://localhost:3000/dashboard.html{Colors.RESET}")
            return dashboard_process
        print(f"{Colors.YELLOW}.{Colors.RESET}", end='', flush=True)
    
    print(f"\n{Colors.RED}❌ Erro ao iniciar Dashboard{Colors.RESET}")
    print(f"{Colors.YELLOW}💡 Verifique se o serve_dashboard.py está funcionando: python serve_dashboard.py{Colors.RESET}")
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
