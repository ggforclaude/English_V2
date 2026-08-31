"""
Claude API를 사용해서 문법 커리큘럼 내용 채우기
각 주제별로 설명, 예시, 퀴즈를 생성합니다.
"""

import asyncio
import json
from datetime import datetime
import anthropic

client = anthropic.Anthropic()


async def fill_grammar_entry(entry: dict) -> dict:
    """Claude API로 문법 주제 내용 생성"""
    topic_name = entry["topic"]
    level = entry["level"]

    prompt = f"""당신은 영어 문법 전문가입니다. 다음 문법 주제에 대해 학습 자료를 만들어주세요.

주제: {topic_name}
난이도: {level}

다음 JSON 형식으로 반환해주세요:
{{
    "explanation_ko": "한국어 설명 (2-3문장)",
    "explanation_en": "English explanation (2-3 sentences)",
    "examples": [
        {{"sentence_en": "Example sentence in English", "sentence_ko": "한국어 번역"}},
        {{"sentence_en": "Example sentence in English", "sentence_ko": "한국어 번역"}},
        {{"sentence_en": "Example sentence in English", "sentence_ko": "한국어 번역"}}
    ],
    "quiz": [
        {{
            "question": "한국어 문제",
            "options": ["선택지 A", "선택지 B", "선택지 C", "선택지 D"],
            "correct": 0,
            "explanation": "답 설명"
        }},
        {{
            "question": "한국어 문제",
            "options": ["선택지 A", "선택지 B", "선택지 C", "선택지 D"],
            "correct": 1,
            "explanation": "답 설명"
        }},
        {{
            "question": "한국어 문제",
            "options": ["선택지 A", "선택지 B", "선택지 C", "선택지 D"],
            "correct": 2,
            "explanation": "답 설명"
        }}
    ]
}}

주의:
- 예시는 실제 사용 가능한 문장들
- 퀴즈는 객관식 4개 선택지 (정답 인덱스는 0-3)
- 설명은 간결하고 명확하게"""

    try:
        message = client.messages.create(
            model="claude-opus-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = next(
            (block.text for block in message.content if hasattr(block, 'text')), ""
        )
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]

        data = json.loads(json_str)
        entry["explanation_ko"] = data.get("explanation_ko", entry["explanation_ko"])
        entry["explanation_en"] = data.get("explanation_en", "")
        entry["examples"] = data.get("examples", entry["examples"])
        entry["quiz"] = data.get("quiz", entry["quiz"])

        return entry
    except Exception as e:
        print(f"❌ {entry['id']} 생성 실패: {e}")
        return entry


async def main():
    """메인 실행"""
    from generate_grammar_curriculum import GRAMMAR_TOPICS, generate_entry

    curriculum = []
    for idx, (topic_id, topic_name, level, part) in enumerate(GRAMMAR_TOPICS):
        print(f"[{idx+1}/{len(GRAMMAR_TOPICS)}] {topic_name} 생성 중...")

        entry = generate_entry(topic_id, topic_name, level, part)
        filled_entry = await fill_grammar_entry(entry)
        curriculum.append(filled_entry)

        # API 레이트 제한 방지
        if idx % 5 == 4:
            await asyncio.sleep(2)

    # 결과 저장
    output_path = "Improve_Eng/grammar_curriculum_full.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(curriculum, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료! {len(curriculum)}개 주제 저장됨: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
