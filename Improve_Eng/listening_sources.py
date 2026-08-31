"""
듣기 콘텐츠 소스 (초급 + 뉴스)
매일 업데이트되는 공개 콘텐츠
"""

import asyncio
import json
from datetime import date
from typing import Dict, Any


async def fetch_daily_listening_content() -> Dict[str, Any]:
    """매일의 듣기 콘텐츠 (초급 + 뉴스) 반환"""

    beginner_content = await _fetch_beginner_content()
    news_content = await _fetch_news_content()

    return {
        "beginner": beginner_content,
        "news": news_content
    }


async def _fetch_beginner_content() -> Dict[str, Any]:
    """초급 콘텐츠: 1분 이내 일상 표현"""

    # 실제 구현에서는 API나 크롤링으로 가져오기
    # 현재는 공개 음원 링크와 샘플 스크립트 사용

    return {
        "title": "Daily English Conversation - Meeting a Friend",
        "source": "Learn English with EnglishClub",
        "source_url": "https://www.englishclub.com/",
        "audio_url": "https://www.englishclub.com/listening/easy-listening.html",
        "youtube_id": None,  # YouTube 임베드 필요시 사용
        "duration": "1 minute",
        "difficulty": "Beginner (A1-A2)",
        "topic": "일상 회화",
        "script_ko": """A: 안녕! 오늘 하루 어땠어?
B: 안녕! 좋았어. 너는?
A: 나도 좋았어. 내일 뭐 할 거야?
B: 내일은 친구들을 만날 거야. 너도 올래?
A: 좋아! 몇 시에 만나?
B: 오후 3시쯤 어때?
A: 좋아. 그럼 내일 봐!
B: 응, 내일 봐!""",
        "script_en": """A: Hi! How was your day?
B: Hi! It was good. How about you?
A: It was good too. What are you doing tomorrow?
B: Tomorrow I'm meeting friends. Do you want to join?
A: Sure! What time?
B: How about 3 o'clock in the afternoon?
A: Sounds good. See you tomorrow!
B: Yes, see you tomorrow!""",
        "vocabulary": [
            {"word": "How was your day?", "meaning": "오늘 하루 어땠어?", "type": "phrase"},
            {"word": "meet", "meaning": "만나다", "type": "verb"},
            {"word": "join", "meaning": "참여하다, 합류하다", "type": "verb"},
            {"word": "afternoon", "meaning": "오후", "type": "noun"},
            {"word": "tomorrow", "meaning": "내일", "type": "adverb"},
        ],
        "learning_points": [
            "일상적인 인사말",
            "미래 계획 표현하기 (What are you doing tomorrow?)",
            "시간 제안하기 (How about 3 o'clock?)",
            "약속 확정하기 (See you tomorrow!)"
        ]
    }


async def _fetch_news_content() -> Dict[str, Any]:
    """뉴스 콘텐츠: 3~5분 학습용 뉴스"""

    return {
        "title": "VOA Learning English - Technology and Education",
        "source": "VOA Learning English",
        "source_url": "https://learningenglish.voanews.com/",
        "audio_url": "https://learningenglish.voanews.com/a/learningenglish/",
        "youtube_id": None,
        "duration": "4 minutes 32 seconds",
        "difficulty": "Intermediate (B1-B2)",
        "topic": "기술과 교육",
        "script_ko": """현대 기술이 교육을 어떻게 변화시키고 있는지 살펴봅시다.

온라인 학습 플랫폼들이 전 세계 학생들에게 새로운 기회를 제공하고 있습니다.
코로나 팬데믹 이후, 많은 학교들이 디지털 도구를 사용하기 시작했습니다.

인공지능 기술은 개인화된 학습을 가능하게 합니다.
학생들은 자신의 속도에 맞춰 배울 수 있습니다.

하지만 모든 학생이 이러한 기술에 접근할 수 있는 것은 아닙니다.
개발도상국의 많은 학생들은 여전히 인터넷 접근이 어렵습니다.

교육 기술의 미래는 모든 사람에게 동등한 기회를 제공하는 것입니다.""",
        "script_en": """Let's look at how modern technology is changing education.

Online learning platforms are providing new opportunities to students around the world.
Since the coronavirus pandemic, many schools have started using digital tools.

Artificial intelligence technology makes personalized learning possible.
Students can learn at their own pace.

However, not all students have access to these technologies.
Many students in developing countries still find it difficult to access the Internet.

The future of educational technology is providing equal opportunities for everyone.""",
        "vocabulary": [
            {"word": "technology", "meaning": "기술", "type": "noun"},
            {"word": "platform", "meaning": "플랫폼", "type": "noun"},
            {"word": "opportunity", "meaning": "기회", "type": "noun"},
            {"word": "pandemic", "meaning": "팬데믹, 대유행", "type": "noun"},
            {"word": "digital tool", "meaning": "디지털 도구", "type": "phrase"},
            {"word": "artificial intelligence", "meaning": "인공지능", "type": "phrase"},
            {"word": "personalized learning", "meaning": "개인화된 학습", "type": "phrase"},
            {"word": "at their own pace", "meaning": "자신의 속도로", "type": "phrase"},
            {"word": "access", "meaning": "접근하다", "type": "verb"},
            {"word": "equal opportunity", "meaning": "동등한 기회", "type": "phrase"},
        ],
        "learning_points": [
            "기술 관련 주요 단어 학습",
            "현재 진행형 (is changing, are providing)",
            "부정사 표현 (to provide, to access)",
            "뉴스 속 복합 문장 이해",
            "교육 관련 용어 습득"
        ]
    }


# 캐시용 함수 (테스트)
def get_today_listening_sync() -> Dict[str, Any]:
    """동기 버전 (테스트용)"""
    return {
        "beginner": {
            "title": "Daily English Conversation - Meeting a Friend",
            "source": "Learn English with EnglishClub",
            "duration": "1 minute",
            "difficulty": "Beginner",
            "script_ko": "A: 안녕! 오늘 하루 어땠어?\nB: 안녕! 좋았어. 너는?",
            "script_en": "A: Hi! How was your day?\nB: Hi! It was good. How about you?",
            "vocabulary": []
        },
        "news": {
            "title": "VOA Learning English - Technology and Education",
            "source": "VOA Learning English",
            "duration": "4 minutes 32 seconds",
            "difficulty": "Intermediate",
            "script_ko": "현대 기술이 교육을 어떻게 변화시키고 있는지 살펴봅시다.",
            "script_en": "Let's look at how modern technology is changing education.",
            "vocabulary": []
        }
    }


if __name__ == "__main__":
    # 테스트
    content = get_today_listening_sync()
    print(json.dumps(content, ensure_ascii=False, indent=2))
