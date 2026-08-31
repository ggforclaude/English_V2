# 투자 대시보드 설정 가이드

이 가이드는 온라인 기반 투자 대시보드를 설정하는 방법을 설명합니다.

## 1️⃣ Google Sheets 설정

### 1-1. Google Sheets 생성
1. [Google Sheets](https://sheets.google.com)에서 새로운 스프레드시트 생성
2. 스프레드시트 이름을 "투자대시보드_2026" 또는 원하는 이름으로 설정
3. URL에서 Sheets ID 복사:
   ```
   https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit#gid=0
   ```

### 1-2. Google Cloud 프로젝트 설정
1. [Google Cloud Console](https://console.cloud.google.com)에서 새 프로젝트 생성
2. "투자대시보드" 또는 유사한 이름으로 설정

### 1-3. Google Sheets API 활성화
1. Cloud Console에서 "API 및 서비스" → "라이브러리" 이동
2. "Google Sheets API" 검색 후 활성화
3. "Google Drive API"도 활성화

### 1-4. 서비스 계정 생성
1. Cloud Console에서 "API 및 서비스" → "사용자 인증정보" 이동
2. "사용자 인증정보 만들기" → "서비스 계정" 선택
3. 서비스 계정 이름 입력 (예: "investment-dashboard")
4. 역할은 "기본" → "편집자" 선택
5. "계속" → "완료"

### 1-5. 서비스 계정 키 다운로드
1. 생성된 서비스 계정 클릭
2. "키" 탭 이동
3. "키 추가" → "새 키 만들기" → "JSON"
4. 다운로드된 파일을 `research/sheets_credentials.json`으로 저장

### 1-6. 서비스 계정에 Sheets 접근 권한 부여
1. Google Sheets를 열고 "공유" 클릭
2. 서비스 계정 이메일 (JSON 파일의 "client_email") 입력
3. "편집자" 권한 부여
4. "공유" 클릭

### 1-7. 웹 대시보드용 공개 설정
1. Google Sheets "공유" → "사람 및 그룹 제한"
2. "변경" → "링크를 알고 있는 모든 사용자"로 설정
3. "뷰어" 권한으로 설정

## 2️⃣ 환경 변수 설정

### 2-1. .env 파일 생성
```bash
cd research/
cp .env.example .env
```

### 2-2. .env 파일 수정
```env
# Google Sheets
GOOGLE_SHEETS_ID=위에서 복사한 SHEETS_ID
GOOGLE_CREDENTIALS_JSON=sheets_credentials.json

# Anthropic API (텔레그램 뉴스 요약용)
ANTHROPIC_API_KEY=your_api_key_here

# 텔레그램 (기존 설정 유지)
TELEGRAM_API_ID=existing_id
TELEGRAM_API_HASH=existing_hash
TELEGRAM_CHANNELS=YeouidoStory2
```

## 3️⃣ Python 의존성 설치

```bash
pip install gspread google-auth-oauthlib google-auth-httplib2 google-auth
pip install aiohttp asyncio
```

## 4️⃣ 시스템 구조

### 데이터 흐름
```
매일 09:05 KST & 19:00 KST 실행
    ↓
[fetch_research.py]       → 리서치 보고서
[gold_price.py]           → 금 시세
[sector_rsi.py]           → 섹터 RSI
[fetch_indicators.py]     → 환율/금리/VIX
[telegram_fetcher.py]     → 텔레그램 뉴스
    ↓
[sheets_manager.py]       → Google Sheets에 데이터 저장
    ↓
[dashboard.html]          → 웹 브라우저에서 시각화
```

### Google Sheets 시트 구조
- `최신일자_리서치`: 오늘+최근 3일 리서치 (매 업데이트시 새로고침)
- `최신일자_금시세`: 오늘 금 시세 (매 업데이트시 새로고침)
- `최신일자_RSI`: 오늘 섹터 RSI (매 업데이트시 새로고침)
- `최신일자_지표`: 오늘 투자 지표 (환율, 금리, VIX 등 - 매 업데이트시 새로고침)
- `누적데이터_리서치`: 전체 리서치 (계속 추가)
- `누적데이터_금시세`: 전체 금 시세 추이 (계속 추가)
- `누적데이터_RSI`: 전체 RSI 추이 (계속 추가)
- `누적데이터_지표`: 전체 투자 지표 추이 (계속 추가)
- `뉴스`: 일자별 뉴스 요약 + 원문 (계속 추가)

## 5️⃣ 스케줄러 설정

### Windows 작업 스케줄러
```batch
# 09:05 AM 작업
schtasks /create /tn "InvestmentDashboard_Morning" /tr "python D:\OneDrive\1. NA\cluade\research\daily_update_sheets.py" /sc daily /st 09:05

# 07:00 PM 작업
schtasks /create /tn "InvestmentDashboard_Evening" /tr "python D:\OneDrive\1. NA\cluade\research\daily_update_sheets.py" /sc daily /st 19:00
```

## 6️⃣ 대시보드 접근

1. `research/dashboard.html` 파일을 브라우저에서 열기
2. 또는 간단한 HTTP 서버로 제공:
   ```bash
   python -m http.server 8000 --directory research
   ```
3. `http://localhost:8000/dashboard.html` 접속

## 7️⃣ 트러블슈팅

### "Google Sheets API 인증 오류"
- `sheets_credentials.json` 파일이 `research/` 폴더에 있는지 확인
- 파일 내용이 유효한 JSON인지 확인
- 서비스 계정 이메일이 Google Sheets에 공유되어 있는지 확인

### "시트를 찾을 수 없습니다" 오류
- Google Sheets에서 정해진 이름의 시트가 존재하는지 확인
- `sheets_manager.py`의 `ensure_sheets_exist()` 함수 실행:
  ```bash
  python -c "from sheets_manager import ensure_sheets_exist; ensure_sheets_exist()"
  ```

### "API 쿼터 초과"
- 업데이트 빈도를 줄이거나, 데이터 배치 크기를 감소시킬 것
- 불필요한 API 호출이 있는지 로그 확인

## 8️⃣ 보안 주의사항

- `sheets_credentials.json`을 공개 저장소에 커밋하지 않을 것
- `.env` 파일도 절대 공개하지 않을 것
- API 키는 환경변수로만 관리할 것
- 정기적으로 서비스 계정 권한을 검토할 것
