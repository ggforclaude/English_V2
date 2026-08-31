"""
학습 리포트 생성 및 Claude API를 통한 약점 분석
보충 학습 자료 자동 생성
"""
import anthropic
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

log = logging.getLogger(__name__)
_client = anthropic.Anthropic()


async def analyze_weak_points(
    learning_history: list,
    wrong_items: list,
    current_levels: dict,
    days_count: int = 30,
) -> dict:
    """
    지난 days_count일간의 학습 기록을 분석하고 약점 탐지.
    Claude API를 사용하여 약점별 보충 학습 자료 생성.

    Args:
        learning_history: [{"date": "2026-08-28", "domain": "grammar", "correct": true}, ...]
        wrong_items: [{"domain": "listening", "question": "...", "correct": "A", "user_answer": "B"}, ...]
        current_levels: {"grammar": "B1", "listening": "B2", ...}
        days_count: 분석 기간 (기본 30일)

    Returns:
    {
        "weak_areas": [
            {
                "domain": "grammar",
                "weakness": "Present Perfect 시제",
                "error_rate": 0.4,
                "examples": ["문장1", "문장2"],
                "supplemental_content": "Claude가 생성한 설명",
                "practice_items": [{"q": "...", "a": "...", "explanation": "..."}]
            },
            ...
        ],
        "overall_progress": {
            "days_studied": int,
            "total_questions": int,
            "accuracy": float,
            "trend": "improving" | "stable" | "declining"
        },
        "next_focus": "가장 집중해야 할 영역",
        "html_report": "HTML 형식의 전체 리포트"
    }
}
    """

    # 1. 약점 분석
    weak_areas = _analyze_mistakes(wrong_items, current_levels)

    # 2. 전체 진도 계산
    overall_progress = _calculate_progress(learning_history, days_count)

    # 3. Claude API로 보충 자료 생성
    supplemental = await _generate_supplemental_content(weak_areas, current_levels)

    # 4. HTML 리포트 생성
    html_report = _build_report_html(weak_areas, overall_progress, supplemental)

    return {
        "weak_areas": weak_areas,
        "overall_progress": overall_progress,
        "next_focus": supplemental.get("next_focus", ""),
        "supplemental_content": supplemental,
        "html_report": html_report,
        "generated_at": str(datetime.now()),
    }


def _analyze_mistakes(wrong_items: list, current_levels: dict) -> list:
    """
    오답 항목에서 약점 영역 추출.
    같은 영역의 오류 패턴을 그룹화하여 구체적인 약점 탐지.
    """
    from collections import defaultdict

    if not wrong_items:
        return []

    # 영역별로 오류 그룹화
    domain_errors = defaultdict(list)
    for item in wrong_items:
        domain = item.get("domain", "unknown")
        domain_errors[domain].append(item)

    # 각 영역의 약점 분석
    weak_areas = []
    for domain, errors in domain_errors.items():
        error_rate = min(len(errors) / max(1, len(errors)), 1.0)

        # 약점 유형 추론
        weakness = _infer_weakness(domain, errors)

        weak_areas.append({
            "domain": domain,
            "weakness": weakness,
            "error_rate": error_rate,
            "error_count": len(errors),
            "examples": [e.get("question", "")[:100] for e in errors[:3]],
        })

    return sorted(weak_areas, key=lambda x: x["error_rate"], reverse=True)


def _infer_weakness(domain: str, errors: list) -> str:
    """
    오류 패턴으로부터 구체적인 약점 유추.
    예: grammar 오류 → "Present Perfect 이해 부족" 같은 식
    """
    if domain == "listening":
        # 듣기 약점: 빠른 속도, 발음, 어휘
        return "빠른 속도의 자연스러운 발음 이해"

    elif domain == "grammar":
        # 문법 약점: 시제, 조동사 등
        common_errors = {
            "tense": "시제 혼동 (특히 과거/현재 완료형)",
            "passive": "수동태 형성",
            "modal": "조동사 사용",
            "conditional": "가정법 구조",
        }
        # 간단한 휴리스틱 (실제로는 더 정교한 분석 필요)
        return list(common_errors.values())[len(errors) % len(common_errors)]

    elif domain == "reading":
        return "복잡한 문장 구조 이해"

    elif domain == "speaking":
        return "자연스러운 발음과 리듬감"

    return "해당 영역의 기초 다지기"


