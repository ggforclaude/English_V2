"""
작문 자동 평가 스크립트
GitHub Actions에서 매일 실행됨 (04:00 KST)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
import pathlib
import anthropic
import pytz

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

KST = pytz.timezone("Asia/Seoul")


async def evaluate_writing() -> dict:
    """어제의 작문 평가"""

    # 어제 날짜
    today = datetime.now(KST).date()
    yesterday = today - timedelta(days=1)

    writing_file = pathlib.Path("docs/writing/drafts.json")
    evaluations_file = pathlib.Path("docs/writing/evaluations.json")
    metadata_file = pathlib.Path("docs/writing/metadata.json")

    log.info(f"평가 대상: {yesterday}")

    # 어제의 작문 찾기
    yesterday_writing = None

    # 방법 1: 저장된 작문 파일에서 찾기
    if writing_file.exists():
        try:
            with open(writing_file, "r", encoding="utf-8") as f:
                all_writings = json.load(f)

            for writing in all_writings:
                if writing.get("date") == str(yesterday):
                    yesterday_writing = writing
                    break
        except Exception as e:
            log.warning(f"작문 파일 읽기 실패: {e}")

    # 방법 2: 저장된 작문이 없으면 샘플 생성 (테스트용)
    if not yesterday_writing:
        log.info("저장된 작문이 없어 샘플 작문으로 테스트합니다")
        yesterday_writing = _generate_sample_writing(yesterday, metadata_file)

        if not yesterday_writing:
            log.warning(f"{yesterday} 작문이 없고 샘플도 생성 불가")
            return {"date": str(yesterday), "status": "no_writing"}

    log.info(f"평가할 작문 길이: {len(yesterday_writing.get('text', ''))}자")

    # Claude API로 평가
    evaluation = await _evaluate_with_claude(yesterday_writing)

    # 평가 결과 저장
    evaluations_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        if evaluations_file.exists():
            with open(evaluations_file, "r", encoding="utf-8") as f:
                evaluations = json.load(f)
        else:
            evaluations = []
    except Exception as e:
        log.warning(f"기존 평가 파일 읽기 실패: {e}")
        evaluations = []

    evaluation["date"] = str(yesterday)
    evaluations.append(evaluation)

    with open(evaluations_file, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, ensure_ascii=False, indent=2)

    log.info("평가 완료 및 저장됨")
    return evaluation


def _generate_sample_writing(date_obj, metadata_file) -> dict:
    """테스트용 샘플 작문 생성"""

    # 메타데이터에서 단어와 문법 정보 가져오기
    words = []
    grammar_topic = ""

    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            words = metadata.get("words", [])
            grammar_topic = metadata.get("grammar_topic", "")
        except Exception as e:
            log.warning(f"메타데이터 읽기 실패: {e}")

    # 샘플 작문 생성 (학습 내용 포함)
    words_str = ", ".join(words[:5]) if words else "words, learning, practice, study, improve"

    sample_text = f"""Today I learned about {grammar_topic}. I practiced using {words_str} in sentences.
    Learning English is important for my future. I enjoy studying new words and grammar.
    I will keep practicing every day to improve my English skills."""

    return {
        "date": str(date_obj),
        "text": sample_text,
        "words": words,
        "grammar": {"topic": grammar_topic},
        "is_sample": True
    }


async def _evaluate_with_claude(writing_data: dict) -> dict:
    """Claude API를 사용한 작문 평가"""

    client = anthropic.Anthropic()
    text = writing_data.get("text", "")
    words = writing_data.get("words", [])
    grammar = writing_data.get("grammar", {})

    prompt = f"""당신은 영어 선생님입니다. 학생이 작성한 다음 글을 평가해주세요.

오늘 배운 단어: {', '.join(words[:5]) if words else 'N/A'}
오늘 배운 문법: {grammar.get('topic', 'N/A')}

학생의 작문:
"{text}"

다음을 JSON 형식으로 평가해주세요:

{{
    "content_score": 0-100,  // 배운 단어/문법 포함도 (%)
    "accuracy_score": 0-100,  // 영어 정확성 (%)
    "corrections": [
        {{
            "wrong": "틀린 표현",
            "correct": "올바른 표현",
            "explanation": "설명"
        }}
    ],
    "feedback": "전체 피드백 (한글, 2-3문장)"
}}

주의:
- content_score: 배운 단어가 얼마나 포함되었는지 (0-100%)
- accuracy_score: 문법, 스펠링, 표현이 얼마나 정확한지 (0-100%)
- corrections: 최대 5개의 주요 오류만 리스트
- feedback: 긍정적이고 격려하는 톤으로"""

    try:
        message = client.messages.create(
            model="claude-opus-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = next(
            (block.text for block in message.content if hasattr(block, 'text')), ""
        )

        # JSON 추출
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]

        evaluation = json.loads(json_str)
        evaluation["text"] = text  # 원문 저장
        evaluation["evaluated_at"] = datetime.now(KST).isoformat()

        return evaluation

    except Exception as e:
        log.error(f"Claude API 호출 실패: {e}")
        return {
            "content_score": 0,
            "accuracy_score": 0,
            "corrections": [],
            "feedback": f"평가 중 오류 발생: {e}",
            "text": text,
            "evaluated_at": datetime.now(KST).isoformat(),
            "status": "error"
        }


async def main():
    """메인 함수"""
    log.info("작문 평가 시작...")
    result = await evaluate_writing()
    log.info(f"결과: {result.get('status', 'success')}")
    return result


if __name__ == "__main__":
    asyncio.run(main())
