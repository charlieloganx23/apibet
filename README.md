# 🎰 Bet365 Virtual Football API

Sistema de scraping e API REST para capturar e servir dados de Futebol Virtual da Bet365.

## ⚠️ AVISOS IMPORTANTES

1. **Legalidade**: Este projeto é apenas para fins educacionais. Web scraping pode violar os Termos de Serviço do site.
2. **Responsabilidade**: O uso deste código é por sua conta e risco.
3. **Bet365**: Não possui API pública oficial para Futebol Virtual.
4. **Manutenção**: Proteções anti-bot e estrutura do site mudam frequentemente.

## 🚀 Funcionalidades

- ✅ Scraping de partidas ao vivo de Futebol Virtual
- ✅ Scraping de histórico de resultados
- ✅ Banco de dados para armazenamento
- ✅ API REST completa com FastAPI
- ✅ Scheduler para execução automática
- ✅ Suporte a múltiplas competições (Mundial, Premiership, Superliga)
- ✅ Logs detalhados de execução

## 📋 Requisitos

- Python 3.9+
- Chrome/Chromium instalado
- ChromeDriver compatível com versão do Chrome

## 🔧 Instalação

### 1. Clone ou baixe o projeto

```bash
cd apibet
```

### 2. Crie um ambiente virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```powershell
pip install -r requirements.txt
```

### 4. Instale o ChromeDriver

```powershell
# Opção 1: Usando webdriver-manager (recomendado)
pip install webdriver-manager

# Opção 2: Download manual
# https://chromedriver.chromium.org/downloads
# Coloque no PATH do sistema
```

### 5. Configure as variáveis de ambiente

```powershell
Copy-Item .env.example .env
# Edite o arquivo .env conforme necessário
```

### 6. Inicialize o banco de dados

```powershell
python main.py init-db
```

## 📖 Uso

### Modo 1: Scraping Único (Teste)

```powershell
python main.py once
```

### Modo 2: API REST

```powershell
python main.py api
```

Acesse a documentação interativa em: `http://localhost:8000/docs`

### Modo 3: Scheduler Automático

```powershell
python main.py scraper
```

Executa scraping automaticamente a cada X minutos (configurável em `.env`).

### Modo 4: Rodar Ambos (API + Scheduler)

```powershell
# Terminal 1
python main.py api

# Terminal 2
python main.py scraper
```

## 🔌 Endpoints da API

### Partidas

- `GET /matches` - Lista partidas com filtros
  - Parâmetros: `competition`, `status`, `date_from`, `date_to`, `limit`, `offset`
- `GET /matches/{match_id}` - Detalhes de uma partida
- `GET /matches/live/current` - Partidas ao vivo

### Resultados

- `GET /results/recent` - Resultados recentes
  - Parâmetros: `hours`, `competition`

### Informações

- `GET /competitions` - Lista competições disponíveis
- `GET /stats` - Estatísticas gerais

### Scraper

- `GET /scraper/logs` - Logs de execução
- `GET /scraper/status` - Status do último scraping
- `POST /scraper/run` - Dispara scraping manual

## 📁 Estrutura do Projeto

```
apibet/
├── main.py              # Script principal
├── api.py               # API REST (FastAPI)
├── scraper.py           # Lógica de scraping
├── scheduler.py         # Agendador automático
├── models.py            # Modelos do banco de dados
├── database.py          # Conexão e sessões
├── config.py            # Configurações
├── requirements.txt     # Dependências
├── .env.example         # Exemplo de variáveis
├── .gitignore           # Arquivos ignorados
└── logs/                # Logs da aplicação
```

## ⚙️ Configurações (.env)

```ini
# Banco de dados
DATABASE_URL=sqlite:///./bet365_virtual.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Scraper
SCRAPER_INTERVAL_MINUTES=5
SCRAPER_HEADLESS=True

# Bet365 URLs
BET365_URL=https://www.bet365.com/#/AVR/B146/R^1/
BET365_RESULTS_URL=https://extra.bet365.com/results
```

## 🛠️ Desenvolvimento

### ⚠️ IMPORTANTE: Adaptar Seletores HTML

O arquivo `scraper.py` contém seletores CSS **fictícios** que precisam ser adaptados:

1. Acesse o site da Bet365
2. Inspecione o HTML das partidas
3. Identifique os seletores corretos
4. Atualize os métodos `_parse_match_element()` e `_parse_result_element()`

### Método Alternativo: Interceptar Requisições

Se o site carrega dados via API interna (JSON), pode ser mais eficiente:

```python
# Usar Selenium Wire ou Playwright para capturar requisições XHR/Fetch
# Exemplo com Playwright:
from playwright.sync_api import sync_playwright

def intercept_requests():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Interceptar requisições
        page.on("response", lambda response: 
            print(response.url, response.status)
        )
        
        page.goto("https://www.bet365.com/...")
        # Filtrar URLs relevantes e extrair JSON
```

## 📊 Banco de Dados

### Tabelas

1. **virtual_matches** - Partidas de futebol virtual
2. **virtual_match_markets** - Mercados específicos
3. **scraper_logs** - Logs de execução

### Exemplos de Queries

```python
from database import get_db
from models import VirtualMatch

with get_db() as db:
    # Últimas 10 partidas
    matches = db.query(VirtualMatch).order_by(
        VirtualMatch.match_date.desc()
    ).limit(10).all()
    
    # Partidas ao vivo
    live = db.query(VirtualMatch).filter(
        VirtualMatch.status == 'live'
    ).all()
```

## 🐛 Troubleshooting

### Erro: ChromeDriver não encontrado

```powershell
pip install webdriver-manager
```

Ou baixe manualmente em: https://chromedriver.chromium.org/

### Erro: Cloudflare/Captcha

O site detectou bot. Soluções:

1. Use proxy rotativo
2. Implemente delay entre requisições
3. Use Playwright Stealth
4. Considere serviços de bypass (Bright Data, ScraperAPI)

### Erro: Seletores não encontram elementos

Atualize os seletores CSS no `scraper.py` conforme estrutura real do site.

## 📝 TODO / Melhorias Futuras

- [ ] Implementar captura de odds
- [ ] Adicionar mais mercados (Over/Under, Ambas Marcam, etc.)
- [ ] Sistema de notificações (Telegram, Discord)
- [ ] Dashboard web para visualização
- [ ] Docker/Docker Compose
- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Backup automático do banco

## 📄 Licença

Este projeto é apenas para fins educacionais. Use por sua conta e risco.

## 🤝 Contribuições

Este é um projeto de exemplo. Adapte conforme suas necessidades.

## 📞 Suporte

Para dúvidas sobre implementação, consulte:
- Documentação do Selenium: https://selenium-python.readthedocs.io/
- Documentação do FastAPI: https://fastapi.tiangolo.com/
- Documentação do Playwright: https://playwright.dev/python/

---

**Lembrete Final**: Sempre verifique a legalidade do web scraping na sua jurisdição e respeite os Termos de Serviço dos sites.
