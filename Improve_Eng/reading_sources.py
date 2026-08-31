"""
다독(읽기) 콘텐츠
영어 원문 + 한글 번역 + 어휘 + 이해도 확인 퀴즈
"""
import asyncio
import json
import logging
from datetime import date
from typing import Dict, Any

log = logging.getLogger(__name__)


async def fetch_daily_reading_article() -> Dict[str, Any]:
    """매일의 읽기 콘텐츠 (영어 + 번역)"""

    # 샘플 기사 (실제로는 API나 크롤링으로 가져올 수 있음)
    article = {
        "title": "The Benefits of Learning Multiple Languages",
        "source": "BBC Learning English",
        "source_url": "https://www.bbc.co.uk/learningenglish/",
        "level": "B1",
        "reading_time": "5 minutes",

        "content_en": """The Benefits of Learning Multiple Languages

In our increasingly connected world, speaking multiple languages has become more valuable than ever. Whether for career advancement, personal growth, or cultural understanding, learning new languages opens doors to countless opportunities.

**Career Advantages**

Companies today are looking for employees who can communicate with international clients and partners. Bilingual workers often earn higher salaries and have access to more job opportunities. In fields like tourism, diplomacy, and international business, language skills are essential.

**Cognitive Benefits**

Research shows that learning languages improves brain function. It enhances memory, concentration, and problem-solving abilities. Multilingual people often perform better in tasks requiring attention and multitasking. Learning languages also delays cognitive decline in older age.

**Cultural Understanding**

Language is not just a communication tool; it's a window into culture. When you learn a language, you gain insight into different ways of thinking and living. This helps you become more empathetic and open-minded. It allows you to enjoy literature, films, and music in their original language.

**Personal Growth**

Learning languages builds confidence and self-esteem. It challenges your brain and keeps you mentally active. Many learners report that acquiring a new language is one of their most rewarding achievements.

**Making It Practical**

Start small with languages that interest you. Use apps, take classes, or find language exchange partners. Immerse yourself in the language through films, podcasts, and books. The key is consistency and regular practice.

**Conclusion**

In a globalized world, speaking multiple languages is no longer a luxury—it's a practical skill. Whether you want to advance your career, travel more comfortably, or simply understand the world better, learning languages is an investment in yourself.""",

        "content_ko": None,  # Claude API로 생성할 예정

        "vocabulary": [
            {"word": "multilingual", "meaning": "다국어를 할 수 있는", "example": "She is a multilingual speaker."},
            {"word": "advancement", "meaning": "진전, 승진", "example": "Career advancement requires new skills."},
            {"word": "cognitive", "meaning": "인지의, 인식의", "example": "Cognitive abilities improve with practice."},
            {"word": "concentration", "meaning": "집중력", "example": "Deep concentration helps learning."},
            {"word": "multitasking", "meaning": "다중작업", "example": "Bilingual people are good at multitasking."},
            {"word": "empathetic", "meaning": "공감하는", "example": "An empathetic person understands others' feelings."},
            {"word": "immerse", "meaning": "몰두하다, 빠져들다", "example": "Immerse yourself in English films."},
            {"word": "consistency", "meaning": "일관성, 꾸준함", "example": "Consistency is key to success."},
        ],

        "comprehension_questions": [
            {
                "question": "According to the article, what is one career advantage of being bilingual?",
                "options": [
                    "Bilingual workers always become managers",
                    "Bilingual workers often earn higher salaries",
                    "Bilingual workers work shorter hours",
                    "Bilingual workers don't need training"
                ],
                "correct": 1,
                "explanation": "The article states 'Bilingual workers often earn higher salaries and have access to more job opportunities.'"
            },
            {
                "question": "What cognitive benefit is NOT mentioned in the article?",
                "options": [
                    "Improved memory",
                    "Better concentration",
                    "Increased height",
                    "Better problem-solving"
                ],
                "correct": 2,
                "explanation": "The article mentions memory, concentration, and problem-solving, but NOT height. That would be a physical change, not cognitive."
            },
            {
                "question": "Why is language described as 'a window into culture'?",
                "options": [
                    "Because windows are made of glass",
                    "Because it helps you see windows in other countries",
                    "Because it gives insight into different ways of thinking and living",
                    "Because language can be used to build houses"
                ],
                "correct": 2,
                "explanation": "The article explains: 'Language is not just a communication tool; it's a window into culture... you gain insight into different ways of thinking and living.'"
            },
            {
                "question": "What does the article suggest as the key to learning languages?",
                "options": [
                    "Studying for 8 hours a day",
                    "Only learning one language at a time",
                    "Consistency and regular practice",
                    "Learning only from textbooks"
                ],
                "correct": 2,
                "explanation": "The article states: 'The key is consistency and regular practice.'"
            }
        ],

        "learning_points": [
            "직장에서의 언어 사용 장점",
            "뇌 기능 향상 효과",
            "문화 이해와 공감 능력",
            "개인 성장과 자신감 증진",
            "효과적인 학습 전략"
        ]
    }

    # Claude API로 한글 번역 생성
    if not article["content_ko"]:
        article["content_ko"] = await _translate_to_korean(article["content_en"])

    return article


async def _translate_to_korean(english_text: str) -> str:
    """Claude API를 사용한 한글 번역"""
    import anthropic

    client = anthropic.Anthropic()

    prompt = f"""다음 영어 텍스트를 자연스러운 한국어로 번역해주세요.
    전문 번역처럼 자연스럽고 읽기 편하게 번역해야 합니다.

    영어 텍스트:
    {english_text}"""

    try:
        message = client.messages.create(
            model="claude-opus-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = next(
            (block.text for block in message.content if hasattr(block, 'text')), ""
        )
        return response_text
    except Exception as e:
        log.error(f"Translation failed: {e}")
        return "[번역 실패]"


def get_today_reading_sync() -> Dict[str, Any]:
    """동기 버전 (테스트용)"""
    return {
        "title": "The Benefits of Learning Multiple Languages",
        "source": "BBC Learning English",
        "level": "B1",
        "reading_time": "5 minutes",
        "content_en": "Learning multiple languages has many benefits...",
        "content_ko": "여러 언어를 배우면 많은 이점이 있습니다...",
        "vocabulary": [],
        "comprehension_questions": [],
        "learning_points": []
    }


if __name__ == "__main__":
    # 테스트
    article = get_today_reading_sync()
    print(json.dumps(article, ensure_ascii=False, indent=2)[:500])
