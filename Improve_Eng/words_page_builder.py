"""
오늘의 10개 단어 페이지 생성
/today/words 페이지를 빌드합니다.
"""
import pathlib
import json
from datetime import date


def build_words_page(
    today: date,
    daily_words: dict,
    current_levels: dict,
) -> str:
    """10개 단어 페이지 생성."""
    page_path = _save_words_html(
        today=today,
        daily_words=daily_words,
        current_levels=current_levels,
    )
    return page_path


def _save_words_html(
    today: date,
    daily_words: dict,
    current_levels: dict,
) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "words"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    words_list = daily_words.get("words", [])
    words_json = json.dumps(words_list, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 10개 단어 - Improve English</title>
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
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .date {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 10px;
        }}

        .content {{
            padding: 30px;
        }}

        .words-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .word-card {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .word-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }}

        .word-card.flipped {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .word-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .word-card.flipped .word-title {{
            color: white;
        }}

        .word-pronunciation {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 10px;
            font-style: italic;
        }}

        .word-card.flipped .word-pronunciation {{
            color: rgba(255,255,255,0.8);
        }}

        .word-pos {{
            display: inline-block;
            background: #e7f3ff;
            color: #0066cc;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-bottom: 10px;
        }}

        .word-card.flipped .word-pos {{
            background: rgba(255,255,255,0.2);
            color: white;
        }}

        .word-definition {{
            font-size: 1em;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.5;
        }}

        .word-card.flipped .word-definition {{
            color: white;
        }}

        .word-example {{
            background: white;
            padding: 10px;
            border-left: 3px solid #667eea;
            font-size: 0.95em;
            color: #666;
            font-style: italic;
            margin-top: 10px;
        }}

        .word-card.flipped .word-example {{
            background: rgba(255,255,255,0.1);
            border-left-color: white;
            color: rgba(255,255,255,0.9);
        }}

        .hint {{
            font-size: 0.8em;
            color: #999;
            text-align: center;
            margin-top: 10px;
        }}

        .word-card.flipped .hint {{
            color: rgba(255,255,255,0.6);
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
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #764ba2;
        }}

        .progress {{
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }}

        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 오늘의 10개 단어</h1>
            <p>클릭해서 정의/예문을 확인하세요</p>
            <div class="date">{today.strftime("%Y년 %m월 %d일")}</div>
        </div>

        <div class="content">
            <div class="progress">
                <p>학습 진행도: <span id="learned">0</span> / {len(words_list)}</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress"></div>
                </div>
            </div>

            <div class="words-grid" id="wordsGrid">
                <!-- 카드가 여기에 동적으로 생성됩니다 -->
            </div>

            <div class="navigation">
                <a href="/today" class="nav-button">← 돌아가기</a>
                <a href="/today/vocab" class="nav-button">어휘 →</a>
            </div>
        </div>
    </div>

    <script>
        const wordsData = {words_json};
        const grid = document.getElementById('wordsGrid');
        const learned = new Set();

        // 카드 생성
        wordsData.forEach((word, index) => {{
            const card = document.createElement('div');
            card.className = 'word-card';
            card.innerHTML = `
                <div class="word-title">${{word.word}}</div>
                <div class="word-pronunciation">${{word.pronunciation || 'N/A'}}</div>
                ${{word.pos ? `<div class="word-pos">${{word.pos}}</div>` : ''}}
                <div class="word-definition">${{word.meaning_en || '(정의 없음)'}}</div>
                ${{word.example_en ? `<div class="word-example">"${{word.example_en}}"</div>` : ''}}
                <div class="hint">클릭해서 다시 보기</div>
            `;

            card.addEventListener('click', function() {{
                this.classList.toggle('flipped');
                if (this.classList.contains('flipped')) {{
                    learned.add(index);
                }} else {{
                    learned.delete(index);
                }}
                updateProgress();
            }});

            grid.appendChild(card);
        }});

        function updateProgress() {{
            document.getElementById('learned').textContent = learned.size;
            const percent = (learned.size / wordsData.length) * 100;
            document.getElementById('progress').style.width = percent + '%';
        }}
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
