@echo off
chcp 65001 > nul
title ApiBet - Sincronização Automática

echo.
echo ========================================================================
echo    🔄 ApiBet - Sistema de Sincronização Automática
echo ========================================================================
echo.
echo    Este sistema sincroniza automaticamente:
echo    • Novos jogos das ligas
echo    • Resultados de jogos finalizados
echo    • Status de todas as partidas
echo.
echo    ⏰ CORRELAÇÃO DE HORÁRIOS:
echo    • Se no seu PC é 12:22, no site Bet365 são 16:22 (+4h)
echo    • O sistema usa automaticamente o horário do site
echo.
echo ========================================================================
echo.

REM Verifica se Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.12+
    pause
    exit /b 1
)

echo Escolha uma opção:
echo.
echo [1] Executar sincronização UMA VEZ
echo [2] Executar sincronização AUTOMÁTICA (a cada 30 minutos)
echo [3] Executar sincronização AUTOMÁTICA (a cada 15 minutos)
echo [4] Voltar
echo.

set /p opcao="Digite o número da opção: "

if "%opcao%"=="1" (
    echo.
    echo 🔄 Executando sincronização única...
    python auto_sync.py
    echo.
    echo ✅ Sincronização concluída!
    pause
) else if "%opcao%"=="2" (
    echo.
    echo 🤖 Iniciando agendador automático (a cada 30 minutos)...
    echo    Pressione Ctrl+C para interromper
    python auto_scheduler.py --interval 30
) else if "%opcao%"=="3" (
    echo.
    echo 🤖 Iniciando agendador automático (a cada 15 minutos)...
    echo    Pressione Ctrl+C para interromper
    python auto_scheduler.py --interval 15
) else (
    echo Voltando...
    exit /b 0
)

pause
