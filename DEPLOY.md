# Guia de Deploy - Bet365 Virtual Football API

## 🐳 Deploy com Docker

### 1. Criar Dockerfile

```dockerfile
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instala Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instala ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py", "api"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/bet365
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  scraper:
    build: .
    command: python main.py scraper
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/bet365
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=bet365
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## ☁️ Deploy em VPS (Ubuntu/Debian)

### 1. Preparar o servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Instalar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Instalar ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
CHROMEDRIVER_VERSION=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 2. Configurar aplicação

```bash
# Clone ou envie os arquivos
git clone <seu-repo> /opt/bet365-api
cd /opt/bet365-api

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
nano .env  # Editar configurações
```

### 3. Configurar systemd (API)

```bash
sudo nano /etc/systemd/system/bet365-api.service
```

```ini
[Unit]
Description=Bet365 Virtual Football API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/bet365-api
Environment="PATH=/opt/bet365-api/venv/bin"
ExecStart=/opt/bet365-api/venv/bin/python main.py api
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Configurar systemd (Scraper)

```bash
sudo nano /etc/systemd/system/bet365-scraper.service
```

```ini
[Unit]
Description=Bet365 Virtual Football Scraper
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/bet365-api
Environment="PATH=/opt/bet365-api/venv/bin"
ExecStart=/opt/bet365-api/venv/bin/python main.py scraper
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Iniciar serviços

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar
sudo systemctl enable bet365-api bet365-scraper
sudo systemctl start bet365-api bet365-scraper

# Verificar status
sudo systemctl status bet365-api
sudo systemctl status bet365-scraper

# Ver logs
sudo journalctl -u bet365-api -f
```

## 🌐 Configurar Nginx (Reverse Proxy)

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/bet365-api
```

```nginx
server {
    listen 80;
    server_name api.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/bet365-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 SSL com Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.seudominio.com
```

## 📊 Monitoramento

### 1. Instalar supervisord (alternativa ao systemd)

```bash
sudo apt install supervisor -y
sudo nano /etc/supervisor/conf.d/bet365-api.conf
```

```ini
[program:bet365-api]
command=/opt/bet365-api/venv/bin/python main.py api
directory=/opt/bet365-api
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/bet365-api.err.log
stdout_logfile=/var/log/bet365-api.out.log

[program:bet365-scraper]
command=/opt/bet365-api/venv/bin/python main.py scraper
directory=/opt/bet365-api
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/bet365-scraper.err.log
stdout_logfile=/var/log/bet365-scraper.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

## 🔄 Backup Automático

```bash
sudo nano /opt/bet365-api/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/bet365"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup do banco SQLite (se usar)
cp /opt/bet365-api/bet365_virtual.db $BACKUP_DIR/db_$DATE.db

# Backup do PostgreSQL (se usar)
# pg_dump -U user bet365 > $BACKUP_DIR/db_$DATE.sql

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "db_*.db" -mtime +7 -delete
```

```bash
chmod +x /opt/bet365-api/backup.sh

# Agendar no cron (diário às 3h)
sudo crontab -e
0 3 * * * /opt/bet365-api/backup.sh
```

## 🚀 Deploy em Cloud

### Heroku

```bash
# Criar Procfile
web: python main.py api
worker: python main.py scraper
```

### Railway / Render

Adicionar configurações no dashboard:
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py api`

### AWS EC2 / Google Cloud / Azure

Seguir os passos de VPS acima, adaptando para o provider.

## 📝 Checklist de Produção

- [ ] Configurar variáveis de ambiente
- [ ] Usar PostgreSQL ao invés de SQLite
- [ ] Configurar logs rotativos
- [ ] Implementar rate limiting
- [ ] Adicionar autenticação na API
- [ ] Configurar HTTPS/SSL
- [ ] Monitorar uso de recursos
- [ ] Configurar alertas (Sentry, etc)
- [ ] Fazer backup regular
- [ ] Documentar processos
