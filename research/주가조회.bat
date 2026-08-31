@echo off
chcp 65001 > nul
cd /d "%~dp0"
"C:\Python314\python.exe" "%~dp0stock_price_lookup.py"
pause
