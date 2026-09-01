"""
/today 고정 URL 페이지 생성 (리디자인: 컴팩트 대시보드)
매일 방문할 때마다 그날의 학습 콘텐츠를 동적으로 표시
"""
import json
import pathlib
from datetime import date
from typing import Optional

def build_today_page(
    today: date,
    day_number: int,
    anki_stats: dict,
    voa_content: dict,
    grammar_content: dict,
    daily_learning: dict,
    current_levels: dict,
    report_available: bool = False,
    grammar_topic: dict = None,
    daily_vocabulary: dict = None,
    reading_article: dict = None,
) -> pathlib.Path:
    """
    /today 컴팩트 대시보드 페이지 생성
    """
    grammar_topic = grammar_topic or {}
    daily_vocabulary = daily_vocabulary or {}
    reading_article = reading_article or {}

    html = _render_today_page(
        today, day_number, anki_stats, voa_content, grammar_content,
        daily_learning, current_levels, report_available,
        grammar_topic, daily_vocabulary, reading_article
    )

    base = pathlib.Path(__file__).parent.parent / "docs" / "today"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def _render_today_page(today, day_number, anki_stats, voa_content, grammar_content,
                       daily_learning, current_levels, report_available,
                       grammar_topic=None, daily_vocabulary=None, reading_article=None):
    """
    컴팩트 대시보드 렌더링
    """
    grammar_topic = grammar_topic or {}
    daily_vocabulary = daily_vocabulary or {}
    reading_article = reading_article or {}

    today_str = str(today)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 영어 학습 - {today_str}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            border-radius: 12px;
            padding: 25px 30px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.2em;
        }}

        .date-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1em;
            color: #666;
        }}

        .level-badges {{
            display: flex;
            gap: 10px;
        }}

        .level-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }}

        .level-b1 {{ background: #bfdbfe; color: #1e40af; }}

        .sections {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}

        .section-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: all 0.3s;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 180px;
        }}

        .section-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .section-emoji {{
            font-size: 2em;
        }}

        .section-title {{
            font-size: 1.1em;
            font-weight: bold;
            color: #667eea;
        }}

        .section-content {{
            font-size: 0.9em;
            color: #555;
            margin-bottom: 12px;
            line-height: 1.5;
            flex-grow: 1;
        }}

        .section-tag {{
            display: inline-block;
            background: #f0f4ff;
            color: #667eea;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75em;
            font-weight: bold;
            margin-top: 8px;
        }}

        .action-button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9em;
            margin-top: 10px;
            transition: background 0.3s;
            align-self: flex-start;
        }}

        .action-button:hover {{
            background: #764ba2;
        }}

        footer {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }}

        .extra-links {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }}

        .extra-links a {{
            padding: 10px 20px;
            background: #f0f4ff;
            color: #667eea;
            border: 1px solid #667eea;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s;
        }}

        .extra-links a:hover {{
            background: #667eea;
            color: white;
        }}

        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8em; }}
            .date-info {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
            .sections {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 오늘의 영어 학습</h1>
            <div class="date-info">
                <span>📅 {today_str} (Day {day_number})</span>
                <div class="level-badges">
                    <span class="level-badge level-{current_levels.get('listening', 'b1').lower()}">
                        Level: {current_levels.get('listening', 'B1')}
                    </span>
                </div>
            </div>
        </header>

        <div class="sections">
            <!-- 1. 단어 -->
            <a href="/today/words" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">📝</span>
                        <div class="section-title">단어</div>
                    </div>
                    <div class="section-content">
                        <strong>10개 단어 학습</strong><br/>
                        진행률: {anki_stats['ngsl']['progress_pct']:.0f}%<br/>
                        <span class="section-tag">퀴즈 학습</span>
                    </div>
                </div>
                <div class="action-button">시작하기→</div>
            </a>

            <!-- 2. 어휘 -->
            <a href="/today/vocab" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">✨</span>
                        <div class="section-title">어휘</div>
                    </div>
                    <div class="section-content">
                        <strong>유사 표현 비교</strong><br/>
                        {_get_vocab_preview(daily_vocabulary)}<br/>
                        <span class="section-tag">구문 학습</span>
                    </div>
                </div>
                <div class="action-button">학습하기→</div>
            </a>

            <!-- 3. 문법 -->
            <a href="/today/grammar" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">✏️</span>
                        <div class="section-title">문법</div>
                    </div>
                    <div class="section-content">
                        <strong>{grammar_topic.get('topic', '문법 학습')}</strong><br/>
                        {grammar_topic.get('explanation_ko', '')[:60]}...<br/>
                        <span class="section-tag">3-4개 퀴즈</span>
                    </div>
                </div>
                <div class="action-button">학습하기→</div>
            </a>

            <!-- 4. 듣기 -->
            <a href="/today/listening" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">🎧</span>
                        <div class="section-title">듣기</div>
                    </div>
                    <div class="section-content">
                        <strong>{voa_content.get('title', 'VOA Learning')[:40]}</strong><br/>
                        음원 + 스크립트<br/>
                        <span class="section-tag">20분</span>
                    </div>
                </div>
                <div class="action-button">재생하기→</div>
            </a>

            <!-- 5. 읽기 -->
            <a href="/today/reading" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">📖</span>
                        <div class="section-title">읽기</div>
                    </div>
                    <div class="section-content">
                        <strong>{reading_article.get('title', '오늘의 기사')[:40]}</strong><br/>
                        영어/한글 탭<br/>
                        <span class="section-tag">5분</span>
                    </div>
                </div>
                <div class="action-button">읽기→</div>
            </a>

            <!-- 6. 작문 -->
            <a href="/today/writing" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">✍️</span>
                        <div class="section-title">작문</div>
                    </div>
                    <div class="section-content">
                        <strong>미니 에세이 작성</strong><br/>
                        오늘 배운 내용 포함<br/>
                        <span class="section-tag">자동 평가</span>
                    </div>
                </div>
                <div class="action-button">작성하기→</div>
            </a>

            <!-- 7. 발음 -->
            <a href="/today/pronunciation" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">🎤</span>
                        <div class="section-title">발음</div>
                    </div>
                    <div class="section-content">
                        <strong>음성 인식 연습</strong><br/>
                        Web Speech API<br/>
                        <span class="section-tag">10개 단어</span>
                    </div>
                </div>
                <div class="action-button">연습하기→</div>
            </a>

            <!-- 8. 통계 -->
            <a href="/today/stats" class="section-card">
                <div>
                    <div class="section-header">
                        <span class="section-emoji">📊</span>
                        <div class="section-title">통계</div>
                    </div>
                    <div class="section-content">
                        <strong>학습 분석</strong><br/>
                        일간/주간/월간<br/>
                        <span class="section-tag">진행 추적</span>
                    </div>
                </div>
                <div class="action-button">보기→</div>
            </a>
        </div>

        <footer>
            <p style="font-weight: bold; margin-bottom: 10px;">근거 기반 영어 학습 커리큘럼 v2.0</p>
            <p style="font-size: 0.9em; color: #999; margin-bottom: 15px;">
                각 섹션을 클릭하여 오늘의 학습을 시작하세요. 매일 새로운 콘텐츠가 생성됩니다.
            </p>
            <div class="extra-links">
                <a href="/today/writing-feedback">📝 어제 작문 피드백</a>
                <a href="/today/correction">✅ 오답 분석</a>
            </div>
        </footer>
    </div>
</body>
</html>
"""


def _get_vocab_preview(daily_vocabulary: dict) -> str:
    """어휘 미리보기"""
    if not daily_vocabulary or not daily_vocabulary.get('words'):
        return "새로운 표현 학습"

    words = daily_vocabulary.get('words', [])[:3]
    vocab_list = ', '.join([w.get('word', '') for w in words])
    return f"{vocab_list}..."
