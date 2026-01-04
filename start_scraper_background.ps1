# Script para iniciar o scraper em background (Windows)
# Uso: .\start_scraper_background.ps1

# Configuracoes
$PythonScript = "main_rapidapi.py"
$Mode = "continuous"
$LogFile = "logs\scraper_background.log"
$PidFile = "logs\scraper_pid.txt"

# Cria diretorio de logs se nao existir
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  SCRAPER RAPIDAPI - Iniciando em Background" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Mata processos existentes do scraper
Write-Host "Verificando processos existentes..." -ForegroundColor Yellow
$ExistingProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*$PythonScript*"
}

if ($ExistingProcesses) {
    Write-Host "Encerrando processos existentes do scraper..." -ForegroundColor Yellow
    $ExistingProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Inicia novo processo em background
Write-Host "Iniciando scraper em background..." -ForegroundColor Green
$Process = Start-Process -FilePath "python" `
    -ArgumentList "$PythonScript $Mode" `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError "logs\scraper_errors.log" `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Scraper iniciado com sucesso!" -ForegroundColor Green
Write-Host "   PID: $($Process.Id)"
Write-Host ""
Write-Host "Para visualizar logs em tempo real:" -ForegroundColor Yellow
Write-Host "   Get-Content $LogFile -Wait -Tail 20"
Write-Host ""
Write-Host "Para parar o scraper:" -ForegroundColor Red
Write-Host "   Stop-Process -Id $($Process.Id)"
Write-Host "   ou execute: .\stop_scraper.ps1"
Write-Host ""

# Salva PID em arquivo para facil acesso
$Process.Id | Out-File -FilePath "logs\scraper_pid.txt"

Write-Host "PID salvo em: logs\scraper_pid.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "O scraper continuara coletando dados a cada 5 minutos..." -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""