// ============================================================================
// Configuração da API
// ============================================================================
const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';
const USE_API = true; // Se false, usa JSON estático

// Estado global
let allMatches = [];
let filteredMatches = [];
let stats = {};
let scraperStatus = { is_running: false };
let websocket = null;
let wsReconnectAttempts = 0;
const MAX_WS_RECONNECT_ATTEMPTS = 5;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Dashboard inicializando...');
    console.log('📡 API_URL:', API_URL);
    console.log('🔌 WS_URL:', WS_URL);
    console.log('⚙️ USE_API:', USE_API);
    
    initializeEventListeners();
    loadData();
    updateScraperStatus();
    
    // Conectar WebSocket se API estiver ativada
    if (USE_API) {
        console.log('🔌 Iniciando conexão WebSocket...');
        connectWebSocket();
    } else {
        console.log('⚠️ WebSocket desabilitado (USE_API = false)');
    }
});

// Event Listeners
function initializeEventListeners() {
    document.getElementById('btnRefresh').addEventListener('click', loadData);
    document.getElementById('btnAnalyze').addEventListener('click', showAnalysis);
    document.getElementById('btnApplyFilter').addEventListener('click', applyFilters);
    document.getElementById('btnExport').addEventListener('click', exportToCSV);
    
    // Controle do scraper (Fase 2)
    document.getElementById('btnStartScraper').addEventListener('click', startScraper);
    document.getElementById('btnStopScraper').addEventListener('click', stopScraper);
    
    // Logs (Fase 3)
    document.getElementById('btnLogs').addEventListener('click', showLogs);
    document.getElementById('btnRefreshLogs')?.addEventListener('click', loadLogs);
    
    // Analytics & Recommendations (Fase 4)
    document.getElementById('btnAnalytics')?.addEventListener('click', showAnalytics);
    document.getElementById('btnRecommendations')?.addEventListener('click', showRecommendations);
    document.getElementById('btnRefreshRec')?.addEventListener('click', loadRecommendations);
    document.getElementById('btnExportCSV')?.addEventListener('click', exportCSV);
}

// ============================================================================
// Fase 3: WebSocket Tempo Real
// ============================================================================

function connectWebSocket() {
    console.log('🔌 Tentando conectar WebSocket em:', WS_URL);
    console.log('📍 Location:', window.location.href);
    console.log('🌐 Protocol:', window.location.protocol);
    
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        console.log('✅ WebSocket já está conectado');
        return; // Já conectado
    }
    
    try {
        console.log('🔄 Criando nova conexão WebSocket...');
        console.log('📊 WebSocket.CONNECTING:', WebSocket.CONNECTING);
        console.log('📊 WebSocket.OPEN:', WebSocket.OPEN);
        console.log('📊 WebSocket.CLOSING:', WebSocket.CLOSING);
        console.log('📊 WebSocket.CLOSED:', WebSocket.CLOSED);
        
        websocket = new WebSocket(WS_URL);
        console.log('✅ Objeto WebSocket criado, readyState:', websocket.readyState);
        
        websocket.onopen = () => {
            console.log('✅ WebSocket conectado! readyState:', websocket.readyState);
            wsReconnectAttempts = 0;
            updateWSStatus('🟢 Conectado', 'success');
            showToast('Conectado ao servidor em tempo real', 'success');
        };
        
        websocket.onmessage = (event) => {
            console.log('📨 Mensagem WebSocket recebida:', event.data);
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        websocket.onerror = (error) => {
            console.error('❌ Erro no WebSocket:', error);
            console.error('❌ WebSocket readyState:', websocket.readyState);
            console.error('❌ Error object:', error);
            updateWSStatus('🔴 Erro', 'error');
        };
        
        websocket.onclose = (event) => {
            console.log('⚠️ WebSocket desconectado');
            console.log('📊 Close event:', {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean
            });
            updateWSStatus('🟡 Desconectado', 'warning');
            
            // Tentar reconectar
            if (wsReconnectAttempts < MAX_WS_RECONNECT_ATTEMPTS) {
                wsReconnectAttempts++;
                const delay = 3000 * wsReconnectAttempts;
                console.log(`🔄 Agendando reconexão em ${delay}ms (${wsReconnectAttempts}/${MAX_WS_RECONNECT_ATTEMPTS})...`);
                setTimeout(() => {
                    console.log(`🔄 Tentando reconectar (${wsReconnectAttempts}/${MAX_WS_RECONNECT_ATTEMPTS})...`);
                    connectWebSocket();
                }, delay); // Backoff exponencial
            } else {
                console.log('❌ Máximo de tentativas de reconexão atingido');
            }
        };
        
        // Ping a cada 25s para manter conexão
        setInterval(() => {
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                console.log('🏓 Enviando ping...');
                websocket.send('ping');
            }
        }, 25000);
        
    } catch (error) {
        console.error('❌ Erro ao conectar WebSocket:', error);
        console.error('❌ Stack:', error.stack);
        updateWSStatus('🔴 Falha', 'error');
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'connected':
            console.log('📡 WebSocket inicializado:', data);
            break;
        
        case 'new_matches':
            console.log(`🆕 ${data.count} novas partidas adicionadas!`);
            showToast(
                `🆕 ${data.count} nova${data.count > 1 ? 's' : ''} partida${data.count > 1 ? 's' : ''} adicionada${data.count > 1 ? 's' : ''}!`,
                'info'
            );
            
            // Atualizar dados automaticamente
            loadData();
            break;
        
        case 'results_updated':
            console.log(`✅ ${data.count} resultado(s) atualizado(s)!`);
            showToast(
                `✅ ${data.count} resultado${data.count > 1 ? 's' : ''} atualizado${data.count > 1 ? 's' : ''}!`,
                'success'
            );
            
            // Recarregar dados e estatísticas
            loadData();
            if (document.getElementById('analyticsSection').style.display !== 'none') {
                loadPredictionStats();
            }
            break;
        
        case 'result_updated':
            console.log(`🎯 Resultado atualizado: ${data.match} - ${data.score}`);
            showToast(
                `🎯 ${data.match}: ${data.score}`,
                'info'
            );
            
            // Recarregar dados e estatísticas
            loadData();
            if (document.getElementById('analyticsSection').style.display !== 'none') {
                loadPredictionStats();
            }
            break;
        
        case 'pong':
            console.log('🏓 Pong recebido');
            break;
        
        case 'heartbeat':
            console.log('💓 Heartbeat');
            break;
        
        default:
            console.log('📨 Mensagem WebSocket:', data);
    }
}

