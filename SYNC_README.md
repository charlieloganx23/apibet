# 🔄 Sistema de Sincronização Automática

## ⏰ Correlação de Horários

**IMPORTANTE**: O sistema está sincronizado com o horário do site Bet365, não com o horário local do computador.

```
Horário LOCAL do computador: 12:22
Horário do SITE Bet365:      16:22 (+4 horas)
```

Esta correlação é aplicada automaticamente em todo o sistema para garantir que:
- ✅ Jogos sejam marcados como "ao vivo" no momento correto
- ✅ Jogos expirados sejam identificados após 2h do horário previsto
- ✅ Novos jogos sejam coletados no momento certo
- ✅ Resultados sejam atualizados quando disponíveis

## 📁 Arquivos Principais

### 1. `auto_sync.py`
Executa sincronização completa em 4 passos:
1. ✅ Atualiza status das partidas (usando +4h)
2. 📊 Coleta novos jogos via scraper
3. 🏆 Coleta resultados de jogos finalizados
4. ✅ Atualiza status novamente após coleta

**Uso:**
```bash
python auto_sync.py
```

### 2. `auto_scheduler.py`
Executa `auto_sync.py` automaticamente em intervalos regulares.

**Uso:**
```bash
# A cada 30 minutos (padrão)
python auto_scheduler.py

# A cada 15 minutos
python auto_scheduler.py --interval 15

# A cada 60 minutos
python auto_scheduler.py --interval 60
```

### 3. `START_SYNC.bat`
Interface amigável para Windows com menu de opções.

**Uso:**
- Duplo clique no arquivo
- Escolha uma opção:
  - [1] Sincronização única
  - [2] Automático a cada 30 min
  - [3] Automático a cada 15 min

## 🔧 Arquivos Atualizados

Os seguintes arquivos foram atualizados para usar o offset de +4h:

- ✅ `web_api.py` - Endpoints da API
- ✅ `scraper_rapidapi.py` - Coleta de jogos
- ✅ `results_collector.py` - Coleta de resultados
- ✅ `sync_match_status.py` - Atualização de status

## 📊 Status das Partidas

O sistema define o status automaticamente baseado no horário:

| Status | Descrição | Condição |
|--------|-----------|----------|
| 📅 **scheduled** | Agendado | Falta mais de 2h para começar |
| 🔴 **live** | Ao vivo | Entre 2h antes e 30min depois do horário |
| ⏰ **expired** | Expirado | Mais de 30min atrás, sem resultado |
| ✅ **finished** | Finalizado | Tem resultado (gols definidos) |

## 🎯 Lógica de Horários

```python
# Horário do site (local + 4h)
site_time = datetime.now() + timedelta(hours=4)

# Parse horário da partida (ex: "16:22")
match_hour, match_minute = parse(match.scheduled_time)

# Cria datetime da partida no horário do site
match_datetime = site_time.replace(hour=match_hour, minute=match_minute)

# Ajusta para amanhã se necessário
if match_datetime < site_time and time_diff > 12h:
    match_datetime += timedelta(days=1)

# Calcula diferença
time_diff_minutes = (match_datetime - site_time).total_seconds() / 60

# Define status
if time_diff_minutes > 120:      # +2h no futuro
    status = "scheduled"
elif time_diff_minutes > -30:    # Entre -30min e +2h
    status = "live"
else:                             # -30min ou mais
    status = "expired"
```

## 🚀 Início Rápido

### Sincronização Única
```bash
python auto_sync.py
```

### Sincronização Automática
```bash
# Mantém sincronizado a cada 30 minutos
python auto_scheduler.py
```

### Verificar Status Atual
```bash
python check_time_sync.py
```

## 📈 Exemplo de Saída

```
================================================================================
🔄 INICIANDO SINCRONIZAÇÃO AUTOMÁTICA
   Ligas: express, copa, super, euro, premier
   Horário local: 06/01/2026 12:25:57
   Horário do site: 06/01/2026 16:25:57
================================================================================

📌 PASSO 1/4: Atualizando status das partidas...
   ✅ Status atualizados:
      📅 Agendados: 384
      🔴 Ao vivo: 0
      ⏰ Expirados: 0
      ✅ Finalizados: 138

📌 PASSO 2/4: Coletando novos jogos...
   ✅ Liga express: 2 novas, 4 atualizadas
   ✅ Liga copa: 2 novas, 4 atualizadas
   ...

📌 PASSO 3/4: Coletando resultados...
   ✅ Liga express: 5/10 partidas atualizadas
   ...

📌 PASSO 4/4: Atualizando status final...
   ✅ Status atualizados:
      📅 Agendados: 386
      ✅ Finalizados: 143

✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO
```

## ⚙️ Configuração

### Intervalo de Sincronização
Edite `config.py` para ajustar configurações:

```python
# Intervalo padrão (minutos)
SYNC_INTERVAL = 30

# Offset de horário (site vs local)
TIME_OFFSET_HOURS = 4

# Ligas para sincronizar
RAPIDAPI_LEAGUES = ['express', 'copa', 'super', 'euro', 'premier']
```

## 🐛 Troubleshooting

### Horários Incorretos
Se os horários não estão corretos:
1. Verifique se o offset de +4h está aplicado
2. Execute `python check_time_sync.py` para diagnóstico
3. Verifique o fuso horário do sistema

### Sincronização Não Atualiza
1. Verifique conexão com a API RapidAPI
2. Verifique chave de API em `.env`
3. Execute manualmente: `python auto_sync.py`

### Status "Expired" Incorreto
1. Execute `python auto_sync.py` para recalcular
2. Verifique se o horário do sistema está correto
3. Confirme offset de +4h em `web_api.py`

## 📝 Logs

Os logs de sincronização são salvos em:
- Console (stdout)
- Arquivo: `logs/sync.log` (se configurado)

## 🔗 Integração com Dashboard

O dashboard web em `web/dashboard.html` atualiza automaticamente:
- Status das partidas em tempo real
- Novos jogos coletados
- Resultados finalizados
- Badges de validação (✅/❌/⚪/🔴/⏰)

## ✨ Recursos

- ✅ Sincronização automática com offset de +4h
- ✅ Coleta de novos jogos em 5 ligas
- ✅ Atualização de resultados históricos
- ✅ Cálculo dinâmico de status
- ✅ Interface amigável (START_SYNC.bat)
- ✅ Logs detalhados
- ✅ Tratamento de erros robusto
- ✅ Suporte a múltiplos intervalos

## 📚 Documentação Adicional

- [README.md](README.md) - Documentação principal
- [DEPLOY.md](DEPLOY.md) - Guia de deploy
- [SISTEMA_AUTOMACAO.md](SISTEMA_AUTOMACAO.md) - Automação completa

---

🎯 **ApiBet** - Sistema de Predições de Futebol Virtual com IA
