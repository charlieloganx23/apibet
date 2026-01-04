# ========================================
# Script PowerShell para parar scraper em background
# ========================================

Write-Host "⏹️  Parando SCRAPER RAPIDAPI..." -ForegroundColor Yellow
Write-Host ""

# Tenta ler PID do arquivo
$PidFile = "logs\scraper_pid.txt"

if (Test-Path $PidFile) {
    $Pid = Get-Content $PidFile
    
    try {
        $Process = Get-Process -Id $Pid -ErrorAction Stop
        Stop-Process -Id $Pid -Force
        Write-Host "✅ Processo $Pid encerrado com sucesso!" -ForegroundColor Green
        Remove-Item $PidFile
    }
    catch {
        Write-Host "⚠️  Processo $Pid não encontrado (já encerrado?)" -ForegroundColor Yellow
        Remove-Item $PidFile -ErrorAction SilentlyContinue
    }
}
else {
    Write-Host "⚠️  Arquivo PID não encontrado. Buscando processos manualmente..." -ForegroundColor Yellow
    
    $Processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*main_rapidapi.py*"
    }
    
    if ($Processes) {
        $Processes | ForEach-Object {
            Write-Host "   Encerrando PID: $($_.Id)" -ForegroundColor Cyan
            Stop-Process -Id $_.Id -Force
        }
        Write-Host "✅ Processos encerrados!" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Nenhum processo do scraper encontrado." -ForegroundColor Red
    }
}

Write-Host ""
