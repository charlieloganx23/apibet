"""
Script de teste para verificar se conseguimos acessar a Bet365
"""
import undetected_chromedriver as uc
import time
from loguru import logger

def test_bet365_access():
    """Testa acesso básico à Bet365"""
    driver = None
    try:
        logger.info("Iniciando teste de acesso...")
        
        # Configuração mínima
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        # Testa página principal
        logger.info("Acessando www.bet365.com...")
        driver.get("https://www.bet365.com/")
        time.sleep(10)
        
        # Screenshot
        driver.save_screenshot("test_bet365_home.png")
        logger.info("Screenshot salvo: test_bet365_home.png")
        
        # Verifica título
        title = driver.title
        logger.info(f"Título da página: {title}")
        
        # Verifica URL final (pode redirecionar)
        final_url = driver.current_url
        logger.info(f"URL final: {final_url}")
        
        # Verifica conteúdo
        page_source = driver.page_source
        logger.info(f"Tamanho do HTML: {len(page_source)} chars")
        
        # Procura por indicadores de bloqueio
        if "captcha" in page_source.lower():
            logger.warning("⚠️ CAPTCHA detectado!")
        if "access denied" in page_source.lower():
            logger.warning("⚠️ Access Denied detectado!")
        if "bot" in page_source.lower():
            logger.warning("⚠️ Palavra 'bot' encontrada no HTML!")
            
        # Tenta acessar esportes virtuais
        logger.info("\nAcessando Esportes Virtuais...")
        driver.get("https://www.bet365.com/#/AVR/B146/R^1/")
        time.sleep(10)
        
        driver.save_screenshot("test_bet365_virtual.png")
        logger.info("Screenshot salvo: test_bet365_virtual.png")
        
        # Verifica container
        container_html = driver.execute_script("""
            const container = document.querySelector('.vrl-VirtualRacingContainer');
            return container ? container.innerHTML.length : -1;
        """)
        logger.info(f"Container HTML size: {container_html} chars")
        
        logger.info("\n✓ Teste concluído! Verifique os screenshots.")
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
    finally:
        if driver:
            time.sleep(2)
            driver.quit()

if __name__ == "__main__":
    test_bet365_access()
