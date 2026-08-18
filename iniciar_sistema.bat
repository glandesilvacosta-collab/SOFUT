@echo off
title Patrimonio da Familia - Sistema de Ativos
cls
echo ======================================================
echo    PATRIMONIO DA FAMILIA - GESTAO DE ATIVOS E ITENS
echo ======================================================
echo.
echo Iniciando o servidor FastAPI e abrindo o navegador...
echo.
cd /d "%~dp0"
python run.py
pause
