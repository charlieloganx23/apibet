@echo off
chcp 65001 > nul
title ApiBet - Sistema de Predições

echo.
echo ========================================================================
echo    🎯 ApiBet - Iniciando Sistema...
echo ========================================================================
echo.

REM Verifica se Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.12+
    pause
    exit /b 1
)

REM Inicia o sistema unificado
python start.py

pause
