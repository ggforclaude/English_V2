"""
문장 기반 어휘 페이지 생성
/today/vocab 페이지를 빌드합니다.
"""
import pathlib
import json
from datetime import date


def build_vocab_page(
    today: date,
    vocabulary: dict,
    reading_article: dict,
) -> str:
    """문장 기반 어휘 페이지 생성."""
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

    vocab_words = vocabulary.get("words", [])
    vocab_json = json.dumps(vocab_words, ensure_ascii=False, indent=2)
    article_title = reading_article.get("title", "Today's Article")
    article_source = reading_article.get("source", "")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 어휘 - Improve English</title>
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
            max-width: 900px;
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

        .vocab-list {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .vocab-item {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .vocab-item:hover {{
            border-color: #f5576c;
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.1);
        }}

        .vocab-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        .vocab-word {{
            font-size: 1.8em;
            font-weight: bold;
            color: #f5576c;
        }}

        .vocab-pronunciation {{
            font-size: 0.95em;
            color: #999;
            font-style: italic;
        }}

        .vocab-meanings {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .meaning-block {{
            background: white;
            padding: 12px;
            border-radius: 5px;
            border-left: 3px solid #f5576c;
        }}

        .meaning-label {{
            font-weight: bold;
            color: #f5576c;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}

        .meaning-text {{
            color: #333;
            font-size: 0.95em;
            line-height: 1.5;
        }}

        .vocab-examples {{
            background: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }}

        .examples-title {{
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 10px;
        }}

        .example {{
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}

        .example:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}

        .example-text {{
            color: #333;
            font-style: italic;
            margin-bottom: 5px;
        }}

        .example-source {{
            font-size: 0.85em;
            color: #999;
            background: #f0f0f0;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
        }}

        .context-sentence {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 0.95em;
            line-height: 1.6;
        }}

        .context-label {{
            font-weight: bold;
            color: #ff6b6b;
            font-size: 0.85em;
            margin-bottom: 5px;
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

        .empty-message {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}

        @media (max-width: 768px) {{
            .vocab-meanings {{
                grid-template-columns: 1fr;
            }}

            .vocab-header {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 오늘의 어휘</h1>
            <p>읽기 자료에서 배우는 새로운 단어</p>
            <div class="source">📚 {article_source}</div>
        </div>

        <div class="content">
            <div class="article-info">
                <h3>오늘의 읽기 자료</h3>
                <p>{article_title}</p>
            </div>

            <div class="vocab-list" id="vocabList">
                <!-- 어휘 아이템이 여기에 동적으로 생성됩니다 -->
            </div>

            <div class="navigation">
                <a href="/today" class="nav-button">← 단어로</a>
                <a href="/today/grammar" class="nav-button">문법 →</a>
            </div>
        </div>
    </div>

    <script>
        const vocabData = {vocab_json};
        const vocabList = document.getElementById('vocabList');

        if (vocabData.length === 0) {{
            vocabList.innerHTML = '<div class="empty-message">오늘의 어휘가 준비되지 않았습니다. 잠시 후 다시 시도해주세요.</div>';
        }} else {{
            vocabData.forEach((vocab, index) => {{
                const item = document.createElement('div');
                item.className = 'vocab-item';
                item.innerHTML = `
                    <div class="vocab-header">
                        <div>
                            <div class="vocab-word">${{vocab.word}}</div>
                            <div class="vocab-pronunciation">${{vocab.pronunciation || 'N/A'}}</div>
                        </div>
                    </div>

                    <div class="vocab-meanings">
                        <div class="meaning-block">
                            <div class="meaning-label">영어 뜻</div>
                            <div class="meaning-text">${{vocab.meaning_en || 'N/A'}}</div>
                        </div>
                        <div class="meaning-block">
                            <div class="meaning-label">한글 뜻</div>
                            <div class="meaning-text">${{vocab.meaning_ko || 'N/A'}}</div>
                        </div>
                    </div>

                    <div class="vocab-examples">
                        <div class="examples-title">📌 예문</div>
                        <div class="example">
                            <div class="example-text">"${{vocab.example || 'N/A'}}"</div>
                        </div>
                    </div>

                    ${{vocab.context_sentence ? `
                        <div class="context-sentence">
                            <div class="context-label">✨ 원문에서의 사용:</div>
                            <div>${{vocab.context_sentence}}</div>
                        </div>
                    ` : ''}}
                `;
                vocabList.appendChild(item);
            }});
        }}
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
