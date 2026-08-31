# Improve_Eng v2 - 근거 기반 영어 학습 시스템

## 개요

근거 기반(Evidence-Based) 영어 학습 커리큘럼을 구현한 웹 플랫폼입니다.

**일일 90분 커리큘럼:**
- **20분 - 단어**: Anki + NGSL 2,800 단어 (간격 반복 SRS)
- **20분 - 문법**: BBC Learning English + Perfect English Grammar (명시적 학습)
- **20분 - 듣기**: VOA Learning English Level 1~3 (이해 가능한 입력)
- **25분 - 출력**: 미니 에세이 작성 + Claude/Grammarly 교정 (능동적 사용)
- **5분 - 다독**: Oxford Bookworms 단계별 독서 (보완적 학습)

**웹 페이지:**
- `/today` - 고정 URL에서 매일의 학습 콘텐츠 표시
- `/report` - 약점 분석 및 Claude AI 기반 보충 학습 자료

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 또는 GitHub Actions Secrets
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_CREDENTIALS_PATH=active-cable-494902-q1-e70695e40677.json
ANTHROPIC_API_KEY=your_api_key
PAGES_BASE_URL=https://your-github-pages-url
ANKI_CONNECT_URL=http://localhost:8765  # 선택사항
```

### 3. Google Sheets 초기 설정
새 Google Sheets 문서에 다음 시트를 생성하세요:

| 시트명 | 목적 | 컬럼 |
|--------|------|------|
| **Learning_v2** | 일일 학습 기록 | date, day_number, vocab_due, vocab_new, grammar_topic, listening_title, ... |
| **VOA_Cache** | VOA 콘텐츠 캐시 | date, level, title, audio_url, text_summary, link |
| **Weak_Points** | 약점 분석 결과 | analysis_date, domain, weakness, error_rate, error_count, supplemental_generated |
| **Questions** | 생성된 문제 (기존) | date, domain, num, level, text, ... |
| **Responses** | 사용자 응답 (Google Form) | timestamp, answers_csv, ... |

## 아키텍처

```
main_v2.py
├── voa_crawler.py          → VOA Learning English 콘텐츠 수집
├── anki_connector.py        → Anki 덱 상태 조회 (NGSL 진도)
├── sheets_manager_v2.py     → Google Sheets v2 데이터 관리
├── report_analyzer.py       → 약점 분석 + Claude 보충 자료
├── today_page_builder.py    → /today 페이지 생성
├── level_tracker.py (기존)  → CEFR 레벨 계산
├── question_generator.py    → 퀴즈 문제 생성
└── content_fetcher.py       → 문법/어원/발음 콘텐츠 수집
```

## 주요 모듈

### voa_crawler.py
VOA Learning English RSS에서 매일의 콘텐츠를 수집합니다.

```python
await fetch_voa_daily_content()
# 반환: {"title": "...", "text": "...", "audio_url": "...", "level": "Level 1"}
```

**특징:**
- Level 1 우선순위 (초급)
- 자동 폴백 (Level 2, 3)
- 오디오 URL 자동 추출

### anki_connector.py
Anki 덱의 학습 상태를 조회합니다 (AnkiConnect 또는 AnkiWeb API 사용).

```python
anki_stats = await get_anki_stats()
# {"today": {"total_due": 20, "new_cards": 5}, "ngsl": {"progress_pct": 15}}
```

**오프라인 대응:**
- AnkiConnect 미연결 시 기본 일정 제공
- 진도율은 0%로 초기화

### sheets_manager_v2.py
Google Sheets API를 통해 v2 데이터를 관리합니다.

```python
sheets = await get_sheets_manager()
await sheets.save_daily_learning(today, day_number, anki_stats, ...)
await sheets.save_weak_points(today, weak_areas)
```

### report_analyzer.py
학습 기록을 분석하고 Claude API로 약점별 보충 자료를 생성합니다.

```python
report = await analyze_weak_points(
    learning_history=history,
    wrong_items=wrong_list,
    current_levels=levels
)
# 반환: {"weak_areas": [...], "supplemental_content": "Claude 생성 자료"}
```

**Claude API 사용:**
- 약점별 설명 생성
- 예제 문장 제공
- 연습 문제 3개 작성

### today_page_builder.py
`/today` 고정 URL 페이지를 생성합니다 (매일 자동 갱신).

```python
await build_today_page(
    today, day_number, anki_stats, voa_content, ...
)
# 저장: docs/today/index.html
```

**페이지 구성:**
- 각 영역별 탭 (단어, 문법, 듣기, 출력, 다독)
- 외부 리소스 링크 (BBC, VOA, italki, Claude, Grammarly)
- 실시간 진도 통계

## 실행 방법

### 로컬 테스트
```bash
python main_v2.py
```

### GitHub Actions 자동 실행
`.github/workflows/daily-english-learning.yml` 추가:

```yaml
name: Daily English Learning
on:
  schedule:
    - cron: '0 19 * * *'  # 매일 04:00 KST (UTC 19:00)

