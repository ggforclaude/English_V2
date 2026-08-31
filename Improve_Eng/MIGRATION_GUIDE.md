# Improve_Eng v1 → v2 마이그레이션 가이드

## 개요
기존의 이메일/텔레그램 기반 시스템에서 웹 페이지 기반 시스템으로 전환합니다.

**주요 변화:**
- 텔레그램 발송 → `/today` 웹페이지
- 이메일 → 자동 업데이트
- 3-티어 듣기 → VOA 단일 클립 (더 효율적)
- 기존 레벨 추적 → Anki + Claude 기반 분석

## 단계별 마이그레이션

### 1단계: 새 시트 생성 (Google Sheets)

기존 Google Sheets 문서에 새 시트 추가:

#### Learning_v2 시트
```
A: date
B: day_number  
C: vocab_due
D: vocab_new
E: grammar_topic
F: listening_title
G: listening_level
H: output_topic
I: reading_recommend
J: questions_correct
K: questions_total
L: accuracy_pct
M: level_listening
N: level_grammar
O: notes
```

#### VOA_Cache 시트
```
A: date
B: level
C: title
D: audio_url
E: text_summary
F: link
```

#### Weak_Points 시트
```
A: analysis_date
B: domain
C: weakness
D: error_rate
E: error_count
F: supplemental_generated
```

### 2단계: 환경 변수 확인

GitHub Secrets에 다음이 설정되어 있는지 확인:

```
✓ GOOGLE_SHEET_ID
✓ GOOGLE_CREDENTIALS_PATH (또는 GOOGLE_CREDENTIALS_JSON)
✓ ANTHROPIC_API_KEY
✓ PAGES_BASE_URL
```

### 3단계: 새 스크립트 배포

#### GitHub Actions 워크플로우 파일 생성
`.github/workflows/daily-english-v2.yml`:

```yaml
name: Daily English Learning v2
on:
  schedule:
    - cron: '0 19 * * *'  # 매일 04:00 KST

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd Improve_Eng
          pip install -r requirements.txt
          python main_v2.py
        env:
          GOOGLE_SHEET_ID: ${{ secrets.GOOGLE_SHEET_ID }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          PAGES_BASE_URL: ${{ secrets.PAGES_BASE_URL }}
          GOOGLE_CREDENTIALS_PATH: ${{ secrets.GOOGLE_CREDENTIALS_PATH }}
```

#### 기존 워크플로우 비활성화
`.github/workflows/daily-english.yml` → 삭제 또는 비활성화

### 4단계: 로컬 테스트

```bash
cd Improve_Eng

# 환경 변수 설정
export GOOGLE_SHEET_ID="your_sheet_id"
export ANTHROPIC_API_KEY="your_api_key"
export PAGES_BASE_URL="https://username.github.io/repo"

# 실행
python main_v2.py
```

예상 출력:
```
2026-08-28 04:00:00 INFO ============================================================
2026-08-28 04:00:00 INFO Improve_Eng v2 시작: 2026-08-28  Day 123
2026-08-28 04:00:00 INFO ============================================================
2026-08-28 04:00:01 INFO [1] VOA Learning English 콘텐츠 수집...
2026-08-28 04:00:02 INFO   ✓ "US Elections: Understanding the Process"...
2026-08-28 04:00:03 INFO [2] 문법 콘텐츠 수집...
...
2026-08-28 04:00:30 INFO ✓ 완료 - /today 페이지에서 오늘의 학습을 시작하세요!
```

### 5단계: 페이지 확인

#### /today 페이지 확인
```
https://your-username.github.io/your-repo/today/
```

예상 내용:
- 📝 단어 (Anki SRS) - 오늘의 복습 카드
- ✏️ 문법 - BBC/Perfect English Grammar
- 🎧 듣기 - VOA Level 1-3
- 💬 출력 - 미니 에세이 주제
- 📖 다독 - Oxford Bookworms 추천

#### /report 페이지 (주 1회 생성)
```
https://your-username.github.io/your-repo/report/
```

예상 내용:
- 📊 학습 통계 (정확도, 학습일수)
- ⚠️ 약점 분석
- 📚 Claude 기반 보충 자료
- 🎯 다음 집중 영역

## 기능 비교표