def _calculate_progress(learning_history: list, days_count: int) -> dict:
    """
    학습 진도 계산.
    """
    if not learning_history:
        return {
            "days_studied": 0,
            "total_questions": 0,
            "accuracy": 0.0,
            "trend": "no_data",
        }

    # 정확도 계산
    correct = sum(1 for item in learning_history if item.get("correct"))
    total = len(learning_history)
    accuracy = correct / total if total > 0 else 0.0

    # 학습일수 계산
    unique_dates = set(item.get("date", "") for item in learning_history)
    days_studied = len(unique_dates)

    # 트렌드 분석 (간단한 버전)
    if total < 10:
        trend = "not_enough_data"
    elif accuracy > 0.8:
        trend = "excellent"
    elif accuracy > 0.7:
        trend = "good"
    elif accuracy > 0.6:
        trend = "improving"
    elif accuracy > 0.5:
        trend = "needs_work"
    else:
        trend = "struggling"

    return {
        "days_studied": days_studied,
        "total_questions": total,
        "accuracy": round(accuracy * 100, 1),
        "correct_answers": correct,
        "trend": trend,
    }


async def _generate_supplemental_content(weak_areas: list, current_levels: dict) -> dict:
    """
    Claude API를 사용하여 약점별 보충 학습 자료 생성.
    """
    if not weak_areas:
        return {
            "items": [],
            "next_focus": "전체적인 기초 다지기",
        }

    # 가장 약한 영역 top 3
    top_weak = weak_areas[:3]
    domains = ", ".join([f"{item['domain']} ({item['weakness']})" for item in top_weak])

    prompt = f"""사용자의 영어 학습 약점을 분석한 결과입니다:

약점 영역: {domains}

현재 수준:
- 문법: {current_levels.get('grammar', 'B1')}
- 듣기: {current_levels.get('listening', 'B1')}
- 읽기: {current_levels.get('reading', 'B1')}

각 약점별로 다음을 제공해주세요:

1. **약점 설명**: 왜 이 부분이 어려운지 이해하기 쉬운 설명
2. **예제**: 틀리기 쉬운 5-10개 예문
3. **해결책**: 이 약점을 극복하기 위한 구체적인 학습 방법
4. **연습 자료**: 바로 적용할 수 있는 연습 문제 3개

형식:
```json
{{
  "weak_areas": [
    {{
      "domain": "domain_name",
      "title": "구체적인 약점",
      "explanation": "이해하기 쉬운 설명",
      "common_mistakes": ["실수1", "실수2", "실수3"],
      "solution": "해결 방법",
      "practice_questions": [
        {{
          "question": "...",
          "correct_answer": "...",
          "explanation": "..."
        }}
      ]
    }}
  ],
  "next_focus": "우선적으로 집중할 영역"
}}
```

JSON으로만 응답하세요."""

    try:
        message = await _client.messages.create(
            model="claude-opus-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        # JSON 파싱 (Claude Opus 5 ThinkingBlock 처리)
        response_text = next((block.text for block in message.content if hasattr(block, 'text')), "")
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            log.warning("Claude response is not valid JSON, returning fallback")
            return _get_fallback_supplemental(top_weak)

    except Exception as e:
        log.error(f"Failed to generate supplemental content: {e}")
        return _get_fallback_supplemental(top_weak)


def _get_fallback_supplemental(weak_areas: list) -> dict:
    """Claude API 실패 시 기본 보충 자료"""
    return {
        "weak_areas": [
            {
                "domain": item["domain"],
                "title": item["weakness"],
                "explanation": "추가 학습이 필요한 영역입니다.",
                "solution": "BBC Learning English 또는 Perfect English Grammar를 참고하세요.",
                "practice_questions": [],
            }
            for item in weak_areas[:3]
        ],
        "next_focus": weak_areas[0]["domain"] if weak_areas else "전체",
    }


def _build_report_html(weak_areas: list, overall_progress: dict, supplemental: dict) -> str:
    """
    HTML 형식의 학습 리포트 생성.
    /report 페이지에서 표시됨.
    """
    weak_areas_html = ""
    for item in weak_areas[:5]:
        weak_areas_html += f"""
        <div class="weak-area-card">
            <h3>{item['domain'].upper()} - {item.get('weakness', '')}</h3>
            <p><strong>오류율:</strong> {item.get('error_rate', 0):.0%}</p>
            <p><strong>오류 수:</strong> {item.get('error_count', 0)}</p>
            <p><strong>예시:</strong></p>
            <ul>
                {"".join([f"<li>{ex}</li>" for ex in item.get('examples', [])])}
            </ul>
        </div>
        """

    supplemental_html = ""
    for item in supplemental.get("weak_areas", [])[:3]:
        practice_html = "".join([
            f"""<div class="q">
                <p><strong>Q:</strong> {q.get('question', '')}</p>
                <p><strong>A:</strong> {q.get('correct_answer', '')}</p>
                <p><em>{q.get('explanation', '')}</em></p>
            </div>"""
            for q in item.get('practice_questions', [])
        ])
        supplemental_html += f"""
        <div class="supplemental-card">
            <h3>{item.get('domain', 'Unknown').upper()}</h3>
            <h4>{item.get('title', '')}</h4>
            <p><strong>설명:</strong> {item.get('explanation', '')}</p>
            <p><strong>해결책:</strong> {item.get('solution', '')}</p>
            <details>
                <summary>연습 문제 보기</summary>
                <div class="practice-questions">
                    {practice_html}
                </div>
            </details>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>영어 학습 리포트</title>
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
            margin-bottom: 20px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
        }}

        .stat-label {{
            font-size: 0.9em;
            margin-top: 10px;
            opacity: 0.9;
        }}

        .report-section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .report-section h2 {{
            color: #667eea;
            border-bottom: 2px solid #eee;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}

        .weak-area-card, .supplemental-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 6px;
        }}

        .weak-area-card h3, .supplemental-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .weak-area-card h4, .supplemental-card h4 {{
            color: #764ba2;
            margin: 10px 0 5px 0;
        }}

        .practice-questions {{
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }}

        .q {{
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}

        .q:last-child {{
            border-bottom: none;
        }}

        .q p {{
            margin: 5px 0;
            line-height: 1.6;
        }}

        details {{
            cursor: pointer;
            margin-top: 10px;
        }}

        details summary {{
            color: #667eea;
            font-weight: bold;
            padding: 10px;
            background: #f0f4ff;
            border-radius: 4px;
        }}

        details summary:hover {{
            background: #e0ebff;
        }}

        .back-link {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: bold;
        }}

        .back-link:hover {{
            background: #764ba2;
        }}

        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/today" class="back-link">← 돌아가기</a>

        <header>
            <h1>📊 영어 학습 리포트</h1>
            <p>생성 시간: {overall_progress.get('_generated_at', '')}</p>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{overall_progress.get('accuracy', 0):.0f}%</div>
                    <div class="stat-label">정확도</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overall_progress.get('days_studied', 0)}</div>
                    <div class="stat-label">학습일수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overall_progress.get('total_questions', 0)}</div>
                    <div class="stat-label">풀이한 문제</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overall_progress.get('trend', 'N/A')}</div>
                    <div class="stat-label">학습 추세</div>
                </div>
            </div>
        </header>

        <div class="report-section">
            <h2>⚠️ 약점 분석</h2>
            {weak_areas_html if weak_areas_html else '<p>약점 데이터가 없습니다.</p>'}
        </div>

        <div class="report-section">
            <h2>📚 보충 학습 자료</h2>
            {supplemental_html if supplemental_html else '<p>보충 자료 생성 중입니다.</p>'}
        </div>

        <div class="report-section">
            <h2>🎯 다음 단계</h2>
            <p><strong>우선 집중 영역:</strong> {supplemental.get('next_focus', 'N/A')}</p>
            <p style="margin-top: 15px; color: #666;">
                위의 보충 학습 자료를 참고하여 약점을 극복해보세요.
                매일의 학습을 통해 지속적으로 개선될 것입니다.
            </p>
        </div>
    </div>
</body>
</html>
"""

    return html