function updateWSStatus(text, type = 'info') {
    const statusEl = document.getElementById('wsStatus');
    if (statusEl) {
        statusEl.textContent = text;
        
        if (type === 'success') {
            statusEl.style.color = '#10b981';
        } else if (type === 'error') {
            statusEl.style.color = '#ef4444';
        } else if (type === 'warning') {
            statusEl.style.color = '#f59e0b';
        } else {
            statusEl.style.color = '#6b7280';
        }
    }
}

// ============================================================================
// Fase 3: Sistema de Notificações Toast
// ============================================================================

function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: '💡'
    }[type] || '💡';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Animação de entrada
    setTimeout(() => toast.classList.add('toast-show'), 10);
    
    // Remover automaticamente
    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================================================
// Fase 3: Logs do Scraper
// ============================================================================

async function showLogs() {
    document.getElementById('logsSection').style.display = 'block';
    document.getElementById('logsSection').scrollIntoView({ behavior: 'smooth' });
    loadLogs();
}

async function loadLogs() {
    if (!USE_API) {
        document.getElementById('logsContainer').innerHTML = 
            '<div class="loading">⚠️ Ative o modo API para ver logs</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/logs?limit=20`);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        displayLogs(data.logs);
        
    } catch (error) {
        console.error('Erro ao carregar logs:', error);
        document.getElementById('logsContainer').innerHTML = 
            `<div class="loading" style="color: #ef4444;">❌ Erro ao carregar logs: ${error.message}</div>`;
    }
}

