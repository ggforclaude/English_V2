@echo off
chcp 65001 > nul
echo.
echo ============================================
echo  Stock Analysis  (incremental update)
echo  Output: {StockName}_analysis_date.xlsx
echo ============================================
echo.
python "%~dp0analyze_stock.py" %*
if %ERRORLEVEL% neq 0 pause
