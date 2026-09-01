"""
읽기 페이지 생성
/today/reading 페이지를 빌드합니다.
영어/번역 탭 + 어휘 + 이해도 확인 퀴즈
"""
import pathlib
import json
from datetime import date


def build_reading_page(today: date, reading_article: dict) -> str:
    """읽기 페이지 생성."""
    page_path = _save_reading_html(today=today, reading_article=reading_article)
    return page_path


def _save_reading_html(today: date, reading_article: dict) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "reading"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    # 데이터 추출
    title = reading_article.get("title", "Reading Article")
    source = reading_article.get("source", "")
    source_url = reading_article.get("source_url", "")
    level = reading_article.get("level", "B1")
    reading_time = reading_article.get("reading_time", "")
    content_en = reading_article.get("content_en", "")
    content_ko = reading_article.get("content_ko", "")
    vocabulary = reading_article.get("vocabulary", [])
    questions = reading_article.get("comprehension_questions", [])
    learning_points = reading_article.get("learning_points", [])

    vocab_json = json.dumps(vocabulary, ensure_ascii=False)
    questions_json = json.dumps(questions, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="/English_V2/">
    <title>오늘의 읽기 - Improve English</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}

        .header p {{
            font-size: 1.05em;
            opacity: 0.95;
            margin-bottom: 15px;
        }}

        .meta {{
            display: flex;
            justify-content: center;
            gap: 20px;
            font-size: 0.95em;
            opacity: 0.9;
            margin-bottom: 15px;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .level-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.3);
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }}

        .source-link {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            color: white;
            transition: background 0.3s;
            font-size: 0.9em;
        }}

        .source-link:hover {{
            background: rgba(255,255,255,0.3);
        }}

        .content {{
            padding: 40px;
        }}

        .tabs {{
            display: flex;
            gap: 0;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
        }}

        .tab-button {{
            padding: 15px 30px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 1.05em;
            font-weight: bold;
            color: #999;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            transition: all 0.3s;
        }}

        .tab-button.active {{
            color: #11998e;
            border-bottom-color: #11998e;
        }}

        .tab-button:hover {{
            color: #11998e;
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.3s ease-in;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        .article-text {{
            line-height: 2;
            font-size: 1.05em;
            color: #333;
            margin-bottom: 30px;
        }}

        .article-text h2 {{
            color: #11998e;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #38ef7d;
            padding-bottom: 10px;
        }}

        .article-text p {{
            margin-bottom: 15px;
            text-align: justify;
        }}

        .article-text strong {{
            color: #11998e;
            font-weight: 600;
        }}

        .vocabulary-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 30px;
            margin-top: 40px;
        }}

        .section-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #11998e;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #38ef7d;
        }}

        .vocabulary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}

        .vocab-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }}

        .vocab-card:hover {{
            border-color: #11998e;
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.1);
        }}

        .vocab-word {{
            font-weight: bold;
            color: #11998e;
            font-size: 1.1em;
            margin-bottom: 8px;
        }}

        .vocab-meaning {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 12px;
        }}

        .vocab-example {{
            background: #f0f8f7;
            padding: 10px;
            border-radius: 5px;
            font-style: italic;
            font-size: 0.9em;
            color: #555;
            line-height: 1.5;
        }}

        .learning-points {{
            background: #f0f8f7;
            border-left: 4px solid #38ef7d;
            padding: 20px;
            margin-top: 25px;
            border-radius: 5px;
        }}

        .learning-points-title {{
            font-weight: bold;
            color: #11998e;
            margin-bottom: 15px;
            font-size: 1.05em;
        }}

        .learning-points-list {{
            list-style-position: inside;
            color: #666;
        }}

        .learning-points-list li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}

        .quiz-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 30px;
            margin-top: 40px;
        }}

        .quiz-question {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
        }}

        .question-number {{
            color: #11998e;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 0.95em;
        }}

        .question-text {{
            font-size: 1.05em;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
        }}

        .options {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .option {{
            display: flex;
            align-items: center;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .option:hover {{
            border-color: #11998e;
            background: #f0f8f7;
        }}

        .option input[type="radio"] {{
            margin-right: 15px;
            cursor: pointer;
            width: 20px;
            height: 20px;
        }}

        .option-text {{
            flex-grow: 1;
            font-size: 0.95em;
        }}

        .option.correct {{
            border-color: #28a745;
            background: #e8f5e9;
        }}

        .option.incorrect {{
            border-color: #dc3545;
            background: #ffebee;
        }}

        .explanation-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 0.95em;
            color: #333;
        }}

        .explanation-box strong {{
            color: #856404;
        }}

        .quiz-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 25px;
        }}

        .btn {{
            padding: 12px 25px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            font-size: 0.95em;
        }}

        .btn-submit {{
            background: #11998e;
            color: white;
            flex-grow: 1;
        }}

        .btn-submit:hover {{
            background: #0e7a6e;
        }}

        .btn-reset {{
            background: #6c757d;
            color: white;
        }}

        .btn-reset:hover {{
            background: #5a6268;
        }}

        .score-display {{
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 20px;
            display: none;
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
            background: #11998e;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #0e7a6e;
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

            .tabs {{
                flex-wrap: wrap;
            }}

            .tab-button {{
                flex: 1 1 50%;
                padding: 12px 15px;
                font-size: 0.95em;
            }}

            .vocabulary-grid {{
                grid-template-columns: 1fr;
            }}

            .meta {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 오늘의 읽기</h1>
            <p>{title}</p>
            <div class="meta">
                <div class="meta-item">
                    <span class="level-badge">난이도: {level}</span>
                </div>
                <div class="meta-item">
                    ⏱️ {reading_time}
                </div>
            </div>
            <a href="{source_url}" target="_blank" class="source-link">
                📌 원본 사이트: {source}
            </a>
        </div>

        <div class="content">
            <!-- 탭 -->
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab(event, 'english')">
                    🇬🇧 English
                </button>
                <button class="tab-button" onclick="switchTab(event, 'korean')">
                    🇰🇷 한글 번역
                </button>
            </div>

            <!-- 영어 탭 -->
            <div id="english" class="tab-content active">
                <div class="article-text">
                    {content_en}
                </div>
            </div>

            <!-- 한글 탭 -->
            <div id="korean" class="tab-content">
                <div class="article-text">
                    {content_ko}
                </div>
            </div>

            <!-- 어휘 섹션 -->
            <div class="vocabulary-section">
                <div class="section-title">📚 주요 표현</div>
                <div class="vocabulary-grid" id="vocabularyGrid"></div>
            </div>

            <!-- 학습 포인트 -->
            {'<div class="learning-points">' if learning_points else ''}
            {'<div class="learning-points-title">✨ 학습 포인트</div>' if learning_points else ''}
            {'<ul class="learning-points-list" id="learningPointsList"></ul>' if learning_points else ''}
            {'</div>' if learning_points else ''}

            <!-- 이해도 확인 퀴즈 -->
            {'<div class="quiz-section">' if questions else ''}
            {'<div class="section-title">❓ 이해도 확인</div>' if questions else ''}
            {'<div class="score-display" id="scoreDisplay"></div>' if questions else ''}
            {'<form id="quizForm">' if questions else ''}
            """

    if questions:
        for idx, q in enumerate(questions, 1):
            question_text = q.get("question", "")
            options = q.get("options", [])
            html += f'''
                <div class="quiz-question" data-question="{idx-1}">
                    <div class="question-number">문제 {idx}</div>
                    <div class="question-text">{question_text}</div>
                    <div class="options">
            '''

            for opt_idx, option in enumerate(options):
                html += f'''
                        <label class="option">
                            <input type="radio" name="q{idx-1}" value="{opt_idx}">
                            <span class="option-text">{option}</span>
                        </label>
                '''

            html += """
                    </div>
                </div>
            """

        html += """
            </form>
            <div class="quiz-buttons">
                <button class="btn btn-submit" id="submitBtn">제출</button>
                <button class="btn btn-reset" id="resetBtn">다시 풀기</button>
            </div>
            </div>
        """

    html += f"""
        </div>

        <div class="navigation">
            <a href="/today/listening" class="nav-button">← 듣기로</a>
            <a href="/today" class="nav-button">홈 →</a>
        </div>
    </div>

    <script>
        const vocabularyData = {vocab_json};
        const questionsData = {questions_json};
        const learningPointsData = {json.dumps(learning_points, ensure_ascii=False)};

        // 탭 전환
        function switchTab(event, tabName) {{
            event.preventDefault();

            // 모든 탭 비활성화
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));

            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(button => button.classList.remove('active'));

            // 선택된 탭 활성화
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        // 어휘 렌더링
        function renderVocabulary(data) {{
            const grid = document.getElementById('vocabularyGrid');
            if (!grid) return;

            data.forEach(vocab => {{
                const card = document.createElement('div');
                card.className = 'vocab-card';
                card.innerHTML = `
                    <div class="vocab-word">${{vocab.word}}</div>
                    <div class="vocab-meaning">${{vocab.meaning}}</div>
                    <div class="vocab-example">"${{vocab.example}}"</div>
                `;
                grid.appendChild(card);
            }});
        }}

        // 학습 포인트 렌더링
        function renderLearningPoints(data) {{
            const list = document.getElementById('learningPointsList');
            if (!list) return;

            data.forEach(point => {{
                const li = document.createElement('li');
                li.textContent = point;
                list.appendChild(li);
            }});
        }}

        // 퀴즈 제출
        document.getElementById('submitBtn')?.addEventListener('click', () => {{
            const form = document.getElementById('quizForm');
            if (!form) return;

            let correct = 0;
            let answered = 0;

            questionsData.forEach((question, qIdx) => {{
                const selected = document.querySelector(`input[name="q${{qIdx}}"]:checked`);
                if (selected) {{
                    answered++;
                    const selectedIdx = parseInt(selected.value);
                    const isCorrect = selectedIdx === question.correct;
                    const questionDiv = document.querySelector(`[data-question="${{qIdx}}"]`);

                    if (isCorrect) {{
                        correct++;
                        questionDiv.classList.add('correct');
                    }} else {{
                        questionDiv.classList.add('incorrect');
                    }}

                    // 정답 표시
                    const options = questionDiv.querySelectorAll('.option');
                    options[question.correct].classList.add('correct');

                    // 설명 표시
                    let explanation = document.createElement('div');
                    explanation.className = 'explanation-box';
                    explanation.innerHTML = `<strong>설명:</strong> ${{question.explanation}}`;
                    questionDiv.appendChild(explanation);

                    // 모든 옵션 비활성화
                    options.forEach(opt => opt.style.pointerEvents = 'none');
                }}
            }});

            if (answered === questionsData.length) {{
                const percentage = Math.round((correct / questionsData.length) * 100);
                const scoreDisplay = document.getElementById('scoreDisplay');
                scoreDisplay.innerHTML = `정답: ${{correct}}/${{questionsData.length}} (${{percentage}}%)`;
                scoreDisplay.style.display = 'block';
                document.getElementById('submitBtn').disabled = true;
            }}
        }});

        // 다시 풀기
        document.getElementById('resetBtn')?.addEventListener('click', () => {{
            location.reload();
        }});

        // 초기화
        renderVocabulary(vocabularyData);
        renderLearningPoints(learningPointsData);
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
