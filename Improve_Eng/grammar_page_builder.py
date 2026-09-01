"""
문법 페이지 생성
/today/grammar 페이지를 빌드합니다.
출처, 추가 자료 링크, 객관식 퀴즈 포함
"""
import pathlib
import json
from datetime import date


def build_grammar_page(today: date, grammar_topic: dict) -> str:
    """문법 페이지 생성."""
    page_path = _save_grammar_html(today=today, grammar_topic=grammar_topic)
    return page_path


def _save_grammar_html(today: date, grammar_topic: dict) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "grammar"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    # 데이터 추출
    topic = grammar_topic.get("topic", "Grammar Topic")
    level = grammar_topic.get("level", "B1")
    explanation_ko = grammar_topic.get("explanation_ko", "")
    explanation_en = grammar_topic.get("explanation_en", "")
    examples = grammar_topic.get("examples", [])
    source = grammar_topic.get("source", {"name": "BBC Learning English", "url": "https://www.bbc.co.uk/learningenglish/"})
    resources = grammar_topic.get("additional_resources", [])
    quiz = grammar_topic.get("quiz", [])

    grammar_json = json.dumps(quiz, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="/English_V2/">
    <title>오늘의 문법 - Improve English</title>
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
            max-width: 950px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}

        .header p {{
            font-size: 1.15em;
            opacity: 0.95;
            margin-bottom: 15px;
        }}

        .level-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.3);
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 3px solid #667eea;
        }}

        .explanation {{
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
            line-height: 1.8;
        }}

        .explanation-ko {{
            color: #333;
            font-size: 1.1em;
            margin-bottom: 15px;
            font-weight: 500;
        }}

        .explanation-en {{
            color: #666;
            font-size: 0.95em;
            font-style: italic;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }}

        .examples-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .example-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .example-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);
        }}

        .example-en {{
            color: #333;
            font-weight: 600;
            margin-bottom: 10px;
            font-style: italic;
            font-size: 1em;
        }}

        .example-ko {{
            color: #666;
            font-size: 0.95em;
            line-height: 1.6;
        }}

        .resources-container {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 20px;
        }}

        .resources-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.05em;
        }}

        .resource-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .resource-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .resource-link {{
            display: inline-block;
            padding: 10px 18px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.95em;
            transition: background 0.3s;
            flex-grow: 1;
        }}

        .resource-link:hover {{
            background: #5568d3;
        }}

        .primary-source {{
            background: #667eea;
            color: white;
        }}

        .quiz-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 30px;
        }}

        .quiz-question {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
        }}

        .quiz-question.active {{
            border-color: #667eea;
        }}

        .question-number {{
            color: #667eea;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 0.95em;
        }}

        .question-text {{
            font-size: 1.1em;
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
            border-color: #667eea;
            background: #f8f9fa;
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
            background: #667eea;
            color: white;
            flex-grow: 1;
        }}

        .btn-submit:hover {{
            background: #5568d3;
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
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #5568d3;
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

            .examples-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 오늘의 문법</h1>
            <p>{topic}</p>
            <div class="level-badge">난이도: {level}</div>
        </div>

        <div class="content">
            <!-- 설명 섹션 -->
            <div class="section">
                <div class="section-title">📖 문법 설명</div>
                <div class="explanation">
                    <div class="explanation-ko">{explanation_ko}</div>
                    <div class="explanation-en">{explanation_en}</div>
                </div>
            </div>

            <!-- 예시 섹션 -->
            <div class="section">
                <div class="section-title">💡 예시</div>
                <div class="examples-grid">
            """

    for example in examples:
        en = example.get("sentence_en", "")
        ko = example.get("sentence_ko", "")
        html += f"""
                    <div class="example-card">
                        <div class="example-en">"{en}"</div>
                        <div class="example-ko">{ko}</div>
                    </div>
            """

    html += """
                </div>
            </div>

            <!-- 출처 및 학습 자료 섹션 -->
            <div class="section">
                <div class="section-title">🔗 학습 자료</div>
                <div class="resources-container">
                    <div class="resources-title">📌 주요 출처</div>
                    <div class="resource-list">
            """

    if source:
        source_name = source.get("name", "")
        source_url = source.get("url", "")
        html += f'''
                        <div class="resource-item">
                            <a href="{source_url}" target="_blank" class="resource-link primary-source">
                                🎯 {source_name}
                            </a>
                        </div>
            '''

    html += """
                    </div>
                </div>
            """

    if resources:
        html += """
                <div class="resources-container">
                    <div class="resources-title">📚 추가 학습 자료</div>
                    <div class="resource-list">
            """
        for res in resources:
            res_name = res.get("name", "")
            res_url = res.get("url", "")
            html += f'''
                        <div class="resource-item">
                            <a href="{res_url}" target="_blank" class="resource-link">
                                📖 {res_name}
                            </a>
                        </div>
            '''
        html += """
                    </div>
                </div>
            """

    html += """
            </div>

            <!-- 퀴즈 섹션 -->
            """

    if quiz:
        html += """
            <div class="section">
                <div class="section-title">❓ 학습 확인 퀴즈</div>
                <div class="score-display" id="scoreDisplay"></div>
                <div class="quiz-section">
                    <form id="quizForm">
            """

        for idx, q in enumerate(quiz, 1):
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
            </div>
        """

    html += """
        </div>

        <div class="navigation">
            <a href="today/words" class="nav-button">← 단어로</a>
            <a href="today" class="nav-button">홈 →</a>
        </div>
    </div>

    <script>
        const quizData = """
    html += grammar_json
    html += """;

        document.getElementById('submitBtn').addEventListener('click', () => {
            const form = document.getElementById('quizForm');
            if (!form) return;

            let correct = 0;
            let answered = 0;

            quizData.forEach((question, qIdx) => {
                const selected = document.querySelector(`input[name="q${qIdx}"]:checked`);
                if (selected) {
                    answered++;
                    const selectedIdx = parseInt(selected.value);
                    const isCorrect = selectedIdx === question.correct;
                    const questionDiv = document.querySelector(`[data-question="${qIdx}"]`);

                    if (isCorrect) {
                        correct++;
                        questionDiv.classList.add('correct');
                    } else {
                        questionDiv.classList.add('incorrect');
                    }

                    // 설명 표시
                    const options = questionDiv.querySelectorAll('.option');
                    options[question.correct].classList.add('correct');

                    let explanation = document.createElement('div');
                    explanation.className = 'explanation-box';
                    explanation.innerHTML = `<strong>정답 설명:</strong> ${question.explanation}`;
                    questionDiv.appendChild(explanation);

                    // 모든 옵션 비활성화
                    options.forEach(opt => opt.style.pointerEvents = 'none');
                }
            });

            if (answered === quizData.length) {
                const percentage = Math.round((correct / quizData.length) * 100);
                const scoreDisplay = document.getElementById('scoreDisplay');
                scoreDisplay.innerHTML = `정답: ${correct}/${quizData.length} (${percentage}%)`;
                scoreDisplay.style.display = 'block';
                document.getElementById('submitBtn').disabled = true;
            }
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            location.reload();
        });
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
