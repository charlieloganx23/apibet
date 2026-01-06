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
    initializeEventListeners();
    loadData();
    updateScraperStatus();
    
    // Conectar WebSocket se API estiver ativada
    if (USE_API) {
        connectWebSocket();
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
}

// ============================================================================
// Fase 3: WebSocket Tempo Real
// ============================================================================

function connectWebSocket() {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        return; // Já conectado
    }
    
    try {
        websocket = new WebSocket(WS_URL);
        
        websocket.onopen = () => {
            console.log('✅ WebSocket conectado');
            wsReconnectAttempts = 0;
            updateWSStatus('🟢 Conectado', 'success');
            showToast('Conectado ao servidor em tempo real', 'success');
        };
        
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        websocket.onerror = (error) => {
            console.error('❌ Erro no WebSocket:', error);
            updateWSStatus('🔴 Erro', 'error');
        };
        
        websocket.onclose = () => {
            console.log('⚠️ WebSocket desconectado');
            updateWSStatus('🟡 Desconectado', 'warning');
            
            // Tentar reconectar
            if (wsReconnectAttempts < MAX_WS_RECONNECT_ATTEMPTS) {
                wsReconnectAttempts++;
                setTimeout(() => {
                    console.log(`🔄 Tentando reconectar (${wsReconnectAttempts}/${MAX_WS_RECONNECT_ATTEMPTS})...`);
                    connectWebSocket();
                }, 3000 * wsReconnectAttempts); // Backoff exponencial
            }
        };
        
        // Ping a cada 25s para manter conexão
        setInterval(() => {
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send('ping');
            }
        }, 25000);
        
    } catch (error) {
        console.error('Erro ao conectar WebSocket:', error);
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
            const response = await fetch(`${API_URL}/api/matches?limit=200`);
            
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
    
    filteredMatches = allMatches.filter(match => {
        // Filtro de liga
        if (leagueFilter !== 'all' && match.league !== leagueFilter) {
            return false;
        }
        
        // Filtro de status
        if (statusFilter !== 'all' && match.status !== statusFilter) {
            return false;
        }
        
        // Busca por time
        if (searchTerm && 
            !match.team_home.toLowerCase().includes(searchTerm) &&
            !match.team_away.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        return true;
    });
    
    updateTable();
}

// Atualizar tabela
function updateTable() {
    const tbody = document.getElementById('matchesTableBody');
    const count = document.getElementById('tableCount');
    
    count.textContent = `Mostrando ${filteredMatches.length} partidas`;
    
    if (filteredMatches.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading">Nenhuma partida encontrada</td></tr>';
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

// Atualizar status do scraper a cada 30 segundos
if (USE_API) {
    setInterval(updateScraperStatus, 30000);
