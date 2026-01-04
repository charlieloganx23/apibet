"""
Script auxiliar para inspecionar a estrutura do site Bet365
e ajudar a identificar seletores corretos
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

def inspect_bet365():
    """Inspeciona a estrutura da página"""
    
    print("=" * 60)
    print("INSPETOR DE ESTRUTURA - BET365 VIRTUAL FOOTBALL")
    print("=" * 60)
    
    # Configura Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Habilita logs de performance para capturar network requests
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://www.bet365.com/#/AVR/B146/R^1/"
        print(f"\n1. Acessando URL: {url}")
        driver.get(url)
        
        print("   Aguardando carregamento (15 segundos)...")
        time.sleep(15)
        
        # Salva HTML
        print("\n2. Salvando HTML completo...")
        html = driver.page_source
        with open('bet365_structure.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   ✓ Salvo em: bet365_structure.html")
        
        # Analisa estrutura
        print("\n3. Analisando estrutura HTML...")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Procura por padrões comuns
        print("\n   Procurando por elementos relevantes:")
        
        patterns = [
            "div[class*='match']",
            "div[class*='event']",
            "div[class*='fixture']",
            "div[class*='virtual']",
            "div[class*='sport']",
            "div[class*='game']",
            "[data-match-id]",
            "[data-event-id]",
            ".score",
            ".team"
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if elements:
                print(f"   ✓ Encontrados {len(elements)} elementos: {pattern}")
                if len(elements) > 0:
                    print(f"      Exemplo: {str(elements[0])[:150]}...")
        
        # Captura Network Requests
        print("\n4. Analisando requisições de rede...")
        logs = driver.get_log('performance')
        
        urls_relevantes = []
        for log in logs:
            try:
                message = json.loads(log['message'])['message']
                if message['method'] == 'Network.responseReceived':
                    url = message['params']['response']['url']
                    if any(k in url.lower() for k in ['virtual', 'sport', 'event', 'match', 'api', 'data']):
                        urls_relevantes.append(url)
            except:
                pass
        
        # Remove duplicadas
        urls_relevantes = list(set(urls_relevantes))
        
        if urls_relevantes:
            print(f"\n   ✓ {len(urls_relevantes)} URLs relevantes encontradas:")
            with open('bet365_network_urls.txt', 'w', encoding='utf-8') as f:
                for url in urls_relevantes[:20]:  # Mostra primeiras 20
                    print(f"      - {url[:100]}...")
                    f.write(url + '\n')
            print("   ✓ Lista completa salva em: bet365_network_urls.txt")
        else:
            print("   ⚠ Nenhuma URL relevante encontrada")
        
        # Captura screenshot
        print("\n5. Capturando screenshot...")
        driver.save_screenshot('bet365_screenshot.png')
        print("   ✓ Salvo em: bet365_screenshot.png")
        
        print("\n" + "=" * 60)
        print("INSPEÇÃO CONCLUÍDA!")
        print("=" * 60)
        print("\nArquivos gerados:")
        print("  1. bet365_structure.html - HTML completo da página")
        print("  2. bet365_network_urls.txt - URLs de requisições")
        print("  3. bet365_screenshot.png - Captura de tela")
        print("\nPróximos passos:")
        print("  1. Abra bet365_structure.html e procure por partidas")
        print("  2. Identifique classes CSS e estrutura")
        print("  3. Atualize os seletores no scraper.py")
        print("  4. Verifique as URLs em bet365_network_urls.txt")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        input("\nPressione ENTER para fechar o navegador...")
        driver.quit()


if __name__ == "__main__":
    inspect_bet365()
