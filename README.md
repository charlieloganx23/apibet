# 🎯 ApiBet - Sistema de Predições de Futebol Virtual

Sistema completo de predições com Machine Learning, API REST, WebSocket tempo real, Analytics e Recomendações.

## 🚀 Inicialização Rápida (NOVO!)

### ⚡ Método Mais Fácil - Duplo Clique
```
1. Duplo clique em: START_AQUI.bat
2. Aguarde 10 segundos
3. Pronto! O navegador abrirá automaticamente 🎉
```

### 🐍 Ou via Python
```bash
python start.py
```

**Isso é tudo!** O sistema agora:
- ✅ Inicia API e Dashboard automaticamente
- ✅ Verifica e libera portas em uso
- ✅ Abre o navegador no dashboard
- ✅ Mostra status e URLs de acesso
- ✅ Encerra tudo com CTRL+C

## 📊 URLs do Sistema

| Serviço | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000/dashboard.html |
| **API Docs** | http://localhost:8000/docs |
| **WebSocket** | ws://localhost:8000/ws |

## 🎮 Funcionalidades (Todas as 4 Fases)

### Fase 1: Dashboard ✅
- Interface responsiva
- Visualização de partidas
- Predições com ML

### Fase 2: API REST ✅
- 16 endpoints
- Controle do scraper
- Documentação automática

### Fase 3: Tempo Real ✅
- WebSocket
- Toast notifications  
- Logs do scraper

### Fase 4: Analytics ✅
- KPIs e gráficos
- Recomendações de apostas
- Export CSV

## 📋 Comandos do Scraper

```bash
# Executar uma vez
python main_rapidapi.py once

# Ver estatísticas
python main_rapidapi.py stats

# Predizer partida
python predict_match.py 21:00
```

## 🐛 Solução de Problemas

### WebSocket desconectado?
1. Use `START_AQUI.bat` ou `python start.py`
2. Abra http://localhost:3000 (não file://)
3. Console (F12) para ver erros

### Porta em uso?
- O `start.py` libera automaticamente!

## 📊 Estatísticas

- Taxa de Acerto: 58.3%
- Total de Partidas: 200+
- Ligas: 5 (Express, Copa, Super, Euro, Premier)
- Versão: 1.4.0

## 🚀 Melhorias v1.4.0

✨ **Novo Sistema de Inicialização Unificado**
- ➕ `start.py` - Inicia tudo automaticamente
- ➕ `START_AQUI.bat` - Duplo clique para iniciar
- ➕ Verificação e liberação de portas
- ➕ Abertura automática do navegador
- ➕ Feedback visual colorido
- ➕ Encerramento graceful com CTRL+C

📊 **Analytics Completo**
- KPIs visuais
- Gráficos Chart.js
- Recomendações de apostas
- Export CSV

---

**GitHub**: https://github.com/charlieloganx23/apibet
