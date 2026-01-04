"""
Scraper para Bet365 Futebol Virtual
⚠️ AVISO: Este código é apenas para fins educacionais.
Web scraping pode violar os Termos de Serviço do site.
"""
from datetime import datetime
from typing import List, Dict, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import json
import re
from loguru import logger

from config import (
    BET365_URL,
    BET365_RESULTS_URL,
    SCRAPER_HEADLESS,
    SCRAPER_MANUAL_MODE,
    SCRAPER_MANUAL_TIMEOUT,
    SCRAPER_USER_AGENT,
    COMPETITIONS
)
from models import VirtualMatch, ScraperLog
from database import get_db


class Bet365VirtualScraper:
    """Scraper para capturar dados de Futebol Virtual da Bet365"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura o driver com undetected-chromedriver (bypass anti-bot)"""
        try:
            # ⭐ UNDETECTED CHROMEDRIVER - Bypass automático de detecção
            options = uc.ChromeOptions()
            
            # ⭐ MODO MANUAL: Força navegador visível
            should_use_headless = SCRAPER_HEADLESS and not SCRAPER_MANUAL_MODE
            
            if should_use_headless:
                options.add_argument("--headless=new")
                logger.info("Modo headless ativado")
            else:
                logger.info("🖥️  Navegador será aberto visível (modo manual)")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            # User-Agent
            options.add_argument(f"--user-agent={SCRAPER_USER_AGENT}")
            
            # Preferências
            prefs = {
                "profile.managed_default_content_settings.images": 2,  # Desabilita imagens
                "profile.default_content_setting_values.notifications": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            # Cria driver com undetected-chromedriver (auto-bypass)
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                use_subprocess=True  # Melhor performance
            )
            
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("✓ Driver undetected-chromedriver configurado")
            
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {e}")
            raise
    
    def wait_for_manual_action(self, target_selector=".vrl-VirtualRacingContainer", min_content_size=100):
        """Aguarda usuário resolver CAPTCHA/login manualmente"""
        logger.info("")
        logger.info("═" * 70)
        logger.info("🔧 MODO MANUAL ATIVADO")
        logger.info("═" * 70)
        logger.info("")
        logger.info("➤ POR FAVOR, faça o seguinte no navegador que acabou de abrir:")
        logger.info("  1. Resolva o CAPTCHA (se aparecer)")
        logger.info("  2. Faça login na Bet365 (se necessário)")
        logger.info("  3. Aguarde a página de Esportes Virtuais carregar completamente")
        logger.info("")
        logger.info(f"⏱️  Você tem {SCRAPER_MANUAL_TIMEOUT} segundos...")
        logger.info("")
        logger.info("💡 O scraper detectará automaticamente quando estiver pronto!")
        logger.info("")
        
        start_time = time.time()
        check_interval = 2  # Verifica a cada 2 segundos
        
        while time.time() - start_time < SCRAPER_MANUAL_TIMEOUT:
            try:
                # Verifica se navegador ainda está aberto
                try:
                    _ = self.driver.current_url
                except:
                    logger.error("")
                    logger.error("❌ ERRO: Navegador foi fechado!")
                    logger.error("   Por favor, não feche o navegador manualmente.")
                    logger.error("   O script continuará automaticamente após você resolver o CAPTCHA.")
                    logger.error("")
                    return False
                
                # Verifica se o container tem conteúdo
                container_size = self.driver.execute_script(f"""
                    const container = document.querySelector('{target_selector}');
                    return container ? container.innerHTML.length : 0;
                """)
                
                elapsed = int(time.time() - start_time)
                remaining = SCRAPER_MANUAL_TIMEOUT - elapsed
                
                if container_size >= min_content_size:
                    logger.info("")
                    logger.info("✅ DETECÇÃO AUTOMÁTICA: Conteúdo carregado!")
                    logger.info(f"   Container: {container_size} chars")
                    logger.info("")
                    logger.info("🚀 Prosseguindo com automação...")
                    logger.info("═" * 70)
                    logger.info("")
                    return True
                    
                if elapsed % 15 == 0 and elapsed > 0:  # Log a cada 15s
                    logger.info(f"⏳ Aguardando... ({remaining}s restantes | Container: {container_size} chars)")
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.debug(f"Erro ao verificar container: {e}")
                time.sleep(check_interval)
        
        logger.warning("")
        logger.warning("⚠️ Timeout atingido! Continuando mesmo assim...")
        logger.warning("")
        return False
    
    def close_driver(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver fechado")
    
    def scrape_live_matches(self) -> List[Dict]:
        """
        Scrape partidas ao vivo com múltiplas estratégias
        """
        matches = []
        
        try:
            logger.info(f"Acessando URL: {BET365_URL}")
            
            # ⭐ IMPORTANTE: Acessa página principal primeiro (evita detecção)
            logger.info("Acessando página principal...")
            self.driver.get("https://www.bet365.com/")
            time.sleep(8)  # Aguarda página principal carregar completamente
            
            # Verifica título
            try:
                page_title = self.driver.title
                logger.info(f"✓ Bet365 carregada: {page_title}")
            except:
                pass
            
            # Agora navega para esportes virtuais
            logger.info("Navegando para Esportes Virtuais...")
            self.driver.get(BET365_URL)
            time.sleep(5)  # Aguarda redirecionamento
            
            # ⭐ MODO MANUAL: Aguarda usuário resolver CAPTCHA/login
            if SCRAPER_MANUAL_MODE:
                manual_success = self.wait_for_manual_action(
                    target_selector=".vrl-VirtualRacingContainer",
                    min_content_size=1000  # Considera carregado se tiver >1000 chars
                )
                
                if not manual_success:
                    logger.warning("Modo manual não completou com sucesso, mas continuando...")
            
            # ⭐ AGUARDA JAVASCRIPT RENDERIZAR CONTEÚDO DINÂMICO
            logger.info("Aguardando carregamento dinâmico do conteúdo...")
            try:
                # Espera até 20s pelo container principal carregar elementos filhos
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.vrl-VirtualRacingContainer > *"))
                )
                logger.info("✓ Conteúdo dinâmico carregado!")
            except TimeoutException:
                logger.warning("⚠️ Timeout esperando conteúdo dinâmico - continuando mesmo assim...")
            
            # ⭐ TENTA EXECUTAR JAVASCRIPT PARA FORÇAR RENDERING
            try:
                container_html = self.driver.execute_script("""
                    const container = document.querySelector('.vrl-VirtualRacingContainer');
                    return container ? container.innerHTML.length : 0;
                """)
                logger.info(f"Container HTML size: {container_html} chars")
            except Exception as e:
                logger.debug(f"Erro ao verificar container: {e}")
            
            # Aguarda adicional para garantir estabilidade
            time.sleep(8)
            
            # Estratégia 1: Tentar capturar via Network requests (mais confiável)
            logger.info("Tentando capturar dados via requisições de rede...")
            network_matches = self._capture_network_data()
            if network_matches:
                matches.extend(network_matches)
                logger.info(f"Capturados {len(network_matches)} via network")
            
            # Estratégia 2: Parse HTML
            if not matches:
                logger.info("Tentando parsear HTML...")
                page_source = self.driver.page_source
                
                # Salva HTML para debug
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.info("HTML salvo em debug_page.html para análise")
                
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Seletores baseados na análise do HTML capturado da Bet365
                selectors = [
                    {'name': 'div.vr-VirtualRacingModule'},  # Módulo principal de esportes virtuais
                    {'name': 'div.vrl-VirtualRacingContainer'},  # Container de corridas virtuais
                    {'name': 'div[class*="rcl"]'},  # React Component Library da Bet365
                    {'name': 'div[class*="ovm"]'},  # Odd View Module
                    {'name': 'div[class*="src"]'},  # Score/Result Component  
                    {'name': 'div[class*="event"]'},
                    {'name': 'div[class*="match"]'},
                    {'name': 'div[class*="fixture"]'}
                ]
                
                for selector in selectors:
                    elements = soup.select(selector['name'])
                    if elements:
                        logger.info(f"Encontrados {len(elements)} elementos com seletor: {selector['name']}")
                        for element in elements:
                            try:
                                match_data = self._parse_match_element(element)
                                if match_data:
                                    matches.append(match_data)
                            except Exception as e:
                                logger.debug(f"Erro ao parsear elemento: {e}")
                        if matches:
                            break
            
            logger.info(f"✓ Total de {len(matches)} partidas encontradas ao vivo")
            
        except Exception as e:
            logger.error(f"Erro ao fazer scrape de partidas ao vivo: {e}")
        
        return matches
    
    def scrape_results_history(self, days: int = 7) -> List[Dict]:
        """
        Scrape histórico de resultados
        ⚠️ Este método precisa ser adaptado à estrutura real do site
        """
        matches = []
        
        try:
            logger.info(f"Acessando histórico: {BET365_RESULTS_URL}")
            self.driver.get(BET365_RESULTS_URL)
            
            time.sleep(3)
            
            # Analisar estrutura da página de resultados
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # ⚠️ AJUSTAR SELETORES
            result_elements = soup.find_all('div', class_='result-row')  # EXEMPLO
            
            for element in result_elements:
                try:
                    match_data = self._parse_result_element(element)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.warning(f"Erro ao parsear resultado: {e}")
                    continue
            
            logger.info(f"Total de {len(matches)} resultados históricos encontrados")
            
        except Exception as e:
            logger.error(f"Erro ao fazer scrape de histórico: {e}")
        
        return matches
    
    def _parse_match_element(self, element) -> Optional[Dict]:
        """
        Parseia elemento HTML de uma partida
        ⚠️ ADAPTAR à estrutura real do site
        """
        try:
            # EXEMPLO - estrutura fictícia
            match_data = {
                'match_id': f"vf_{datetime.now().timestamp()}",
                'competition': "CAMPEONATO MUNDIAL",  # Extrair do HTML
                'home_team': element.find('span', class_='home-team').text.strip(),
                'away_team': element.find('span', class_='away-team').text.strip(),
                'home_score_ht': None,
                'away_score_ht': None,
                'home_score_ft': None,
                'away_score_ft': None,
                'status': 'live',
                'match_time': element.find('span', class_='time').text.strip(),
                'match_date': datetime.now(),
                'source_url': self.driver.current_url,
                'additional_data': {}
            }
            
            return match_data
            
        except Exception as e:
            logger.debug(f"Erro ao parsear elemento: {e}")
            return None
    
    def _parse_result_element(self, element) -> Optional[Dict]:
        """
        Parseia elemento HTML de um resultado
        ⚠️ ADAPTAR à estrutura real do site
        """
        try:
            # EXEMPLO - estrutura fictícia
            match_data = {
                'match_id': element.get('data-match-id', f"vf_{datetime.now().timestamp()}"),
                'competition': "PREMIERSHIP",  # Extrair do HTML
                'home_team': element.find('span', class_='home-team').text.strip(),
                'away_team': element.find('span', class_='away-team').text.strip(),
                'home_score_ht': int(element.find('span', class_='ht-home').text),
                'away_score_ht': int(element.find('span', class_='ht-away').text),
                'home_score_ft': int(element.find('span', class_='ft-home').text),
                'away_score_ft': int(element.find('span', class_='ft-away').text),
                'status': 'finished',
                'match_time': '90\'',
                'match_date': datetime.now(),  # Extrair data real
                'source_url': BET365_RESULTS_URL,
                'additional_data': {}
            }
            
            return match_data
            
        except Exception as e:
            logger.debug(f"Erro ao parsear resultado: {e}")
            return None
    
    def _capture_network_data(self) -> List[Dict]:
        """
        Tenta capturar dados JSON das requisições de rede
        """
        matches = []
        try:
            # Obtém logs de performance que incluem network requests
            logs = self.driver.get_log('performance')
            
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    
                    # Procura por requisições que possam conter dados de partidas
                    if message['method'] == 'Network.responseReceived':
                        url = message['params']['response']['url']
                        
                        # Filtrar URLs relevantes (ajustar conforme necessário)
                        if any(keyword in url.lower() for keyword in ['virtual', 'sport', 'event', 'match', 'fixture']):
                            logger.debug(f"URL relevante encontrada: {url}")
                            
                            # Tentar obter o corpo da resposta
                            try:
                                request_id = message['params']['requestId']
                                response = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                
                                if response and 'body' in response:
                                    body = response['body']
                                    data = json.loads(body)
                                    
                                    # Processar dados JSON (adaptar conforme estrutura real)
                                    parsed = self._parse_json_data(data)
                                    if parsed:
                                        matches.extend(parsed)
                                        
                            except Exception as e:
                                logger.debug(f"Não foi possível obter corpo da resposta: {e}")
                                
                except Exception as e:
                    logger.debug(f"Erro ao processar log: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Erro ao capturar network data: {e}")
        
        return matches
    
    def _parse_json_data(self, data: Dict) -> List[Dict]:
        """
        Parse dados JSON capturados da rede
        ⚠️ Estrutura precisa ser adaptada conforme API real
        """
        matches = []
        
        try:
            # Exemplo - adaptar conforme estrutura real
            # Pode ser data['events'], data['matches'], data['fixtures'], etc.
            events = data.get('events', data.get('matches', data.get('data', [])))
            
            if isinstance(events, list):
                for event in events:
                    match = self._extract_match_from_json(event)
                    if match:
                        matches.append(match)
            elif isinstance(events, dict):
                match = self._extract_match_from_json(events)
                if match:
                    matches.append(match)
                    
        except Exception as e:
            logger.debug(f"Erro ao parsear JSON: {e}")
        
        return matches
    
    def _extract_match_from_json(self, event: Dict) -> Optional[Dict]:
        """
        Extrai dados de partida de um objeto JSON
        ⚠️ Adaptar campos conforme estrutura real
        """
        try:
            # Exemplo de estrutura - ADAPTAR
            match_data = {
                'match_id': event.get('id', event.get('eventId', f"vf_{int(datetime.now().timestamp())}")),
                'competition': event.get('competition', event.get('league', 'VIRTUAL')),
                'home_team': event.get('homeTeam', event.get('home', {}).get('name', 'Unknown')),
                'away_team': event.get('awayTeam', event.get('away', {}).get('name', 'Unknown')),
                'home_score_ht': event.get('scores', {}).get('ht', {}).get('home'),
                'away_score_ht': event.get('scores', {}).get('ht', {}).get('away'),
                'home_score_ft': event.get('scores', {}).get('ft', {}).get('home'),
                'away_score_ft': event.get('scores', {}).get('ft', {}).get('away'),
                'status': event.get('status', 'live'),
                'match_time': event.get('time', event.get('minute', '')),
                'match_date': datetime.now(),
                'source_url': self.driver.current_url,
                'additional_data': event
            }
            
            return match_data
            
        except Exception as e:
            logger.debug(f"Erro ao extrair partida do JSON: {e}")
            return None
    
    def save_matches_to_db(self, matches: List[Dict]):
        """Salva partidas no banco de dados"""
        with get_db() as db:
            new_count = 0
            updated_count = 0
            
            for match_data in matches:
                try:
                    # Verifica se já existe
                    existing = db.query(VirtualMatch).filter(
                        VirtualMatch.match_id == match_data['match_id']
                    ).first()
                    
                    if existing:
                        # Atualiza
                        for key, value in match_data.items():
                            setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Cria novo
                        match = VirtualMatch(**match_data)
                        db.add(match)
                        new_count += 1
                        
                except Exception as e:
                    logger.error(f"Erro ao salvar partida {match_data.get('match_id')}: {e}")
                    continue
            
            db.commit()
            logger.info(f"Salvo no BD: {new_count} novas, {updated_count} atualizadas")
            
            return new_count, updated_count
    
    def run_scraping_cycle(self):
        """Executa um ciclo completo de scraping"""
        log = ScraperLog(started_at=datetime.utcnow())
        
        try:
            self.setup_driver()
            
            # Scrape partidas ao vivo
            live_matches = self.scrape_live_matches()
            
            # Scrape histórico
            historical_matches = self.scrape_results_history()
            
            # Combina resultados
            all_matches = live_matches + historical_matches
            
            # Salva no banco
            new_count, updated_count = self.save_matches_to_db(all_matches)
            
            log.finished_at = datetime.utcnow()
            log.status = 'success'
            log.matches_found = len(all_matches)
            log.matches_new = new_count
            log.matches_updated = updated_count
            
        except Exception as e:
            log.finished_at = datetime.utcnow()
            log.status = 'error'
            log.error_message = str(e)
            logger.error(f"Erro no ciclo de scraping: {e}")
            
        finally:
            self.close_driver()
            
            # Salva log e captura valores antes de fechar sessão
            with get_db() as db:
                db.add(log)
                db.commit()
                db.refresh(log)  # Recarrega para garantir que está atualizado
                
                # Captura todos os valores necessários antes da sessão fechar
                log_data = {
                    'status': log.status,
                    'matches_found': log.matches_found,
                    'matches_new': log.matches_new,
                    'matches_updated': log.matches_updated,
                    'error_message': log.error_message,
                    'started_at': log.started_at,
                    'finished_at': log.finished_at
                }
        
        # Retorna dicionário ao invés do objeto desconectado
        return type('ScraperResult', (), log_data)()


# Função para uso externo
def run_scraper():
    """Função principal para executar o scraper"""
    scraper = Bet365VirtualScraper()
    return scraper.run_scraping_cycle()


if __name__ == "__main__":
    from database import init_db
    init_db()
    run_scraper()
