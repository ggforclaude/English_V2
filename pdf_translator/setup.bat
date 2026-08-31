@echo off
echo ====================================
echo  PDF 한국어 번역기 - 환경 설치
echo ====================================
echo.

echo [1] Python 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo 패키지 설치 실패. pip 및 Python 버전을 확인하세요.
    pause
    exit /b 1
)

echo.
echo [2] Tesseract OCR 설치 여부 확인...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo.
    echo [주의] Tesseract OCR이 설치되지 않았습니다.
    echo  이미지 내 텍스트 번역을 위해 아래 주소에서 설치하세요:
    echo  https://github.com/UB-Mannheim/tesseract/wiki
    echo  설치 경로: C:\Program Files\Tesseract-OCR\
    echo.
    echo  설치 후 영어(eng) 언어 데이터가 포함되어 있는지 확인하세요.
) else (
    echo  Tesseract OK
)

echo.
echo [3] ANTHROPIC_API_KEY 환경변수 확인...
if "%ANTHROPIC_API_KEY%"=="" (
    echo [주의] ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.
    echo  시스템 환경변수에 ANTHROPIC_API_KEY=sk-ant-... 를 추가하세요.
) else (
    echo  API KEY OK
)

echo.
echo 설치 완료! 다음 명령으로 실행하세요:
echo   python main.py
echo.
pause