| 기능 | v1 | v2 | 변화 |
|------|----|----|------|
| **배송 방식** | 텔레그램 + 이메일 | 웹페이지 `/today` | 항상 접속 가능 |
| **듣기** | 3-티어 (SHORT/MEDIUM/LONG) | VOA 단일 클립 | 더 효율적 |
| **문법** | Claude 생성 | BBC + Perfect English Grammar | 검증된 자료 |
| **단어** | 본문 내 어휘 | Anki 전용 덱 (NGSL) | SRS 기반 효율성 |
| **출력** | 없음 | 매일 미니 에세이 | 능동적 사용 강화 |
| **다독** | 없음 | Oxford Bookworms 추천 | 근거 기반 추가 |
| **약점 분석** | 없음 | Claude AI 기반 | 개인화 보충 자료 |
| **리포트** | 이메일 요약 | `/report` 상세 페이지 | 시각화 + 상세 분석 |

## 주의사항

### 이전 데이터 보존
기존 Questions/Responses/Level_History 시트는 **보존됩니다**.
- Learning_v2는 새로운 데이터만 저장
- 기존 통계는 영향 받지 않음

### Anki 설정
v2를 시작하기 전에 Anki 설정 완료:

1. **NGSL 덱 준비**
   - Anki 앱 또는 AnkiWeb에서 "NGSL 2800 단어" 덱 생성
   - 또는 기존 단어 덱 이름 수정

2. **AnkiConnect 설정** (선택)
   - Anki 데스크톱에서 AnkiConnect 플러그인 설치
   - 로컬 통계 실시간 조회 가능
   - 미설정 시 기본 일정 사용

### 텔레그램/이메일 대체
v2에서는 웹페이지만 사용하므로:
- 모바일: 홈 화면에 `/today` 바로가기 추가
- 북마크 활용
- 매일 정해진 시간에 접속하는 습관 형성

## 트러블슈팅

### 1. VOA 콘텐츠가 로드되지 않음

**증상:**
```
[Improve_Eng] Failed to fetch from any VOA level
```

**해결:**
```bash
# 1. feedparser 버전 확인
pip show feedparser

# 2. 수동 테스트
python -c "import feedparser; feed = feedparser.parse('https://www.voaspecialenglish.com/api/p/v1/rss/ctee-level-1'); print(len(feed.entries))"

# 3. 의존성 재설치
pip install --upgrade feedparser requests
```

### 2. Google Sheets 오류

**증상:**
```
[Sheets] Failed to save learning data: 403 Forbidden
```

**해결:**
- Google Cloud Console에서 Sheets API 활성화 확인
- 서비스 계정 이메일이 Sheets 문서의 공유 대상인지 확인
- GOOGLE_SHEET_ID가 정확한지 확인

```bash
# 시트 ID 확인
# https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
# → SHEET_ID 복사
```

### 3. Anki 연결 실패

**증상:**
```
[Anki] AnkiConnect not available
```

**해결:**
- **데스크톱**: Anki 앱 실행 후 Tools → Add-ons → AnkiConnect 설치
- **모바일**: AnkiDroid 설치 (오프라인 모드로 동작)
- **확인**: http://localhost:8765 접속 시 `AnkiConnect` 표시되어야 함

### 4. Claude API 오류

**증상:**
```
Failed to generate supplemental content: 401 Unauthorized
```

**해결:**
```bash
# API 키 확인
echo $ANTHROPIC_API_KEY

# 키 재설정 (GitHub Secrets)
# Settings → Secrets → ANTHROPIC_API_KEY → Update
```

## 성공 체크리스트

v2 마이그레이션이 완료되었는지 확인하세요:

- [ ] 새 시트 3개 생성 (Learning_v2, VOA_Cache, Weak_Points)
- [ ] 환경 변수 설정 완료
- [ ] GitHub Actions 워크플로우 파일 생성
- [ ] 로컬 테스트 성공
- [ ] `/today` 페이지 접속 가능
- [ ] Google Sheets에 데이터 저장됨
- [ ] 다음 주 월요일에 `/report` 페이지 생성 확인

## 지원

문제가 발생하면:

1. **로그 확인**: GitHub Actions 로그에서 오류 메시지 확인
2. **로컬 테스트**: 환경 변수와 의존성 재확인
3. **API 테스트**:
   ```bash
   # VOA
   python -c "import asyncio; from voa_crawler import fetch_voa_daily_content; print(asyncio.run(fetch_voa_daily_content()))"
   
   # Anki
   python -c "import asyncio; from anki_connector import get_anki_stats; print(asyncio.run(get_anki_stats()))"
   
   # Claude
   python -c "import anthropic; print(anthropic.Anthropic().messages.create(model='claude-opus-4-1-20250805', max_tokens=10, messages=[{'role': 'user', 'content': 'Hi'}]))"
   ```

## 다음 단계

v2 안정화 후:
- 사용자 피드백 수집
- UI/UX 개선
- 추가 언어 지원
- 모바일 앱 개발