function displayLogs(logs) {
    const container = document.getElementById('logsContainer');
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<div class="loading">Nenhum log encontrado</div>';
        return;
    }
    
    container.innerHTML = logs.map(log => {
        const startDate = log.started_at ? new Date(log.started_at).toLocaleString('pt-BR') : 'N/A';
        const endDate = log.finished_at ? new Date(log.finished_at).toLocaleString('pt-BR') : 'Em execução';
        const duration = log.finished_at && log.started_at 
            ? `${((new Date(log.finished_at) - new Date(log.started_at)) / 1000).toFixed(1)}s`
            : '-';
        
        const statusClass = log.status === 'success' ? 'success' : 
                           log.status === 'error' ? 'error' : 'warning';
        
        const statusIcon = log.status === 'success' ? '✅' : 
                          log.status === 'error' ? '❌' : '⚠️';
        
        return `
            <div class="log-item log-${statusClass}">
                <div class="log-header">
                    <div class="log-status">${statusIcon} ${log.status.toUpperCase()}</div>
                    <div class="log-date">${startDate}</div>
                </div>
                <div class="log-details">
                    <div class="log-stat">
                        <strong>Encontradas:</strong> ${log.matches_found || 0}
                    </div>
                    <div class="log-stat">
                        <strong>Novas:</strong> ${log.matches_new || 0}
                    </div>
                    <div class="log-stat">
                        <strong>Atualizadas:</strong> ${log.matches_updated || 0}
                    </div>
                    <div class="log-stat">
                        <strong>Duração:</strong> ${duration}
                    </div>
                </div>
                ${log.error_message ? `
                    <div class="log-error">
                        <strong>Erro:</strong> ${log.error_message}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Carregar dados do banco
async function loadData() {
    showLoading(true);
    updateStatus('Carregando dados...');
    
    try {
        if (USE_API) {
            // Usar API REST
            const response = await fetch(`${API_URL}/api/matches?limit=500`);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            allMatches = await response.json();
            
            // Buscar estatísticas
            const statsResponse = await fetch(`${API_URL}/api/stats`);
            if (statsResponse.ok) {
                stats = await statsResponse.json();
            }
        } else {
            // Fallback: usar JSON estático
            const response = await fetch('data/matches.json');
            
            if (!response.ok) {
                throw new Error('JSON não encontrado');
            }
            
            const data = await response.json();
            allMatches = data.matches;
            stats = data.stats;
        }
        
        updateDashboard();
        updateStatus('✅ Dados carregados via ' + (USE_API ? 'API' : 'JSON'), 'success');
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        updateStatus(`❌ Erro: ${error.message}`, 'error');
        
        // Fallback: tentar JSON se API falhou
        if (USE_API) {
            try {
                const response = await fetch('data/matches.json');
                const data = await response.json();
                allMatches = data.matches;
                stats = data.stats;
                updateDashboard();
                updateStatus('⚠️ Usando dados em cache (API offline)', 'warning');
            } catch (fallbackError) {
                updateStatus('❌ API offline e sem cache', 'error');
            }
        }
    } finally {
        showLoading(false);
    }
}

// Executar script Python para gerar JSON
async function executePythonScript() {
    updateStatus('Gerando dados do banco SQLite...');
    
    // Criar um iframe oculto para executar o script
    const notice = document.createElement('div');
    notice.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        z-index: 10000;
        max-width: 500px;
        text-align: center;
    `;
    notice.innerHTML = `
        <h2 style="margin-bottom: 20px;">📊 Primeira Execução</h2>
        <p style="margin-bottom: 20px;">Execute o seguinte comando no terminal:</p>
        <code style="display: block; background: #f3f4f6; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            python web_data_generator.py
        </code>
        <button onclick="location.reload()" style="padding: 12px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
            Executei! Recarregar
        </button>
    `;
    document.body.appendChild(notice);
    showLoading(false);
}

// Atualizar dashboard
function updateDashboard() {
    // Atualizar estatísticas
    document.getElementById('totalMatches').textContent = stats.total || 0;
    document.getElementById('finishedMatches').textContent = stats.finished || 0;
    document.getElementById('scheduledMatches').textContent = stats.scheduled || 0;
    document.getElementById('accuracyValue').textContent = 
        stats.accuracy ? `${stats.accuracy}%` : '-';
    
    // Atualizar última atualização
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleString('pt-BR');
    
    // Atualizar ligas
    updateLeaguesGrid();
    
    // Aplicar filtros iniciais
    applyFilters();
}

// Atualizar grid de ligas
function updateLeaguesGrid() {
    const grid = document.getElementById('leaguesGrid');
    const leagueStats = {};
    
    // Contar por liga
    allMatches.forEach(match => {
        leagueStats[match.league] = (leagueStats[match.league] || 0) + 1;
    });
    
    // Criar cards
    grid.innerHTML = Object.entries(leagueStats)
        .map(([league, count]) => `
            <div class="league-card">
                <div class="league-name">${league}</div>
                <div class="league-count">${count}</div>
            </div>
        `)
        .join('');
}

// Aplicar filtros
function applyFilters() {
    const leagueFilter = document.getElementById('filterLeague').value;
    const statusFilter = document.getElementById('filterStatus').value;
    const searchTerm = document.getElementById('searchTeam').value.toLowerCase();
    
    console.log('🔍 Aplicando filtros:', { leagueFilter, statusFilter, searchTerm });
    console.log('📊 Total de partidas antes do filtro:', allMatches.length);
    
    filteredMatches = allMatches.filter(match => {
        // Filtro de liga
        if (leagueFilter !== 'all' && match.league !== leagueFilter) {
            return false;
        }
        
        // Filtro de status (melhorado)
        if (statusFilter !== 'all') {
            if (statusFilter === 'finished') {
                // Finalizadas = tem resultado confirmado
                if (match.status !== 'finished') {
                    return false;
                }
            } else if (statusFilter === 'scheduled') {
                // Agendadas = scheduled, live ou expired (sem resultado)
                if (match.status === 'finished') {
                    return false;
                }
            }
        }
        
        // Busca por time
        if (searchTerm && 
            !match.team_home.toLowerCase().includes(searchTerm) &&
            !match.team_away.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        return true;
    });
    
    console.log('✅ Partidas após filtro:', filteredMatches.length);
    if (filteredMatches.length > 0) {
        console.log('📋 Exemplo de partida filtrada:', filteredMatches[0]);
    }
    
    updateTable();
}

// Atualizar tabela
function updateTable() {
    const tbody = document.getElementById('matchesTableBody');
    const count = document.getElementById('tableCount');
    
    count.textContent = `Mostrando ${filteredMatches.length} partidas`;
    
    if (filteredMatches.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="loading">Nenhuma partida encontrada</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredMatches
        .sort((a, b) => {
            // Ordenar por horário
            const timeA = parseInt(a.hour) * 60 + parseInt(a.minute);
            const timeB = parseInt(b.hour) * 60 + parseInt(b.minute);
            return timeA - timeB;
        })
        .slice(0, 50) // Limitar a 50 partidas
        .map(match => `
            <tr>
                <td><strong>${match.hour}:${match.minute}</strong></td>
                <td><span class="league-badge ${match.league}">${match.league}</span></td>
                <td>${match.team_home} <strong>vs</strong> ${match.team_away}</td>
                <td class="odd-value ${getOddClass(match.odd_home)}">${match.odd_home.toFixed(2)}</td>
                <td class="odd-value ${getOddClass(match.odd_draw)}">${match.odd_draw.toFixed(2)}</td>
                <td class="odd-value ${getOddClass(match.odd_away)}">${match.odd_away.toFixed(2)}</td>
                <td class="odd-value">${match.odd_under_25 ? match.odd_under_25.toFixed(2) : '-'}</td>
                <td class="odd-value">${match.odd_over_25 ? match.odd_over_25.toFixed(2) : '-'}</td>
                <td>
                    <button class="btn-predict" onclick="predictMatch('${match.hour}', '${match.minute}')">
                        🔮 Prever
                    </button>
                </td>
                <td class="validation-cell">
                    ${generateValidationBadges(match)}
                </td>
            </tr>
        `)
        .join('');
}

// Classificar odd por valor
function getOddClass(odd) {
    if (odd < 2.0) return 'odd-low';
    if (odd < 3.0) return 'odd-medium';
    return 'odd-high';
}

// Gerar badges de validação de predições
function generateValidationBadges(match) {
    // Status baseado em horário e resultado
    if (match.status === 'expired' && !match.result) {
        return '<span class="validation-badge expired">⏰ Aguardando Resultado</span>';
    }
    
    if (match.status === 'live') {
        return '<span class="validation-badge live">🔴 Ao Vivo / Em Breve</span>';
    }
    
    // Se não finalizado, mostra pendente
    if (match.status !== 'finished' || !match.result) {
        return '<span class="validation-badge pending">⚪ Agendado</span>';
    }
    
    // Calcular predições
    const odds = [match.odd_home, match.odd_draw, match.odd_away];
    const minOdd = Math.min(...odds);
    let predictedWinner = 'home';
    if (minOdd === match.odd_draw) predictedWinner = 'draw';
    else if (minOdd === match.odd_away) predictedWinner = 'away';
    
    const winnerLabel = { home: 'Casa', draw: 'Empate', away: 'Fora' };
    const actualLabel = { home: 'Casa', draw: 'Empate', away: 'Fora' };
    
    // Validar vencedor
    const winnerCorrect = predictedWinner === match.result;
    const winnerBadge = winnerCorrect 
        ? `<span class="validation-badge correct" title="Predição: ${winnerLabel[predictedWinner]}">✅ ${winnerLabel[predictedWinner]}</span>`
        : `<span class="validation-badge wrong" title="Predição: ${winnerLabel[predictedWinner]} | Real: ${actualLabel[match.result]}">❌ ${winnerLabel[predictedWinner]} → ${actualLabel[match.result]}</span>`;
    
    // Validar Under/Over 2.5
    let overUnderBadge = '';
    if (match.odd_under_25 && match.odd_over_25 && match.total_goals !== null) {
        const predictedOver = match.odd_over_25 < match.odd_under_25;
        const actualOver = match.total_goals > 2.5;
        const overUnderCorrect = predictedOver === actualOver;
        
        const predLabel = predictedOver ? 'Over 2.5' : 'Under 2.5';
        const actualLabel = actualOver ? 'Over 2.5' : 'Under 2.5';
        
        overUnderBadge = overUnderCorrect
            ? `<span class="validation-badge correct">✅ ${predLabel}</span>`
            : `<span class="validation-badge wrong" title="Real: ${actualLabel}">❌ ${predLabel}</span>`;
    }
    
    // Validar Ambas Marcam
    let bothScoreBadge = '';
    if (match.odd_both_score_yes && match.odd_both_score_no && match.goals_home !== null && match.goals_away !== null) {
        const predictedBothScore = match.odd_both_score_yes < match.odd_both_score_no;
        const actualBothScore = match.goals_home > 0 && match.goals_away > 0;
        const bothScoreCorrect = predictedBothScore === actualBothScore;
        
        const predLabel = predictedBothScore ? 'Ambas Sim' : 'Ambas Não';
        const actualLabel = actualBothScore ? 'Ambas Sim' : 'Ambas Não';
        
        bothScoreBadge = bothScoreCorrect
            ? `<span class="validation-badge correct">✅ ${predLabel}</span>`
            : `<span class="validation-badge wrong" title="Real: ${actualLabel}">❌ ${predLabel}</span>`;
    }
    
    // Mostrar placar
    const scoreDisplay = (match.goals_home !== null && match.goals_away !== null)
        ? `<div class="match-score">${match.goals_home} x ${match.goals_away}</div>`
        : '';
    
    return `
        <div class="validation-content">
            ${scoreDisplay}
            <div class="validation-badges">
                ${winnerBadge}
                ${overUnderBadge}
                ${bothScoreBadge}
            </div>
        </div>
    `;
}

// Predição de partida
async function predictMatch(hour, minute) {
    showLoading(true);
    document.getElementById('predictionsSection').style.display = 'block';
    document.getElementById('predictionsSection').scrollIntoView({ behavior: 'smooth' });
    
    try {
        if (USE_API) {
            // Usar API para predição
            const response = await fetch(`${API_URL}/api/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ hour, minute })
            });
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const prediction = await response.json();
            displayPrediction(prediction);
        } else {
            // Cálculo local (fallback)
            const match = allMatches.find(m => m.hour === hour && m.minute === minute);
            
            if (!match) {
                alert('Partida não encontrada!');
                return;
            }
            
            const prediction = calculateLocalPrediction(match);
            displayPrediction(prediction);
        }
    } catch (error) {
        console.error('Erro ao fazer predição:', error);
        updateStatus(`❌ Erro na predição: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Cálculo local de predição (fallback)
function calculateLocalPrediction(match) {
    
    // Calcular probabilidades implícitas
    const probHome = (1 / match.odd_home) * 100;
    const probDraw = (1 / match.odd_draw) * 100;
    const probAway = (1 / match.odd_away) * 100;
    const total = probHome + probDraw + probAway;
    
    // Normalizar
    const normHome = (probHome / total) * 100;
    const normDraw = (probDraw / total) * 100;
    const normAway = (probAway / total) * 100;
    
    // Gols
    const probUnder = match.odd_under_25 ? (1 / match.odd_under_25) * 100 : 0;
    const probOver = match.odd_over_25 ? (1 / match.odd_over_25) * 100 : 0;
    
    // Ambas marcam
    const probBothYes = match.odd_both_score_yes ? (1 / match.odd_both_score_yes) * 100 : 0;
    const probBothNo = match.odd_both_score_no ? (1 / match.odd_both_score_no) * 100 : 0;
    
    // Determinar favorito
    const maxProb = Math.max(normHome, normDraw, normAway);
    let resultado = 'Casa';
    if (normDraw === maxProb) resultado = 'Empate';
    if (normAway === maxProb) resultado = 'Fora';
    
    const isFavoriteStrong = maxProb > 45;
    
    const content = document.getElementById('predictionContent');
    content.innerHTML = `
        <div class="prediction-header">
            <div class="prediction-match">
                ${match.team_home} vs ${match.team_away}
            </div>
            <div style="color: #6b7280; margin-top: 10px;">
                🏆 Liga: ${match.league.toUpperCase()} | ⏰ ${match.hour}:${match.minute}
            </div>
        </div>
        
        <h3 style="margin-bottom: 15px;">📊 Odds do Mercado</h3>
        <div class="prediction-odds">
            <div class="odd-card">
                <div class="odd-label">🏠 Casa</div>
                <div class="odd-value-large">${match.odd_home.toFixed(2)}</div>
                <div class="odd-label">${normHome.toFixed(1)}%</div>
            </div>
            <div class="odd-card">
                <div class="odd-label">🤝 Empate</div>
                <div class="odd-value-large">${match.odd_draw.toFixed(2)}</div>
                <div class="odd-label">${normDraw.toFixed(1)}%</div>
            </div>
            <div class="odd-card">
                <div class="odd-label">✈️ Fora</div>
                <div class="odd-value-large">${match.odd_away.toFixed(2)}</div>
                <div class="odd-label">${normAway.toFixed(1)}%</div>
            </div>
        </div>
        
        <div class="prediction-result">
            <h3>🎯 Predição Final</h3>
            <div class="prediction-item">
                <strong>1️⃣ Resultado:</strong> Vitória da <strong>${resultado}</strong> (${maxProb.toFixed(1)}% de confiança)
                ${isFavoriteStrong ? '<span style="color: #10b981;"> ✅ Favorito Forte</span>' : '<span style="color: #f59e0b;"> ⚠️ Jogo Equilibrado</span>'}
            </div>
            <div class="prediction-item">
                <strong>2️⃣ Total de Gols:</strong> ${probUnder > probOver ? 'UNDER 2.5' : 'OVER 2.5'} (${Math.max(probUnder, probOver).toFixed(1)}% de confiança)
            </div>
            <div class="prediction-item">
                <strong>3️⃣ Ambas Marcam:</strong> ${probBothNo > probBothYes ? 'NÃO' : 'SIM'} (${Math.max(probBothYes, probBothNo).toFixed(1)}% de confiança)
            </div>
        </div>
        
        <div class="prediction-result" style="margin-top: 20px; background: #fef3c7;">
            <h3>💡 Recomendações</h3>
            <div class="prediction-item">
                ${isFavoriteStrong ? 
                    '✅ Favorito forte: Alta chance de vitória + provável OVER 2.5' :
                    '⚠️ Jogo equilibrado: Risco de empate elevado, evite apostar em resultado'
                }
            </div>
            <div class="prediction-item">
                📊 <strong>Baseado em:</strong> 3 jogos analisados, 58.3% de acurácia geral, <strong>100% placar exato</strong>
            </div>
        </div>
    `;
    
    showLoading(false);
}

// Mostrar análise de padrões
async function showAnalysis() {
    showLoading(true);
    document.getElementById('analysisSection').style.display = 'block';
    document.getElementById('analysisSection').scrollIntoView({ behavior: 'smooth' });
    
    // Análise por liga
    const leagueAnalysis = {};
    allMatches.forEach(match => {
        if (!leagueAnalysis[match.league]) {
            leagueAnalysis[match.league] = {
                count: 0,
                avgOddHome: 0,
                avgOddDraw: 0,
                avgOddAway: 0,
                avgUnder: 0
            };
        }
        
        const league = leagueAnalysis[match.league];
        league.count++;
        league.avgOddHome += match.odd_home;
        league.avgOddDraw += match.odd_draw;
        league.avgOddAway += match.odd_away;
        if (match.odd_under_25) league.avgUnder += match.odd_under_25;
    });
    
    // Calcular médias
    Object.values(leagueAnalysis).forEach(league => {
        league.avgOddHome = (league.avgOddHome / league.count).toFixed(2);
        league.avgOddDraw = (league.avgOddDraw / league.count).toFixed(2);
        league.avgOddAway = (league.avgOddAway / league.count).toFixed(2);
        league.avgUnder = (league.avgUnder / league.count).toFixed(2);
    });
    
    const content = document.getElementById('analysisContent');
    content.innerHTML = `
        <h3 style="margin-bottom: 20px;">📊 Análise por Liga</h3>
        ${Object.entries(leagueAnalysis).map(([league, data]) => {
            const probUnder = (1 / parseFloat(data.avgUnder)) * 100;
            const isDefensive = probUnder > 55;
            
            return `
                <div class="prediction-result" style="margin-bottom: 20px;">
                    <h3><span class="league-badge ${league}">${league.toUpperCase()}</span></h3>
                    <div class="prediction-item">
                        <strong>Total de partidas:</strong> ${data.count}
                    </div>
                    <div class="prediction-item">
                        <strong>Odds médias:</strong> Casa ${data.avgOddHome} | Empate ${data.avgOddDraw} | Fora ${data.avgOddAway}
                    </div>
                    <div class="prediction-item">
                        <strong>Característica:</strong> 
                        ${isDefensive ? 
                            '🛡️ Liga DEFENSIVA - Favorece Under 2.5' :
                            '⚡ Liga OFENSIVA - Favorece Over 2.5'
                        }
                        (Under 2.5 médio: ${data.avgUnder})
                    </div>
                </div>
            `;
        }).join('')}
        
        <div class="prediction-result" style="background: #dbeafe; margin-top: 30px;">
            <h3>🎓 Insights Gerais do Sistema</h3>
            <div class="prediction-item">
                <strong>✅ Acurácia Geral:</strong> 58.3% (média de 3 jogos)
            </div>
            <div class="prediction-item">
                <strong>🏆 Placar Exato:</strong> 100% de acerto (3/3 jogos)
            </div>
            <div class="prediction-item">
                <strong>🎯 Resultado:</strong> 66.7% de acerto (2/3 jogos)
            </div>
            <div class="prediction-item">
                <strong>📊 Under/Over:</strong> 33.3% de acerto (1/3 jogos)
            </div>
            <div class="prediction-item">
                <strong>🔑 Descoberta Chave:</strong> Força do favorito (>45% prob) é o fator mais importante para prever gols
            </div>
        </div>
    `;
    
    showLoading(false);
}

// Exportar para CSV
function exportToCSV() {
    if (filteredMatches.length === 0) {
        alert('Nenhuma partida para exportar!');
        return;
    }
    
    const headers = ['Horário', 'Liga', 'Casa', 'Fora', 'Odd Casa', 'Odd Empate', 'Odd Fora', 'Under 2.5', 'Over 2.5'];
    const rows = filteredMatches.map(m => [
        `${m.hour}:${m.minute}`,
        m.league,
        m.team_home,
        m.team_away,
        m.odd_home,
        m.odd_draw,
        m.odd_away,
        m.odd_under_25 || '',
        m.odd_over_25 || ''
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `partidas_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

// Utilitários
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function updateStatus(message, type = 'info') {
    const statusEl = document.getElementById('statusValue');
    statusEl.textContent = message;
    
    if (type === 'success') {
        statusEl.style.color = '#10b981';
    } else if (type === 'error') {
        statusEl.style.color = '#ef4444';
    } else if (type === 'warning') {
        statusEl.style.color = '#f59e0b';
    } else {
        statusEl.style.color = '#6b7280';
    }
}

// ============================================================================
// Fase 2: Controle do Scraper via API
// ============================================================================

async function startScraper() {
    if (!USE_API) {
        alert('Ative o modo API para controlar o scraper');
        return;
    }
    
    showLoading(true);
    updateStatus('Iniciando scraper...');
    
    try {
        const response = await fetch(`${API_URL}/api/scraper/start`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'started') {
            updateStatus(`✅ Scraper iniciado (PID: ${result.pid})`, 'success');
            scraperStatus.is_running = true;
            updateScraperButtons();
        } else if (result.status === 'already_running') {
            updateStatus(`⚠️ ${result.message}`, 'warning');
        }
    } catch (error) {
        console.error('Erro ao iniciar scraper:', error);
        updateStatus(`❌ Erro: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function stopScraper() {
    if (!USE_API) {
        alert('Ative o modo API para controlar o scraper');
        return;
    }
    
    showLoading(true);
    updateStatus('Parando scraper...');
    
    try {
        const response = await fetch(`${API_URL}/api/scraper/stop`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'stopped' || result.status === 'forced_stop') {
            updateStatus(`✅ ${result.message}`, 'success');
            scraperStatus.is_running = false;
            updateScraperButtons();
        } else if (result.status === 'not_running') {
            updateStatus(`⚠️ ${result.message}`, 'warning');
        }
    } catch (error) {
        console.error('Erro ao parar scraper:', error);
        updateStatus(`❌ Erro: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function updateScraperStatus() {
    if (!USE_API) return;
    
    try {
        const response = await fetch(`${API_URL}/api/scraper/status`);
        
        if (!response.ok) return;
        
        const status = await response.json();
        scraperStatus = status;
        updateScraperButtons();
        
        // Se estiver rodando, mostrar PID
        if (status.is_running && status.pid) {
            const statusEl = document.querySelector('.status-value');
            if (statusEl && statusEl.textContent.includes('Sistema operacional')) {
                statusEl.textContent = `🤖 Scraper ativo (PID: ${status.pid})`;
            }
        }
    } catch (error) {
        console.error('Erro ao verificar status do scraper:', error);
    }
}

function updateScraperButtons() {
    const btnStart = document.getElementById('btnStartScraper');
    const btnStop = document.getElementById('btnStopScraper');
    
    if (btnStart && btnStop) {
        if (scraperStatus.is_running) {
            btnStart.disabled = true;
            btnStart.style.opacity = '0.5';
            btnStop.disabled = false;
            btnStop.style.opacity = '1';
        } else {
            btnStart.disabled = false;
            btnStart.style.opacity = '1';
            btnStop.disabled = true;
            btnStop.style.opacity = '0.5';
        }
    }
}

// Exibir predição (suporta resposta da API ou cálculo local)
function displayPrediction(prediction) {
    const content = document.getElementById('predictionContent');
    
    content.innerHTML = `
        <div class="prediction-header">
            <div class="prediction-match">
                ${prediction.match.team_home} vs ${prediction.match.team_away}
            </div>
            <div style="color: #6b7280; margin-top: 10px;">
                🏆 Liga: ${prediction.match.league.toUpperCase()} | ⏰ ${prediction.match.hour}:${prediction.match.minute}
            </div>
        </div>
        
        <h3 style="margin-bottom: 15px;">📊 Odds do Mercado</h3>
        <div class="prediction-odds">
            <div class="odd-card">
                <div class="odd-label">🏠 Casa</div>
                <div class="odd-value-large">${prediction.odds.home.odd.toFixed(2)}</div>
                <div class="odd-label">${prediction.odds.home.probability.toFixed(1)}%</div>
            </div>
            <div class="odd-card">
                <div class="odd-label">🤝 Empate</div>
                <div class="odd-value-large">${prediction.odds.draw.odd.toFixed(2)}</div>
                <div class="odd-label">${prediction.odds.draw.probability.toFixed(1)}%</div>
            </div>
            <div class="odd-card">
                <div class="odd-label">✈️ Fora</div>
                <div class="odd-value-large">${prediction.odds.away.odd.toFixed(2)}</div>
                <div class="odd-label">${prediction.odds.away.probability.toFixed(1)}%</div>
            </div>
        </div>
        
        <h3 style="margin: 20px 0 15px 0;">🔮 Predição do Sistema</h3>
        <div class="prediction-result ${prediction.prediction.is_favorite_strong ? 'favorite-strong' : 'favorite-weak'}">
            <div style="font-size: 24px; font-weight: 700; margin-bottom: 5px;">
                ${prediction.prediction.result}
            </div>
            <div style="font-size: 18px; color: #6b7280;">
                Confiança: ${prediction.prediction.confidence.toFixed(1)}%
            </div>
            <div style="margin-top: 15px; font-size: 14px;">
                ${prediction.prediction.is_favorite_strong ? '✅ Favorito Forte' : '⚠️ Jogo Equilibrado'}
            </div>
        </div>
        
        <div class="prediction-extra">
            <div class="extra-item">
                <strong>⚽ Gols:</strong> ${prediction.prediction.goals} (${prediction.prediction.goals_confidence.toFixed(1)}% confiança)
            </div>
            <div class="extra-item">
                <strong>🎯 Ambas marcam:</strong> ${prediction.prediction.both_score} (${prediction.prediction.both_score_confidence.toFixed(1)}% confiança)
            </div>
        </div>
        
        <h3 style="margin: 20px 0 15px 0;">💡 Recomendações</h3>
        <div class="recommendations">
            ${prediction.recommendations.map(rec => `
                <div class="recommendation-item ${rec.type}">
                    ${rec.text}
                </div>
            `).join('')}
        </div>
    `;
}

// ============================================================================
// FASE 4: Analytics & Recommendations
// ============================================================================

let leagueChart = null;
let oddsChart = null;

function showAnalytics() {
    // Esconde todas as seções
    document.getElementById('predictionsSection').style.display = 'none';
    document.getElementById('logsSection').style.display = 'none';
    document.getElementById('analysisSection').style.display = 'none';
    document.getElementById('recommendationsSection').style.display = 'none';
    
    // Mostra analytics
    document.getElementById('analyticsSection').style.display = 'block';
    
    loadAnalytics();
}

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_URL}/api/analytics/overview`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const analytics = data.data;
            
            // Atualiza KPIs
            document.getElementById('kpiAccuracy').textContent = 
                `${analytics.accuracy.winner}%`;
            document.getElementById('kpiExactScore').textContent = 
                `${analytics.accuracy.exact_score}%`;
            document.getElementById('kpiTotalMatches').textContent = 
                analytics.total_matches;
            document.getElementById('kpiFinished').textContent = 
                analytics.finished_matches;
            
            // Cria gráfico de distribuição por liga
            createLeagueChart(analytics.leagues);
            
            // Cria gráfico de odds médias
            createOddsChart(analytics.avg_odds);
        }

        // Carrega estatísticas de validação
        await loadPredictionStats();
    } catch (error) {
        console.error('Erro ao carregar analytics:', error);
        showToast('Erro ao carregar analytics', 'error');
    }
}

// Nova função para carregar estatísticas de validação de predições
async function loadPredictionStats() {
    try {
        const response = await fetch(`${API_URL}/api/predictions/stats`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.stats;
            
            // Atualiza badge de status
            const badge = document.getElementById('validationBadge');
            if (data.scheduler_running) {
                badge.textContent = '🟢 Ativo';
                badge.style.background = 'rgba(34, 197, 94, 0.3)';
            } else {
                badge.textContent = '🔴 Inativo';
                badge.style.background = 'rgba(239, 68, 68, 0.3)';
            }
            
            // Atualiza contadores
            document.getElementById('totalPredictions').textContent = stats.total_predictions || 0;
            document.getElementById('correctWinners').textContent = stats.correct_winners || 0;
            document.getElementById('correctScores').textContent = stats.correct_scores || 0;
            document.getElementById('correctOverUnder').textContent = stats.correct_over_under || 0;
            
            // Calcula e atualiza porcentagens
            const total = stats.total_predictions || 1; // Evita divisão por zero
            const accuracyWinner = Math.round((stats.correct_winners / total) * 100) || 0;
            const accuracyOverUnder = Math.round((stats.correct_over_under / total) * 100) || 0;
            
            // Atualiza textos de acurácia
            document.getElementById('accuracyWinner').textContent = `${accuracyWinner}%`;
            document.getElementById('accuracyOverUnder').textContent = `${accuracyOverUnder}%`;
            
            // Atualiza barras de progresso
            document.getElementById('progressWinner').style.width = `${accuracyWinner}%`;
            document.getElementById('progressOverUnder').style.width = `${accuracyOverUnder}%`;
            
            console.log('✅ Estatísticas de validação atualizadas:', stats);
        } else {
            console.warn('⚠️ Erro ao carregar estatísticas:', data.error);
        }
    } catch (error) {
        console.error('❌ Erro ao carregar estatísticas de predições:', error);
    }
}

function createLeagueChart(leagues) {
    const ctx = document.getElementById('leagueChart');
    
    // Destroi gráfico anterior se existir
    if (leagueChart) {
        leagueChart.destroy();
    }
    
    leagueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: leagues.map(l => l.league.toUpperCase()),
            datasets: [{
                label: 'Total',
                data: leagues.map(l => l.total),
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            }, {
                label: 'Finalizadas',
                data: leagues.map(l => l.finished),
                backgroundColor: 'rgba(16, 185, 129, 0.5)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createOddsChart(avgOdds) {
    const ctx = document.getElementById('oddsChart');
    
    // Destroi gráfico anterior se existir
    if (oddsChart) {
        oddsChart.destroy();
    }
    
    oddsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Casa', 'Empate', 'Fora'],
            datasets: [{
                data: [avgOdds.home, avgOdds.draw, avgOdds.away],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(239, 68, 68, 0.7)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });
}

function showRecommendations() {
    // Esconde todas as seções
    document.getElementById('predictionsSection').style.display = 'none';
    document.getElementById('logsSection').style.display = 'none';
    document.getElementById('analysisSection').style.display = 'none';
    document.getElementById('analyticsSection').style.display = 'none';
    
    // Mostra recomendações
    document.getElementById('recommendationsSection').style.display = 'block';
    
    loadRecommendations();
}

async function loadRecommendations() {
    const container = document.getElementById('recommendationsContainer');
    container.innerHTML = '<div class="loading">Carregando recomendações...</div>';
    
    try {
        const response = await fetch(`${API_URL}/api/recommendations?min_confidence=70`);
        const data = await response.json();
        
        if (data.status === 'success' && data.recommendations.length > 0) {
            displayRecommendations(data.recommendations);
        } else {
            container.innerHTML = '<div class="no-data">Nenhuma recomendação disponível no momento</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar recomendações:', error);
        container.innerHTML = '<div class="error">Erro ao carregar recomendações</div>';
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    
    let html = '<div class="recommendations-grid">';
    
    recommendations.forEach(rec => {
        const valueClass = rec.value > 0 ? 'positive' : 'neutral';
        const winnerBadge = rec.predicted_winner === 'home' ? '🏠 Casa' : 
                           rec.predicted_winner === 'away' ? '✈️ Fora' : '🤝 Empate';
        
        html += `
            <div class="recommendation-card">
                <div class="rec-header">
                    <span class="rec-league">${rec.league.toUpperCase()}</span>
                    <span class="rec-confidence ${rec.confidence >= 80 ? 'high' : rec.confidence >= 70 ? 'medium' : 'low'}">
                        ${rec.confidence}% confiança
                    </span>
                </div>
                <div class="rec-match">
                    <div class="rec-teams">
                        ${rec.home_team} vs ${rec.away_team}
                    </div>
                    <div class="rec-date">${formatDateTime(rec.match_date)}</div>
                </div>
                <div class="rec-prediction">
                    <div class="rec-winner">
                        <strong>Predição:</strong> ${winnerBadge}
                    </div>
                    <div class="rec-score">
                        <strong>Placar:</strong> ${rec.predicted_score}
                    </div>
                </div>
                <div class="rec-odds">
                    <div class="rec-odd-value">
                        <strong>Odd:</strong> ${rec.odds.toFixed(2)}
                    </div>
                    <div class="rec-value ${valueClass}">
                        <strong>Value:</strong> ${rec.value > 0 ? '+' : ''}${rec.value.toFixed(1)}%
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

async function exportCSV() {
    try {
        showToast('Gerando arquivo CSV...', 'info');
        
        const response = await fetch(`${API_URL}/api/export/csv?limit=1000`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Cria blob e faz download
            const blob = new Blob([data.content], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', data.filename);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast(`✅ ${data.rows} partidas exportadas!`, 'success');
        }
    } catch (error) {
        console.error('Erro ao exportar CSV:', error);
        showToast('Erro ao exportar CSV', 'error');
    }
}

// Atualizar status do scraper a cada 30 segundos
if (USE_API) {
    setInterval(updateScraperStatus, 30000);
    
    // Atualizar estatísticas de validação a cada 60 segundos
    setInterval(() => {
        if (document.getElementById('analyticsSection').style.display !== 'none') {
            loadPredictionStats();
        }
    }, 60000);
}

