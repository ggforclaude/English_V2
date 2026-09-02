"""
다독(읽기) 콘텐츠
영어 원문 + 한글 번역 + 어휘 + 이해도 확인 퀴즈
day_number에 따라 매일 다른 주제의 기사 제공
"""
import asyncio
import json
import logging
from datetime import date
from typing import Dict, Any
import anthropic

log = logging.getLogger(__name__)

# 다양한 주제의 기사 풀 (10개 주제)
ARTICLE_TOPICS = [
    ("The Benefits of Learning Multiple Languages", "언어 학습의 이점"),
    ("Climate Change and Global Warming", "기후 변화"),
    ("The Future of Artificial Intelligence", "인공지능의 미래"),
    ("Remote Work Revolution", "원격 근무"),
    ("Healthy Lifestyle Tips", "건강한 생활방식"),
    ("Travel Tips for Budget Travelers", "저예산 여행"),
    ("Technology in Education", "교육의 기술"),
    ("Social Media Impact", "소셜 미디어의 영향"),
    ("Environmental Conservation", "환경 보전"),
    ("Work-Life Balance", "일과 삶의 균형"),
]


async def fetch_daily_reading_article(day_number: int = 1) -> Dict[str, Any]:
    """매일의 읽기 콘텐츠 (영어 + 번역). day_number에 따라 다른 주제 제공."""

    # day_number에 따라 주제 선택
    topic_idx = (day_number - 1) % len(ARTICLE_TOPICS)
    title_en, title_ko = ARTICLE_TOPICS[topic_idx]

    client = anthropic.Anthropic()

    prompt = f"""당신은 영어 교육 전문가입니다. 다음 주제에 대한 B1 레벨의 영어 기사를 생성해주세요.

제목: {title_en}

요구사항:
1. 길이: 400-500 단어
2. 단어 난이도: B1 레벨 (초급자도 이해 가능)
3. 자연스러운 영어로 3-4개 단락 구성
4. 명확한 구조: 소개 → 본론 (2-3개 포인트) → 결론

다음 JSON 형식으로만 반환하세요. 설명이나 마크다운 없이 순수 JSON만:

{{
  "title_en": "{title_en}",
  "title_ko": "{title_ko}",
  "content_en": "영어 기사 전문",
  "vocabulary": [
    {{"word": "단어", "meaning_ko": "한글 뜻", "example_en": "예문"}},
    ...최소 5개
  ]
}}"""

    try:
        message = client.messages.create(
            model="claude-opus-5",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = next((block.text for block in message.content if hasattr(block, 'text')), "").strip()

        # JSON 추출
        start = raw.find('{')
        end = raw.rfind('}') + 1

        if start == -1 or end <= 0:
            log.error("No valid JSON in reading article response")
            return _fallback_article(title_en, title_ko)

        json_str = raw[start:end]
        data = json.loads(json_str)

        return {
            "title": data.get("title_en", title_en),
            "title_ko": data.get("title_ko", title_ko),
            "source": "Claude Generated",
            "source_url": "https://improveenglish.com",
            "level": "B1",
            "reading_time": "5 minutes",
            "content_en": data.get("content_en", ""),
            "content_ko": None,
            "vocabulary": data.get("vocabulary", []),
        }

    except json.JSONDecodeError as e:
        log.error(f"Failed to parse reading article JSON: {e}")
        return _fallback_article(title_en, title_ko)
    except Exception as e:
        log.error(f"Failed to generate reading article: {e}")
        return _fallback_article(title_en, title_ko)


def _fallback_article(title_en: str, title_ko: str) -> Dict[str, Any]:
    """폴백 기사"""
    return {
        "title": title_en,
        "title_ko": title_ko,
        "source": "Fallback Content",
        "source_url": "https://improveenglish.com",
        "level": "B1",
        "reading_time": "5 minutes",
        "content_en": f"{title_en}\n\nThis is a placeholder article. Please try again later to get the full article.",
        "content_ko": f"{title_ko}\n\n이것은 임시 기사입니다. 나중에 다시 시도해주세요.",
        "vocabulary": [],
    }


if __name__ == "__main__":
    print(f"Total article topics: {len(ARTICLE_TOPICS)}")
    for day in range(1, 11):
        idx = (day - 1) % len(ARTICLE_TOPICS)
        title_en, title_ko = ARTICLE_TOPICS[idx]
        print(f"Day {day}: {title_en} ({title_ko})")
