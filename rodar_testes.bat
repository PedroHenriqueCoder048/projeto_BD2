@echo off
cd /d "%~dp0"
python -m pytest testes -v
echo.
pause
