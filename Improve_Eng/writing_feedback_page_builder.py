"""
작문 평가 피드백 페이지 생성
/today/writing-feedback 페이지를 빌드합니다.
어제 작문의 평가 결과를 표시합니다.
"""
import pathlib
import json
from datetime import date, timedelta, datetime
import pytz


def build_writing_feedback_page(today: date) -> str:
    """작문 평가 피드백 페이지 생성."""
    page_path = _save_feedback_html(today=today)
    return page_path


def _save_feedback_html(today: date) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "writing-feedback"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    # 어제 평가 찾기
    KST = pytz.timezone("Asia/Seoul")
    yesterday = today - timedelta(days=1)

    evaluations_file = pathlib.Path(__file__).parent.parent / "docs" / "writing" / "evaluations.json"

    yesterday_evaluation = None
    if evaluations_file.exists():
        try:
            with open(evaluations_file, "r", encoding="utf-8") as f:
                evaluations = json.load(f)

            for eval_entry in evaluations:
                if eval_entry.get("date") == str(yesterday):
                    yesterday_evaluation = eval_entry
                    break
        except Exception as e:
            pass

    # 평가 데이터 추출
    if yesterday_evaluation:
        content_score = yesterday_evaluation.get("content_score", 0)
        accuracy_score = yesterday_evaluation.get("accuracy_score", 0)
        corrections = yesterday_evaluation.get("corrections", [])
        feedback = yesterday_evaluation.get("feedback", "")
        writing_text = yesterday_evaluation.get("text", "")
        status = "exists"
    else:
        content_score = 0
        accuracy_score = 0
        corrections = []
        feedback = ""
        writing_text = ""
        status = "no_writing"

    corrections_json = json.dumps(corrections, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="/English_V2/">
    <title>작문 평가 - Improve English</title>
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
            padding: 40px 30px;
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

        .date-info {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 10px;
        }}

        .content {{
            padding: 40px;
        }}

        .no-writing {{
            background: #e7f0ff;
            border-left: 4px solid #667eea;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            color: #333;
        }}

        .no-writing h2 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}

        .no-writing p {{
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }}

        .score-section {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}

        .score-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s;
        }}

        .score-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.1);
        }}

        .score-label {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 15px;
            font-weight: 500;
        }}

        .score-value {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
        }}

        .score-bar {{
            width: 100%;
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 10px;
        }}

        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
        }}

        .score-description {{
            font-size: 0.85em;
            color: #999;
        }}

        .writing-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
        }}

        .section-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}

        .writing-text {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            line-height: 1.8;
            color: #333;
            font-size: 1.05em;
        }}

        .corrections-section {{
            margin-bottom: 30px;
        }}

        .correction-item {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 15px;
        }}

        .correction-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 12px;
        }}

        .correction-wrong {{
            background: #ffebee;
            border: 1px solid #dc3545;
            color: #dc3545;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .correction-arrow {{
            color: #999;
            font-size: 1.3em;
        }}

        .correction-right {{
            background: #e8f5e9;
            border: 1px solid #28a745;
            color: #28a745;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .correction-explanation {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            color: #666;
            font-size: 0.9em;
            line-height: 1.6;
        }}

        .feedback-section {{
            background: #e7f0ff;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 6px;
            color: #333;
            line-height: 1.8;
            font-size: 0.95em;
        }}

        .feedback-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 12px;
            font-size: 1.05em;
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

            .score-section {{
                grid-template-columns: 1fr;
            }}

            .score-value {{
                font-size: 2.5em;
            }}

            .correction-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 작문 평가 결과</h1>
            <div class="date-info">어제 작문에 대한 평가입니다</div>
        </div>

        <div class="content">
            """

    if status == "no_writing":
        html += """
            <div class="no-writing">
                <h2>📋 아직 평가할 작문이 없습니다</h2>
                <p>어제 작문이 없거나 아직 평가되지 않았습니다.</p>
                <p>✍️ <a href="/today/writing" style="color: #667eea; font-weight: bold; text-decoration: none;">오늘의 작문</a>을 작성하고 저장해보세요!</p>
            </div>
        """
    else:
        html += f"""
            <!-- 점수 섹션 -->
            <div class="score-section">
                <div class="score-card">
                    <div class="score-label">학습 내용 포함도</div>
                    <div class="score-value">{content_score}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {content_score}%;"></div>
                    </div>
                    <div class="score-description">배운 단어/문법 포함 정도</div>
                </div>

                <div class="score-card">
                    <div class="score-label">영어 정확성</div>
                    <div class="score-value">{accuracy_score}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {accuracy_score}%;"></div>
                    </div>
                    <div class="score-description">문법/표현/스펠링 정확도</div>
                </div>
            </div>

            <!-- 원문 섹션 -->
            <div class="writing-section">
                <div class="section-title">📄 어제 작문</div>
                <div class="writing-text">{writing_text}</div>
            </div>

            <!-- 교정 섹션 -->
            <div class="corrections-section">
                <div class="section-title">🔍 교정 사항</div>
            """

        if corrections:
            for correction in corrections:
                wrong = correction.get("wrong", "")
                correct = correction.get("correct", "")
                explanation = correction.get("explanation", "")

                html += f"""
                <div class="correction-item">
                    <div class="correction-header">
                        <span class="correction-wrong">❌ {wrong}</span>
                        <span class="correction-arrow">→</span>
                        <span class="correction-right">✅ {correct}</span>
                    </div>
                    <div class="correction-explanation">{explanation}</div>
                </div>
                """
        else:
            html += """
                <div style="text-align: center; padding: 20px; color: #28a745; font-weight: bold;">
                    ✨ 완벽합니다! 어떤 오류도 없었습니다. 🎉
                </div>
            """

        html += """
            </div>

            <!-- 피드백 섹션 -->
            <div class="feedback-section">
                <div class="feedback-title">💬 평가자의 피드백</div>
            """
        html += f"{feedback}\n            </div>\n        "

    html += """
        </div>

        <div class="navigation">
            <a href="/today/writing" class="nav-button">← 오늘 작문하기</a>
            <a href="/today" class="nav-button">홈 →</a>
        </div>
    </div>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
