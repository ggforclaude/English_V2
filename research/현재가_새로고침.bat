@echo off
chcp 65001 > nul
echo.
echo ============================================
echo  Price Refresh  (updates latest Excel file)
echo  Usage: drag stock name or double-click
echo ============================================
echo.
python "%~dp0analyze_stock.py" --refresh-price %*
if %ERRORLEVEL% neq 0 pause