jobs:
  learning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r Improve_Eng/requirements.txt
      - run: python Improve_Eng/main_v2.py
        env:
          GOOGLE_SHEET_ID: ${{ secrets.GOOGLE_SHEET_ID }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          PAGES_BASE_URL: ${{ secrets.PAGES_BASE_URL }}
```

## 사용 가이드

### 1. 매일 학습하기
1. `https://your-domain/today` 방문
2. 5개 영역의 콘텐츠 학습:
   - 📝 **단어**: Anki 앱에서 복습
   - ✏️ **문법**: BBC/Perfect English Grammar 읽기
   - 🎧 **듣기**: VOA 오디오 + 자막 (자막 제거/추가로 2회 청취)
   - 💬 **출력**: 미니 에세이 작성 → Claude 교정
   - 📖 **다독**: Oxford Bookworms 또는 권장 도서 읽기

### 2. 주간 리포트 확인
- 매주 월요일에 자동으로 리포트 생성
- `/report` 페이지에서 확인
- **약점 분석**: 오답이 많은 영역 표시
- **보충 자료**: Claude AI가 생성한 설명/연습 문제
- **다음 집중 영역**: AI 추천 학습 주제

### 3. 진도 추적
Google Sheets의 `Learning_v2` 시트에서:
- 일별 복습 카드 수 추적
- 정확도 변화 그래프
- 레벨 상승 타이밍

## 근거 기반 설명

이 커리큘럼의 각 요소는 학습 과학 연구에 기반합니다:

### 간격 반복 (Distributed Practice) - 강함
- 메타분석: 271개 실험 중 259개에서 검증
- Anki의 SRS 알고리즘이 최적의 복습 간격 자동 계산
- 참고: Cepeda et al. (2006), *Psychological Bulletin*

### 명시적 문법 학습 - 강함
- 캐나다 프랑스어 몰입교육 학생들도 입력만으로는 문법 오류 지속
- 20분의 명시적 학습이 필수
- 참고: Swain (1991), Long (1991)

### 이해 가능한 입력 - 중간
- VOA는 느린 속도의 자연스러운 발음 제공
- 자막을 켰다 껐다 하면서 청취 능력 향상
- 참고: Nakanishi (2015), *TESOL Quarterly*

### 능동적 출력 - 강함
- 말하기/쓰기가 듣기/읽기보다 더 넓은 뇌 영역 활성화
- 매일의 에세이 작성이 중요
- 참고: Li & Jeong (2020), *npj Science of Learning*

### 어휘 임계점 - 중간
- 3,000 어족: 효율적 독해 가능
- 5,000 어족: 사전 없이 편하게 읽기 가능
- 참고: Laufer (1997), Cobb (2007)

## 커스터마이징

### 크롤링 우선순위 변경
`voa_crawler.py`에서:
```python
VOA_RSS_URLS = {
    "level1": "...",  # 우선순위 변경
    "level3": "...",
    "level2": "...",
}
```

### Claude 모델 변경
`report_analyzer.py`에서:
```python
model="claude-opus-5",  # 또는 다른 모델
```

### Google Sheets 위치 변경
`sheets_manager_v2.py`에서 시트 이름 수정:
```python
SHEET_LEARNING_V2 = "My Custom Sheet Name"
```

## 문제 해결

### VOA 콘텐츠가 로드되지 않음
```bash
# feedparser 업데이트
pip install --upgrade feedparser
```

### Anki 연결 실패
- AnkiDroid 또는 Anki 데스크톱 앱 실행 필요
- AnkiConnect 플러그인 설치 (데스크톱)
- `ANKI_CONNECT_URL` 환경변수 확인

### Google Sheets 권한 오류
- 서비스 계정 이메일을 Sheets 공유 대상에 추가
- `GOOGLE_CREDENTIALS_PATH` 확인

## 라이선스
MIT License

## 참고 자료
- [근거 기반 영어 학습 커리큘럼](영어학습_커리큘럼_근거기반.md)
- [VOA Learning English](https://www.voaspecialenglish.com)
- [Anki Documentation](https://docs.ankiweb.net/)
- [BBC Learning English](https://www.bbc.co.uk/learningenglish)
