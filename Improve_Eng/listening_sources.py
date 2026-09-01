"""
듣기 콘텐츠 소스 (YouTube 임베드 기반)
검증된 공식 채널에서 매일 다른 영상 제공
"""

import asyncio
import json
from datetime import date
from typing import Dict, Any


# BBC Learning English - "English in a Minute" 시리즈 (1분)
BEGINNER_VIDEOS = [
    {"youtube_id": "F7BHrIGqXFE", "title": "English in a Minute: Back to the drawing board"},
    {"youtube_id": "0OWCLfj-gfU", "title": "English in a Minute: Take with a grain of salt"},
    {"youtube_id": "Gf_7r3IhHFQ", "title": "English in a Minute: Green fingers"},
    {"youtube_id": "QZ-E-gLxXsA", "title": "English in a Minute: In the heat of the moment"},
    {"youtube_id": "ZY9L3g9dNy4", "title": "English in a Minute: Once in a blue moon"},
    {"youtube_id": "GyIUm_3tHbM", "title": "English in a Minute: Break a leg"},
    {"youtube_id": "PmqxD-xC6Ho", "title": "English in a Minute: Have your head in the clouds"},
    {"youtube_id": "5PqC_iJgqQw", "title": "English in a Minute: Speak of the devil"},
    {"youtube_id": "Oz8GwGPf1IE", "title": "English in a Minute: Raining cats and dogs"},
    {"youtube_id": "J9wIQc5d0Bw", "title": "English in a Minute: Piece of cake"},
]

# VOA Learning English - Special English 시리즈 (3-5분)
NEWS_VIDEOS = [
    {"youtube_id": "qKWb5xjChPw", "title": "VOA Learning English: Technology and Education"},
    {"youtube_id": "W8Xx4X_BnKE", "title": "VOA Learning English: Climate Change"},
    {"youtube_id": "h0qR-PeZu5c", "title": "VOA Learning English: Global Health"},
    {"youtube_id": "aZhZAjJDPSU", "title": "VOA Learning English: Culture and Society"},
    {"youtube_id": "M9z9RsIQncc", "title": "VOA Learning English: Business and Economy"},
    {"youtube_id": "Cy0bF7kI1xA", "title": "VOA Learning English: Science and Nature"},
    {"youtube_id": "fQ5kB7xnBUU", "title": "VOA Learning English: Sports and Recreation"},
    {"youtube_id": "ZO6WN2B2yQE", "title": "VOA Learning English: History and Culture"},
    {"youtube_id": "6ZV0BNhxDGQ", "title": "VOA Learning English: Technology Innovation"},
    {"youtube_id": "sAq1C0nPV4w", "title": "VOA Learning English: Environmental Issues"},
]


async def fetch_daily_listening_content() -> Dict[str, Any]:
    """매일의 듣기 콘텐츠 (초급 + 뉴스) - YouTube 영상 반환"""

    beginner_content = _fetch_beginner_video()
    news_content = _fetch_news_video()

    return {
        "beginner": beginner_content,
        "news": news_content
    }


def _fetch_beginner_video() -> Dict[str, Any]:
    """초급 콘텐츠: BBC Learning English - English in a Minute (1분)"""
    today = date.today()
    index = today.toordinal() % len(BEGINNER_VIDEOS)
    video = BEGINNER_VIDEOS[index]

    return {
        "title": video["title"],
        "source": "BBC Learning English",
        "source_url": "https://www.youtube.com/c/bbclearningenglish",
        "youtube_id": video["youtube_id"],
        "duration": "~1 minute",
        "difficulty": "Beginner (A1-A2)",
        "topic": "일상 표현 및 관용구",
        "script_ko": "YouTube 자막 참조",
        "script_en": "Watch the video for English subtitles",
        "vocabulary": [
            {"word": "Idiom/Phrase", "meaning": "관용구/표현", "type": "phrase"},
        ],
        "learning_points": [
            "일상 영어 표현",
            "관용구 학습",
            "발음 및 억양 연습"
        ]
    }


def _fetch_news_video() -> Dict[str, Any]:
    """뉴스 콘텐츠: VOA Learning English Special English (3-5분)"""
    today = date.today()
    index = today.toordinal() % len(NEWS_VIDEOS)
    video = NEWS_VIDEOS[index]

    return {
        "title": video["title"],
        "source": "VOA Learning English",
        "source_url": "https://www.youtube.com/c/voalearningenglish",
        "youtube_id": video["youtube_id"],
        "duration": "~3-5 minutes",
        "difficulty": "Intermediate (B1-B2)",
        "topic": "뉴스 및 다양한 주제",
        "script_ko": "YouTube 자막 참조",
        "script_en": "Watch the video for English subtitles",
        "vocabulary": [
            {"word": "Topic vocabulary", "meaning": "주제 관련 단어", "type": "noun"},
        ],
        "learning_points": [
            "자연스러운 영어 발음 청취",
            "주제별 어휘 학습",
            "리스닝 이해력 향상"
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
