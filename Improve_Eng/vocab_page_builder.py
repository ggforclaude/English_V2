"""
문장 기반 어휘(구문/표현) 페이지 생성
/today/vocab 페이지를 빌드합니다. (유사 표현 비교)
"""
import pathlib
import json
from datetime import date


def build_vocab_page(
    today: date,
    vocabulary: dict,
    reading_article: dict,
) -> str:
    """문장 기반 어휘(구문/표현) 페이지 생성."""
    page_path = _save_vocab_html(
        today=today,
        vocabulary=vocabulary,
        reading_article=reading_article,
    )
    return page_path


def _save_vocab_html(
    today: date,
    vocabulary: dict,
    reading_article: dict,
) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "vocab"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    expressions = vocabulary.get("expressions", [])
    vocab_json = json.dumps(expressions, ensure_ascii=False, indent=2)
    article_title = reading_article.get("title", "Today's Article")
    article_source = reading_article.get("source", "")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 표현 - Improve English</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

        .source {{
            font-size: 0.95em;
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            margin-top: 10px;
        }}

        .content {{
            padding: 30px;
        }}

        .article-info {{
            background: #f8f9fa;
            border-left: 4px solid #f5576c;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}

        .article-info h3 {{
            color: #f5576c;
            margin-bottom: 5px;
        }}

        .article-info p {{
            color: #666;
            font-size: 0.95em;
        }}

        .expressions-list {{
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}

        .expression-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            transition: all 0.3s ease;
        }}

        .expression-card:hover {{
            border-color: #f5576c;
            box-shadow: 0 5px 20px rgba(245, 87, 108, 0.1);
        }}

        .main-expression {{
            display: flex;
            align-items: baseline;
            margin-bottom: 20px;
        }}

        .expression-text {{
            font-size: 1.8em;
            font-weight: bold;
            color: #f5576c;
            margin-right: 15px;
        }}

        .expression-meaning {{
            color: #666;
            font-size: 0.95em;
        }}

        .expression-description {{
            background: #fdf8f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 3px solid #f5576c;
        }}

        .description-title {{
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 8px;
        }}

        .description-text {{
            color: #666;
            font-size: 0.95em;
            line-height: 1.6;
        }}

        .expression-example {{
            background: white;
            border: 1px solid #e9ecef;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}

        .example-label {{
            font-weight: bold;
            color: #f5576c;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}

        .example-en {{
            color: #333;
            font-style: italic;
            margin-bottom: 5px;
        }}

        .example-ko {{
            color: #999;
            font-size: 0.9em;
        }}

        .similar-expressions {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
        }}

        .similar-title {{
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 15px;
            font-size: 1.05em;
        }}

        .similar-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
        }}

        .similar-box {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #f5576c;
        }}

        .similar-expression {{
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 8px;
            font-size: 1.05em;
        }}

        .similar-meaning {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}

        .difference {{
            background: white;
            padding: 8px;
            border-radius: 3px;
            font-size: 0.85em;
            color: #555;
            line-height: 1.5;
        }}

        .difference-label {{
            font-weight: bold;
            color: #f5576c;
            font-size: 0.8em;
            margin-bottom: 3px;
        }}

        .empty-message {{
            text-align: center;
            padding: 40px;
            color: #999;
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
            background: #f5576c;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #d63447;
        }}

        @media (max-width: 768px) {{
            .similar-grid {{
                grid-template-columns: 1fr;
            }}

            .expression-text {{
                font-size: 1.3em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 오늘의 표현</h1>
            <p>유사하지만 다른 표현들을 비교하며 배우세요</p>
            <div class="source">📚 {article_source}</div>
        </div>

        <div class="content">
            <div class="article-info">
                <h3>오늘의 읽기 자료</h3>
                <p>{article_title}</p>
            </div>

            <div class="expressions-list" id="expressionsList">
                <!-- 표현이 여기에 동적으로 생성됩니다 -->
            </div>

            <div class="navigation">
                <a href="/today/words" class="nav-button">← 단어로</a>
                <a href="/today/grammar" class="nav-button">문법 →</a>
            </div>
        </div>
    </div>

    <script>
        const expressionsData = {vocab_json};
        const expressionsList = document.getElementById('expressionsList');

        if (expressionsData.length === 0) {{
            expressionsList.innerHTML = '<div class="empty-message">오늘의 표현이 준비되지 않았습니다. 잠시 후 다시 시도해주세요.</div>';
        }} else {{
            expressionsData.forEach((expr, index) => {{
                const card = document.createElement('div');
                card.className = 'expression-card';

                let html = `
                    <div class="main-expression">
                        <div class="expression-text">"${{expr.main}}"</div>
                    </div>

                    <div class="expression-description">
                        <div class="description-title">뜻</div>
                        <div class="description-text">${{expr.meaning_ko}}</div>
                        <div class="description-text" style="margin-top: 5px; font-size: 0.9em; color: #999;">(${{expr.meaning_en}})</div>
                    </div>

                    <div class="expression-example">
                        <div class="example-label">예시</div>
                        <div class="example-en">"${{expr.example_en}}"</div>
                        <div class="example-ko">${{expr.example_ko}}</div>
                    </div>
                `;

                // 유사 표현
                if (expr.similar && expr.similar.length > 0) {{
                    html += `
                        <div class="similar-expressions">
                            <div class="similar-title">📌 유사 표현과의 차이</div>
                            <div class="similar-grid">
                    `;

                    expr.similar.forEach(sim => {{
                        html += `
                            <div class="similar-box">
                                <div class="similar-expression">"${{sim.expression}}"</div>
                                <div class="similar-meaning">${{sim.meaning_ko}}</div>
                                <div class="difference">
                                    <div class="difference-label">차이점:</div>
                                    ${{sim.difference}}
                                </div>
                                <div class="example-en" style="margin-top: 8px; font-size: 0.85em;">"${{sim.example_en}}"</div>
                            </div>
                        `;
                    }});

                    html += `
                            </div>
                        </div>
                    `;
                }}

                card.innerHTML = html;
                expressionsList.appendChild(card);
            }});
        }}
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
