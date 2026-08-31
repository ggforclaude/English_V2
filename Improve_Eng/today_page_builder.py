"""
/today 고정 URL 페이지 생성
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
) -> pathlib.Path:
    """
    /today 고정 페이지 생성.
    docs/today/index.html 저장 (JavaScript로 현재 날짜와 매칭)
    """
    html = _render_today_page(
        today, day_number, anki_stats, voa_content, grammar_content,
        daily_learning, current_levels, report_available
    )

    base = pathlib.Path(__file__).parent.parent / "docs" / "today"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def _render_today_page(today, day_number, anki_stats, voa_content, grammar_content,
                       daily_learning, current_levels, report_available):
    """
    /today 페이지 HTML 렌더링
    5개 섹션: 단어(Anki), 문법, 듣기(VOA), 출력(에세이), 다독
    """

    today_str = str(today)

    # Anki 데이터 JSON
    anki_json = json.dumps(anki_stats, ensure_ascii=False)
    voa_json = json.dumps(voa_content, ensure_ascii=False)
    grammar_json = json.dumps(grammar_content, ensure_ascii=False)
    learning_json = json.dumps(daily_learning, ensure_ascii=False)

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
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}

        .date-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .date-info span {{
            font-size: 1.1em;
            color: #666;
        }}

        .level-badges {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .level-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .level-a2 {{ background: #d1f2eb; color: #0f766e; }}
        .level-b1 {{ background: #bfdbfe; color: #1e40af; }}
        .level-b2 {{ background: #ddd6fe; color: #5b21b6; }}
        .level-c1 {{ background: #fecaca; color: #7c2d12; }}

        .sections {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .section:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }}

        .section-title {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}

        .section-emoji {{
            font-size: 1.5em;
        }}

        .section-content {{
            font-size: 0.95em;
            line-height: 1.6;
            color: #555;
        }}

        .vocab-item {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 3px solid #667eea;
        }}

        .audio-player {{
            margin: 15px 0;
            background: #f0f4ff;
            padding: 15px;
            border-radius: 8px;
        }}

        audio {{
            width: 100%;
            margin: 10px 0;
        }}

        .link-button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 10px;
            transition: background 0.3s;
            font-weight: bold;
        }}

        .link-button:hover {{
            background: #764ba2;
        }}

        .external-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}

        .external-links a {{
            font-size: 0.85em;
            padding: 6px 12px;
            background: #f0f4ff;
            border: 1px solid #667eea;
            border-radius: 6px;
            text-decoration: none;
            color: #667eea;
            transition: all 0.3s;
        }}

        .external-links a:hover {{
            background: #667eea;
            color: white;
        }}

        .anki-status {{
            background: #fff8dc;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 0.9em;
        }}

        .stats-box {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}

        .stat-item {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            font-size: 0.8em;
            color: #999;
            margin-top: 5px;
        }}

        footer {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .report-link {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px;
            transition: transform 0.3s;
        }}

        .report-link:hover {{
            transform: scale(1.05);
        }}

        .reading-content {{
            background: #fffbeb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            margin-top: 10px;
        }}

        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8em; }}
            .sections {{ grid-template-columns: 1fr; }}
            .date-info {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
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
                        Listening: {current_levels.get('listening', 'B1')}
                    </span>
                    <span class="level-badge level-{current_levels.get('grammar', 'b1').lower()}">
                        Grammar: {current_levels.get('grammar', 'B1')}
                    </span>
                </div>
            </div>
        </header>

        <div class="sections">
            <!-- 1. 단어 (Anki) -->
            <div class="section">
                <div class="section-title">
                    <span class="section-emoji">📝</span>
                    <span>단어 (20분) - Anki SRS</span>
                </div>
                <div class="section-content">
                    <p>간격 반복을 통한 NGSL 2,800 단어 학습</p>
                    <div class="stats-box">
                        <div class="stat-item">
                            <div class="stat-number">{anki_stats['ngsl']['progress_pct']:.0f}%</div>
                            <div class="stat-label">진행률</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{anki_stats['today']['total_due']}</div>
                            <div class="stat-label">오늘 복습</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{anki_stats['today']['new_cards']}</div>
                            <div class="stat-label">신규 카드</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{anki_stats['ngsl']['learned']}</div>
                            <div class="stat-label">습득 완료</div>
                        </div>
                    </div>
                    <div class="anki-status">
                        <strong>💡 {anki_stats['recommendation']}</strong>
                    </div>
                    <p style="margin-top: 15px; font-size: 0.85em; color: #666;">
                        Anki 앱(또는 AnkiDroid/AnkiWeb)에서 오늘의 복습을 진행하세요.
                    </p>
                </div>
            </div>

            <!-- 2. 문법 (20분) -->
            <div class="section">
                <div class="section-title">
                    <span class="section-emoji">✏️</span>
                    <span>문법 (20분)</span>
                </div>
                <div class="section-content">
                    <h4>{grammar_content.get('topic', '문법 학습')}</h4>
                    <p style="margin: 10px 0;">{grammar_content.get('korean', 'Grammar explanation')[:200]}</p>
                    <div class="vocab-item">
                        <strong>예시:</strong><br/>
                        {grammar_content.get('example', '')}
                    </div>
                    <div class="external-links">
                        <a href="https://www.bbc.co.uk/learningenglish/english/features/learningenglish-grammar" target="_blank">
                            BBC Grammar →
                        </a>
                        <a href="https://www.perfect-english-grammar.com/" target="_blank">
                            Perfect English Grammar →
                        </a>
                    </div>
                </div>
            </div>

            <!-- 3. 듣기 (20분) - VOA -->
            <div class="section">
                <div class="section-title">
                    <span class="section-emoji">🎧</span>
                    <span>듣기 (20분) - VOA Learning English</span>
                </div>
                <div class="section-content">
                    <h4>{voa_content.get('title', 'Daily English')}</h4>
                    <p style="color: #0f766e; font-size: 0.9em; margin: 8px 0;">
                        <strong>📊 {voa_content.get('level', 'Level 1')}</strong>
                    </p>
                    <p style="margin: 10px 0; color: #555;">{voa_content.get('text', '')[:250]}...</p>

                    {_render_audio_player(voa_content) if voa_content.get('audio_url') else ''}

                    <div class="anki-status" style="background: #fff8dc;">
                        💡 <strong>학습 팁:</strong> 먼저 자막 없이 1회 듣고,
                        그 다음 자막을 켜고 1회 더 들으세요.
                    </div>

                    <div class="external-links">
                        <a href="{voa_content.get('link', 'https://www.voaspecialenglish.com')}" target="_blank">
                            원본 기사 →
                        </a>
                        <a href="https://www.voaspecialenglish.com" target="_blank">
                            VOA 웹사이트 →
                        </a>
                    </div>
                </div>
            </div>

            <!-- 4. 출력 (25분) - 에세이 + 교정 -->
            <div class="section">
                <div class="section-title">
                    <span class="section-emoji">💬</span>
                    <span>출력 (25분) - 미니 에세이</span>
                </div>
                <div class="section-content">
                    <p>오늘 배운 단어 3개와 표현을 포함하여 3-5문장 에세이를 써보세요.</p>

                    <div class="vocab-item">
                        <strong>오늘의 주제:</strong><br/>
                        {daily_learning.get('topic', '일상 이야기')}
                    </div>

                    <div class="vocab-item">
                        <strong>필수 포함 표현:</strong>
                        <ul style="margin-top: 8px; margin-left: 20px;">
                            {_render_expressions(daily_learning.get('key_expressions', []))}
                        </ul>
                    </div>

                    <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                        작성 후 Claude 또는 Grammarly로 교정받으세요.
                    </p>

                    <div class="external-links">
                        <a href="https://claude.ai" target="_blank">Claude 교정 →</a>
                        <a href="https://app.grammarly.com/" target="_blank">Grammarly →</a>
                    </div>
                </div>
            </div>

            <!-- 5. 다독 (5분) - 권장 도서 -->
            <div class="section">
                <div class="section-title">
                    <span class="section-emoji">📖</span>
                    <span>다독 (5분)</span>
                </div>
                <div class="section-content">
                    <p>현재 수준에 맞는 원서를 읽어보세요.</p>

                    <div class="reading-content">
                        <strong>단계별 권장:</strong><br/>
                        <ul style="margin-top: 8px; margin-left: 20px; font-size: 0.9em;">
                            <li><strong>초급 (A2):</strong> Oxford Bookworms Starter-Stage 1 (250-400 단어)</li>
                            <li><strong>중하급 (B1):</strong> Oxford Bookworms Stage 2-3 (600-900 단어)</li>
                            <li><strong>중상급 (B2):</strong> Oxford Bookworms Stage 4-5 (1200-1800 단어)</li>
                            <li><strong>고급 (C1):</strong> 실제 원서 및 기사</li>
                        </ul>
                    </div>

                    <p style="margin-top: 15px; font-size: 0.85em; color: #666;">
                        모르는 단어가 한 페이지에 2-3개 이하인 책을 선택하세요.
                    </p>

                    <div class="external-links">
                        <a href="https://www.oup.com/elt/bookworms" target="_blank">
                            Oxford Bookworms →
                        </a>
                    </div>
                </div>
            </section>
        </div>

        <footer>
            <p>근거 기반 영어 학습 커리큘럼 v2.0</p>
            {_render_report_link(report_available)}
            <p style="font-size: 0.9em; color: #999; margin-top: 15px;">
                매일 이 페이지를 방문하면 그날의 학습 콘텐츠가 자동으로 업데이트됩니다.
            </p>
        </footer>
    </div>

    <script>
        // 현재 날짜를 확인하고 콘텐츠 업데이트 (필요시)
        const today = '{today_str}';
        const currentDate = new Date().toISOString().split('T')[0];

        if (today !== currentDate) {{
            console.log('Date mismatch. Page may need refresh.');
        }}
    </script>
</body>
</html>
"""


def _render_audio_player(voa_content: dict) -> str:
    """오디오 플레이어 HTML"""
    if not voa_content.get('audio_url'):
        return ''

    return f"""
    <div class="audio-player">
        <strong>🎵 오디오 듣기:</strong><br/>
        <audio controls style="width: 100%;">
            <source src="{voa_content['audio_url']}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    </div>
    """


def _render_expressions(expressions: list) -> str:
    """필수 표현 렌더링"""
    if not expressions:
        return '<li>오늘의 주요 표현들</li>'

    return ''.join([f'<li><strong>{expr}</strong></li>' for expr in expressions[:5]])


def _render_report_link(report_available: bool) -> str:
    """리포트 링크"""
    if report_available:
        return '<a href="/report" class="report-link">📊 학습 리포트 보기 →</a>'
    return ''
