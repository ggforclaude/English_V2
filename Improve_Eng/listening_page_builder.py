"""
듣기 페이지 생성
/today/listening 페이지를 빌드합니다.
초급(1분) + 뉴스(3~5분) 두 섹션, 음원 플레이어 + 스크립트 토글
"""
import pathlib
import json
from datetime import date


def build_listening_page(today: date, listening_content: dict) -> str:
    """듣기 페이지 생성."""
    page_path = _save_listening_html(today=today, listening_content=listening_content)
    return page_path


def _save_listening_html(today: date, listening_content: dict) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "listening"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    beginner = listening_content.get("beginner", {})
    news = listening_content.get("news", {})

    beginner_json = json.dumps(beginner.get("vocabulary", []), ensure_ascii=False)
    news_json = json.dumps(news.get("vocabulary", []), ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="/English_V2/">
    <title>오늘의 듣기 - Improve English</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}

        .content {{
            padding: 40px;
        }}

        .listening-section {{
            margin-bottom: 50px;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #fa709a;
        }}

        .section-icon {{
            font-size: 2.5em;
            margin-right: 20px;
        }}

        .section-info h2 {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 5px;
        }}

        .section-info p {{
            color: #666;
            font-size: 0.95em;
        }}

        .difficulty-badge {{
            display: inline-block;
            background: #fa709a;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-left: 10px;
            font-weight: bold;
        }}

        .difficulty-badge.beginner {{
            background: #4CAF50;
        }}

        .difficulty-badge.intermediate {{
            background: #2196F3;
        }}

        .player-container {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
        }}

        .player-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            font-size: 1.05em;
        }}

        audio {{
            width: 100%;
            margin-bottom: 15px;
            height: 40px;
        }}

        .player-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #666;
            font-size: 0.9em;
            padding: 10px 0;
            border-top: 1px solid #e9ecef;
            padding-top: 15px;
        }}

        .source-link {{
            display: inline-block;
            background: #fa709a;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9em;
            transition: background 0.3s;
        }}

        .source-link:hover {{
            background: #f55b7a;
        }}

        .script-toggle {{
            background: #fff;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}

        .script-header {{
            padding: 15px 20px;
            background: #f8f9fa;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            color: #333;
            transition: background 0.3s;
        }}

        .script-header:hover {{
            background: #e9ecef;
        }}

        .script-toggle-icon {{
            font-size: 1.3em;
            transition: transform 0.3s;
        }}

        .script-toggle.open .script-toggle-icon {{
            transform: rotate(180deg);
        }}

        .script-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            padding: 0 20px;
        }}

        .script-toggle.open .script-content {{
            max-height: 500px;
            transition: max-height 0.3s ease-in;
        }}

        .script-text {{
            padding: 20px 0;
            line-height: 1.8;
        }}

        .script-ko {{
            color: #333;
            margin-bottom: 25px;
            font-size: 1em;
        }}

        .script-en {{
            color: #666;
            font-size: 0.95em;
            font-style: italic;
            border-top: 2px solid #f0f0f0;
            padding-top: 20px;
        }}

        .vocabulary-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}

        .vocabulary-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }}

        .vocabulary-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }}

        .vocab-item {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 12px;
            font-size: 0.9em;
        }}

        .vocab-word {{
            font-weight: bold;
            color: #fa709a;
            margin-bottom: 5px;
        }}

        .vocab-meaning {{
            color: #666;
        }}

        .learning-points {{
            background: #f8f9fa;
            border-left: 4px solid #fa709a;
            padding: 20px;
            margin-top: 20px;
            border-radius: 5px;
        }}

        .learning-points-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
        }}

        .learning-points-list {{
            list-style-position: inside;
            color: #666;
            font-size: 0.95em;
        }}

        .learning-points-list li {{
            margin-bottom: 8px;
        }}

        .navigation {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}

        .nav-button {{
            display: inline-block;
            padding: 12px 30px;
            margin: 0 10px;
            background: #fa709a;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #f55b7a;
        }}

        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}

            .header {{
                padding: 25px 15px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .section-header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .section-icon {{
                margin-right: 0;
                margin-bottom: 10px;
            }}

            .vocabulary-list {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎧 오늘의 듣기</h1>
            <p>음원 듣고 스크립트로 확인하세요</p>
        </div>

        <div class="content">
            <!-- 초급 섹션 -->
            <div class="listening-section">
                <div class="section-header">
                    <div class="section-icon">🟢</div>
                    <div class="section-info">
                        <div>
                            <h2>{beginner.get('title', 'Beginner Listening')}</h2>
                            <p>{beginner.get('topic', '')}</p>
                            <span class="difficulty-badge beginner">{beginner.get('difficulty', 'Beginner')}</span>
                        </div>
                    </div>
                </div>

                <div class="player-container">
                    <div class="player-title">🎥 비디오</div>
                    {'<iframe width="100%" height="315" src="https://www.youtube.com/embed/' + beginner.get('youtube_id', '') + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>' if beginner.get('youtube_id') else '<p>비디오를 불러올 수 없습니다.</p>'}
                    <div class="player-info">
                        <span>⏱️ {beginner.get('duration', 'N/A')}</span>
                        <a href="{beginner.get('source_url', '#')}" target="_blank" class="source-link">
                            📌 {beginner.get('source', 'Source')}
                        </a>
                    </div>
                </div>

                <!-- 스크립트 토글 -->
                <div class="script-toggle" onclick="toggleScript(this)">
                    <div class="script-header">
                        <span>📝 스크립트 보기</span>
                        <span class="script-toggle-icon">▼</span>
                    </div>
                    <div class="script-content">
                        <div class="script-text">
                            <div class="script-ko">{beginner.get('script_ko', '')}</div>
                            <div class="script-en">{beginner.get('script_en', '')}</div>
                        </div>
                    </div>
                </div>

                <!-- 어휘 -->
                {'<div class="vocabulary-section">' if beginner.get('vocabulary') else ''}
                <div class="vocabulary-title">📚 주요 표현</div>
                <div class="vocabulary-list" id="beginnerVocab"></div>
                {'</div>' if beginner.get('vocabulary') else ''}

                <!-- 학습 포인트 -->
                {'<div class="learning-points">' if beginner.get('learning_points') else ''}
                <div class="learning-points-title">✨ 학습 포인트</div>
                <ul class="learning-points-list" id="beginnerPoints"></ul>
                {'</div>' if beginner.get('learning_points') else ''}
            </div>

            <hr style="border: none; border-top: 2px solid #e9ecef; margin: 50px 0;">

            <!-- 뉴스 섹션 -->
            <div class="listening-section">
                <div class="section-header">
                    <div class="section-icon">🔵</div>
                    <div class="section-info">
                        <div>
                            <h2>{news.get('title', 'News Listening')}</h2>
                            <p>{news.get('topic', '')}</p>
                            <span class="difficulty-badge intermediate">{news.get('difficulty', 'Intermediate')}</span>
                        </div>
                    </div>
                </div>

                <div class="player-container">
                    <div class="player-title">🎥 비디오</div>
                    {'<iframe width="100%" height="315" src="https://www.youtube.com/embed/' + news.get('youtube_id', '') + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>' if news.get('youtube_id') else '<p>비디오를 불러올 수 없습니다.</p>'}
                    <div class="player-info">
                        <span>⏱️ {news.get('duration', 'N/A')}</span>
                        <a href="{news.get('source_url', '#')}" target="_blank" class="source-link">
                            📌 {news.get('source', 'Source')}
                        </a>
                    </div>
                </div>

                <!-- 스크립트 토글 -->
                <div class="script-toggle" onclick="toggleScript(this)">
                    <div class="script-header">
                        <span>📝 스크립트 보기</span>
                        <span class="script-toggle-icon">▼</span>
                    </div>
                    <div class="script-content">
                        <div class="script-text">
                            <div class="script-ko">{news.get('script_ko', '')}</div>
                            <div class="script-en">{news.get('script_en', '')}</div>
                        </div>
                    </div>
                </div>

                <!-- 어휘 -->
                {'<div class="vocabulary-section">' if news.get('vocabulary') else ''}
                <div class="vocabulary-title">📚 주요 표현</div>
                <div class="vocabulary-list" id="newsVocab"></div>
                {'</div>' if news.get('vocabulary') else ''}

                <!-- 학습 포인트 -->
                {'<div class="learning-points">' if news.get('learning_points') else ''}
                <div class="learning-points-title">✨ 학습 포인트</div>
                <ul class="learning-points-list" id="newsPoints"></ul>
                {'</div>' if news.get('learning_points') else ''}
            </div>
        </div>

        <div class="navigation">
            <a href="today/vocab" class="nav-button">← 표현으로</a>
            <a href="today" class="nav-button">홈 →</a>
        </div>
    </div>

    <script>
        const beginnerVocabData = {beginner_json};
        const newsVocabData = {news_json};

        // 스크립트 토글 함수
        function toggleScript(element) {{
            element.classList.toggle('open');
        }}

        // 어휘 렌더링
        function renderVocabulary(data, elementId) {{
            const element = document.getElementById(elementId);
            if (!element) return;

            data.forEach(vocab => {{
                const div = document.createElement('div');
                div.className = 'vocab-item';
                div.innerHTML = `
                    <div class="vocab-word">${{vocab.word}}</div>
                    <div class="vocab-meaning">${{vocab.meaning}}</div>
                `;
                element.appendChild(div);
            }});
        }}

        // 학습 포인트 렌더링
        function renderLearningPoints(data, elementId) {{
            const element = document.getElementById(elementId);
            if (!element) return;

            data.forEach(point => {{
                const li = document.createElement('li');
                li.textContent = point;
                element.appendChild(li);
            }});
        }}

        // 초기화
        renderVocabulary(beginnerVocabData, 'beginnerVocab');
        renderVocabulary(newsVocabData, 'newsVocab');

        const beginnerPoints = {json.dumps(beginner.get('learning_points', []), ensure_ascii=False)};
        const newsPoints = {json.dumps(news.get('learning_points', []), ensure_ascii=False)};

        renderLearningPoints(beginnerPoints, 'beginnerPoints');
        renderLearningPoints(newsPoints, 'newsPoints');
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
