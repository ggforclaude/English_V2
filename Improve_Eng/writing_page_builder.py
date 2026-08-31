"""
작문 페이지 생성
/today/writing 페이지를 빌드합니다.
"""
import pathlib
import json
from datetime import date


def build_writing_page(
    today: date,
    daily_words: dict,
    grammar_topic: dict,
) -> str:
    """작문 페이지 생성."""
    page_path = _save_writing_html(
        today=today,
        daily_words=daily_words,
        grammar_topic=grammar_topic,
    )
    return page_path


def _save_writing_html(
    today: date,
    daily_words: dict,
    grammar_topic: dict,
) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "writing"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    words_list = daily_words.get("words", [])
    words_json = json.dumps(words_list, ensure_ascii=False, indent=2)
    grammar_json = json.dumps(grammar_topic, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>오늘의 작문 - Improve English</title>
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
            max-width: 1000px;
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

        .content {{
            padding: 30px;
        }}

        .main-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .writing-section {{
            grid-column: 1 / -1;
        }}

        .reference-section {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
        }}

        .section-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}

        .words-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .word-item {{
            background: white;
            padding: 12px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }}

        .word-text {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.05em;
        }}

        .word-meaning {{
            color: #666;
            font-size: 0.9em;
            margin-top: 3px;
        }}

        .grammar-box {{
            background: white;
            border: 2px solid #667eea;
            border-radius: 5px;
            padding: 15px;
        }}

        .grammar-topic {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.05em;
            margin-bottom: 8px;
        }}

        .grammar-explanation {{
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
        }}

        .writing-area {{
            margin-bottom: 20px;
        }}

        .writing-label {{
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            display: block;
        }}

        textarea {{
            width: 100%;
            min-height: 200px;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-family: inherit;
            font-size: 1em;
            resize: vertical;
            transition: border-color 0.3s;
        }}

        textarea:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .char-count {{
            text-align: right;
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .tips {{
            background: #e7f3ff;
            border-left: 4px solid #2196f3;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}

        .tips-title {{
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 8px;
        }}

        .tips-list {{
            list-style: none;
            padding-left: 0;
        }}

        .tips-list li {{
            padding: 5px 0;
            color: #333;
            font-size: 0.95em;
            position: relative;
            padding-left: 20px;
        }}

        .tips-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #2196f3;
            font-weight: bold;
        }}

        .button-group {{
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }}

        .btn {{
            padding: 15px 40px;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .btn-submit {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
        }}

        .btn-submit:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}

        .btn-submit:active {{
            transform: translateY(0);
        }}

        .btn-reset {{
            background: #e9ecef;
            color: #333;
            flex: 1;
        }}

        .btn-reset:hover {{
            background: #dee2e6;
        }}

        .status {{
            display: none;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
            font-weight: bold;
        }}

        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }}

        .status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
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

        @media (max-width: 768px) {{
            .main-grid {{
                grid-template-columns: 1fr;
            }}

            .button-group {{
                flex-direction: column;
            }}

            textarea {{
                min-height: 250px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✍️ 오늘의 작문</h1>
            <p>배운 단어와 문법을 사용해서 작문해보세요</p>
        </div>

        <div class="content">
            <div class="main-grid">
                <div class="reference-section">
                    <div class="section-title">📚 오늘의 단어 참고</div>
                    <div class="words-list" id="wordsReference">
                        <!-- 단어가 동적으로 생성됩니다 -->
                    </div>
                </div>

                <div class="reference-section">
                    <div class="section-title">📖 오늘의 문법 참고</div>
                    <div class="grammar-box" id="grammarReference">
                        <!-- 문법이 동적으로 생성됩니다 -->
                    </div>
                </div>
            </div>

            <div class="writing-section">
                <div class="tips">
                    <div class="tips-title">💡 작문 팁</div>
                    <ul class="tips-list">
                        <li>오늘 배운 단어와 문법을 적어도 3개 이상 사용해보세요</li>
                        <li>3-5 문장 정도의 짧은 문장으로 시작하세요</li>
                        <li>철저한 문법보다는 의사소통이 목표입니다</li>
                        <li>틀리는 것을 두려워하지 마세요. 실수가 학습입니다!</li>
                    </ul>
                </div>

                <div class="writing-area">
                    <label class="writing-label">작문 입력</label>
                    <textarea
                        id="writingInput"
                        placeholder="여기에 작문을 입력하세요. 오늘 배운 단어와 문법을 사용해서 2-5개의 문장을 작성해주세요."
                    ></textarea>
                    <div class="char-count">
                        <span id="charCount">0</span> / 500 자
                    </div>
                </div>

                <div class="button-group">
                    <button class="btn btn-submit" onclick="submitWriting()">📤 제출 & 교정받기</button>
                    <button class="btn btn-reset" onclick="resetWriting()">🔄 초기화</button>
                </div>

                <div class="status" id="status"></div>
            </div>

            <div class="navigation">
                <a href="/today/reading" class="nav-button">← 읽기로</a>
                <a href="/today" class="nav-button">대시보드</a>
            </div>
        </div>
    </div>

    <script>
        const wordsData = {words_json};
        const grammarData = {grammar_json};
        const textInput = document.getElementById('writingInput');
        const charCount = document.getElementById('charCount');
        const statusBox = document.getElementById('status');

        // 단어 참고 렌더링
        const wordsRef = document.getElementById('wordsReference');
        if (wordsData.length > 0) {{
            wordsData.slice(0, 5).forEach(word => {{
                const item = document.createElement('div');
                item.className = 'word-item';
                item.innerHTML = `
                    <div class="word-text">${{word.word}}</div>
                    <div class="word-meaning">${{word.meaning_en}}</div>
                `;
                wordsRef.appendChild(item);
            }});
        }} else {{
            wordsRef.innerHTML = '<p style="color: #999;">단어가 없습니다.</p>';
        }}

        // 문법 참고 렌더링
        const grammarRef = document.getElementById('grammarReference');
        if (grammarData.topic) {{
            grammarRef.innerHTML = `
                <div class="grammar-topic">${{grammarData.topic}}</div>
                <div class="grammar-explanation">${{grammarData.explanation_ko || grammarData.explanation_en}}</div>
            `;
        }}

        // 글자 수 카운팅
        textInput.addEventListener('input', function() {{
            charCount.textContent = this.value.length;
            if (this.value.length > 500) {{
                this.value = this.value.substring(0, 500);
                charCount.textContent = '500';
            }}
        }});

        // 작문 제출
        function submitWriting() {{
            const writing = textInput.value.trim();

            if (!writing) {{
                showStatus('작문을 입력해주세요!', 'error');
                return;
            }}

            if (writing.split('.').length < 2) {{
                showStatus('최소 2개 이상의 문장을 작성해주세요!', 'error');
                return;
            }}

            // localStorage에 저장
            localStorage.setItem('userWriting', writing);
            localStorage.setItem('writingDate', new Date().toISOString());

            showStatus('✅ 작문이 저장되었습니다. 교정 페이지로 이동합니다...', 'success');

            // 1초 후 교정 페이지로 이동
            setTimeout(() => {{
                window.location.href = '/today/correction';
            }}, 1500);
        }}

        // 작문 초기화
        function resetWriting() {{
            if (textInput.value && !confirm('작성하신 내용을 모두 삭제하시겠습니까?')) {{
                return;
            }}
            textInput.value = '';
            charCount.textContent = '0';
            statusBox.textContent = '';
            statusBox.className = 'status';
        }}

        // 상태 메시지 표시
        function showStatus(message, type) {{
            statusBox.textContent = message;
            statusBox.className = `status ${{type}}`;
        }}

        // 페이지 로드 시 저장된 내용이 있으면 복원
        window.addEventListener('load', function() {{
            const saved = localStorage.getItem('userWriting');
            if (saved) {{
                // 사용자가 의도적으로 새로 쓰려고 이 페이지에 온 것이므로 복원하지 않음
                // (correction 페이지에서만 사용)
            }}
        }});
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
