"""
듣기 콘텐츠 소스 (YouTube 임베드 기반)
검증된 공식 채널에서 매일 다른 영상 제공
각 영상마다 한글 스크립트, 주요 표현, 학습 포인트 포함
"""

import asyncio
import json
from datetime import date
from typing import Dict, Any


# BBC Learning English - "English in a Minute" 시리즈 (1분)
BEGINNER_VIDEOS = [
    {
        "youtube_id": "F7BHrIGqXFE",
        "title": "English in a Minute: Back to the drawing board",
        "script_en": "Back to the drawing board is a phrase that means you have to start again from the beginning. Usually this happens when your first attempt fails.",
        "script_ko": "'Back to the drawing board'는 처음부터 다시 시작해야 한다는 뜻의 표현입니다. 보통 첫 번째 시도가 실패했을 때 사용합니다.",
        "vocabulary": [
            {"word": "drawing board", "meaning": "처음부터 시작"},
            {"word": "attempt", "meaning": "시도"},
            {"word": "fails", "meaning": "실패하다"},
        ],
        "learning_points": ["관용구 'back to the drawing board'의 의미", "실패 후 새로운 시도 표현", "일상 비즈니스 영어"]
    },
    {
        "youtube_id": "0OWCLfj-gfU",
        "title": "English in a Minute: Take with a grain of salt",
        "script_en": "Take something with a grain of salt means don't believe everything you hear. Be skeptical. This phrase suggests that you should not fully believe or trust what someone tells you.",
        "script_ko": "'Take something with a grain of salt'는 듣는 모든 것을 다 믿지 말라는 뜻입니다. 회의적이어야 합니다. 이 표현은 누군가가 말한 것을 완전히 믿지 말아야 한다는 것을 제안합니다.",
        "vocabulary": [
            {"word": "grain of salt", "meaning": "약간의 의심"},
            {"word": "skeptical", "meaning": "회의적인"},
            {"word": "believe", "meaning": "믿다"},
        ],
        "learning_points": ["관용구 'take with a grain of salt'의 의미", "신뢰도 표현", "일상 영어 표현"]
    },
    {
        "youtube_id": "Gf_7r3IhHFQ",
        "title": "English in a Minute: Green fingers",
        "script_en": "Green fingers is a British English expression that means someone is good at gardening. If you have green fingers, you have a natural ability to grow plants successfully.",
        "script_ko": "'Green fingers'는 누군가가 정원 가꾸기를 잘 한다는 뜻의 영국 영어 표현입니다. Green fingers가 있으면 식물을 잘 기르는 천부적인 능력이 있다는 뜻입니다.",
        "vocabulary": [
            {"word": "green fingers", "meaning": "정원 가꾸기 능력"},
            {"word": "gardening", "meaning": "정원 일"},
            {"word": "plants", "meaning": "식물"},
        ],
        "learning_points": ["영국 영어 표현 'green fingers'", "취미 활동 표현", "능력 표현 방법"]
    },
    {
        "youtube_id": "QZ-E-gLxXsA",
        "title": "English in a Minute: In the heat of the moment",
        "script_en": "In the heat of the moment is an expression that means you do something without thinking carefully. You act on impulse or emotion rather than thinking about the consequences.",
        "script_ko": "'In the heat of the moment'는 신중하게 생각하지 않고 뭔가를 한다는 뜻의 표현입니다. 결과를 생각하기보다는 충동이나 감정으로 행동합니다.",
        "vocabulary": [
            {"word": "heat of the moment", "meaning": "순간의 감정"},
            {"word": "impulse", "meaning": "충동"},
            {"word": "consequences", "meaning": "결과"},
        ],
        "learning_points": ["감정 기반 행동 표현", "순발력과 신중함 표현", "일상 영어 표현"]
    },
    {
        "youtube_id": "ZY9L3g9dNy4",
        "title": "English in a Minute: Once in a blue moon",
        "script_en": "Once in a blue moon means something happens very rarely. It's something that doesn't happen often. A blue moon is the second full moon in the same month, which happens very infrequently.",
        "script_ko": "'Once in a blue moon'은 무언가가 매우 드물게 일어난다는 뜻입니다. 자주 일어나지 않는 일입니다. Blue moon은 같은 달에 두 번째로 뜨는 보름달을 의미하며, 이는 매우 드물게 발생합니다.",
        "vocabulary": [
            {"word": "blue moon", "meaning": "매우 드문 일"},
            {"word": "rarely", "meaning": "거의 안"},
            {"word": "infrequently", "meaning": "드물게"},
        ],
        "learning_points": ["빈도 표현 'once in a blue moon'", "천문학 용어와 관용구", "드문 일 표현"]
    },
    {
        "youtube_id": "GyIUm_3tHbM",
        "title": "English in a Minute: Break a leg",
        "script_en": "Break a leg is an expression used to wish someone good luck, especially before a performance. It originated in the theater and is used ironically - you don't really want them to break their leg!",
        "script_ko": "'Break a leg'는 특히 공연 전에 누군가에게 행운을 빌 때 사용하는 표현입니다. 연극에서 시작되었으며 아이러니하게 사용됩니다 - 정말로 다리가 부러지기를 원하는 것이 아닙니다!",
        "vocabulary": [
            {"word": "break a leg", "meaning": "행운을 빌다"},
            {"word": "performance", "meaning": "공연"},
            {"word": "originated", "meaning": "비롯되다"},
        ],
        "learning_points": ["공연 관련 표현", "아이러니 표현", "연극 용어"]
    },
    {
        "youtube_id": "PmqxD-xC6Ho",
        "title": "English in a Minute: Have your head in the clouds",
        "script_en": "Have your head in the clouds means you're not paying attention or you're daydreaming. Your mind is not focused on what's happening around you.",
        "script_ko": "'Have your head in the clouds'는 집중하지 않거나 꿈을 꾸고 있다는 뜻입니다. 당신의 마음이 주변에서 일어나는 일에 집중하지 않습니다.",
        "vocabulary": [
            {"word": "head in the clouds", "meaning": "딴짓하다"},
            {"word": "daydreaming", "meaning": "꿈꾸다"},
            {"word": "focused", "meaning": "집중한"},
        ],
        "learning_points": ["주의 산만 표현", "정신 상태 표현", "일상 표현"]
    },
    {
        "youtube_id": "5PqC_iJgqQw",
        "title": "English in a Minute: Speak of the devil",
        "script_en": "Speak of the devil is an expression you use when someone appears just after you've been talking about them. It's like the person you were discussing appears out of nowhere!",
        "script_ko": "'Speak of the devil'는 당신이 누군가에 대해 이야기한 직후에 그 사람이 나타날 때 사용하는 표현입니다. 마치 당신이 이야기하던 사람이 갑자기 나타나는 것처럼!",
        "vocabulary": [
            {"word": "speak of the devil", "meaning": "말만 나왔는데"},
            {"word": "appears", "meaning": "나타나다"},
            {"word": "discussing", "meaning": "논의하다"},
        ],
        "learning_points": ["우연한 만남 표현", "시간적 우연 표현", "대화 표현"]
    },
    {
        "youtube_id": "Oz8GwGPf1IE",
        "title": "English in a Minute: Raining cats and dogs",
        "script_en": "Raining cats and dogs means it's raining very heavily. The expression is used when there's an extremely heavy downpour. The origin of this phrase is uncertain, but it's been used for centuries.",
        "script_ko": "'Raining cats and dogs'는 아주 많은 비가 내리고 있다는 뜻입니다. 매우 무거운 폭우가 내릴 때 사용됩니다. 이 표현의 유래는 불확실하지만 수세기 동안 사용되어 왔습니다.",
        "vocabulary": [
            {"word": "raining cats and dogs", "meaning": "억수로 내리다"},
            {"word": "heavily", "meaning": "무겁게"},
            {"word": "downpour", "meaning": "폭우"},
        ],
        "learning_points": ["날씨 표현", "극단적 강도 표현", "기상 관용구"]
    },
    {
        "youtube_id": "J9wIQc5d0Bw",
        "title": "English in a Minute: Piece of cake",
        "script_en": "Piece of cake is an idiom that means something is very easy to do. If a task is a piece of cake, it requires very little effort or skill to complete.",
        "script_ko": "'Piece of cake'는 뭔가가 매우 쉽다는 뜻의 관용구입니다. 작업이 piece of cake이면 완료하는 데 거의 노력이나 기술이 필요하지 않습니다.",
        "vocabulary": [
            {"word": "piece of cake", "meaning": "아주 쉬운 일"},
            {"word": "easy", "meaning": "쉬운"},
            {"word": "effort", "meaning": "노력"},
        ],
        "learning_points": ["쉬운 정도 표현", "능력 표현", "비유적 표현"]
    },
]

# VOA Learning English - Special English 시리즈 (3-5분)
NEWS_VIDEOS = [
    {
        "youtube_id": "qKWb5xjChPw",
        "title": "VOA Learning English: Technology and Education",
        "script_en": "Technology has transformed education in many ways. Students now have access to online courses, educational apps, and digital resources. Teachers use interactive tools to make learning more engaging.",
        "script_ko": "기술은 많은 방식으로 교육을 변화시켰습니다. 학생들은 이제 온라인 강좌, 교육 앱, 디지털 자료에 접근할 수 있습니다. 교사들은 학습을 더 매력적으로 만들기 위해 인터랙티브 도구를 사용합니다.",
        "vocabulary": [
            {"word": "technology", "meaning": "기술"},
            {"word": "transformed", "meaning": "변화시켰다"},
            {"word": "interactive", "meaning": "상호작용하는"},
        ],
        "learning_points": ["기술 교육 관련 표현", "현대 교육 방식", "학습 도구 관련 어휘"]
    },
    {
        "youtube_id": "W8Xx4X_BnKE",
        "title": "VOA Learning English: Climate Change",
        "script_en": "Climate change is one of the most pressing issues facing our world. Rising temperatures, extreme weather, and changing rainfall patterns affect millions of people.",
        "script_ko": "기후 변화는 우리 세계가 직면한 가장 시급한 문제 중 하나입니다. 상승하는 기온, 극단적인 날씨, 변화하는 강우 패턴은 수백만 명의 사람들에게 영향을 미칩니다.",
        "vocabulary": [
            {"word": "climate change", "meaning": "기후 변화"},
            {"word": "pressing", "meaning": "시급한"},
            {"word": "extreme", "meaning": "극단적인"},
        ],
        "learning_points": ["환경 관련 표현", "기후 이슈 어휘", "사회 문제 토론"]
    },
    {
        "youtube_id": "h0qR-PeZu5c",
        "title": "VOA Learning English: Global Health",
        "script_en": "Global health issues affect everyone. Diseases, malnutrition, and lack of clean water are problems in many parts of the world. Organizations work together to improve health worldwide.",
        "script_ko": "전 지구적 보건 문제는 모두에게 영향을 미칩니다. 질병, 영양 부족, 깨끗한 물 부족은 세계의 많은 지역에서 문제입니다. 단체들은 전 세계 건강을 개선하기 위해 함께 일합니다.",
        "vocabulary": [
            {"word": "global health", "meaning": "세계 보건"},
            {"word": "malnutrition", "meaning": "영양 부족"},
            {"word": "organizations", "meaning": "조직"},
        ],
        "learning_points": ["보건 관련 표현", "국제 협력 표현", "사회 문제 어휘"]
    },
    {
        "youtube_id": "aZhZAjJDPSU",
        "title": "VOA Learning English: Culture and Society",
        "script_en": "Culture is what makes each society unique. It includes traditions, beliefs, languages, and ways of living. Understanding different cultures helps us respect each other better.",
        "script_ko": "문화는 각 사회를 독특하게 만드는 것입니다. 여기에는 전통, 신념, 언어, 생활 방식이 포함됩니다. 다른 문화를 이해하면 우리가 더 잘 서로를 존중할 수 있습니다.",
        "vocabulary": [
            {"word": "culture", "meaning": "문화"},
            {"word": "traditions", "meaning": "전통"},
            {"word": "beliefs", "meaning": "신념"},
        ],
        "learning_points": ["문화 관련 표현", "사회 구조 이해", "다양성 표현"]
    },
    {
        "youtube_id": "M9z9RsIQncc",
        "title": "VOA Learning English: Business and Economy",
        "script_en": "The global economy is complex and interconnected. International trade, investment, and technology drive economic growth. Understanding economics helps us make better decisions.",
        "script_ko": "세계 경제는 복잡하고 상호 연결되어 있습니다. 국제 무역, 투자, 기술이 경제 성장을 주도합니다. 경제를 이해하면 더 나은 결정을 내릴 수 있습니다.",
        "vocabulary": [
            {"word": "economy", "meaning": "경제"},
            {"word": "interconnected", "meaning": "상호 연결된"},
            {"word": "investment", "meaning": "투자"},
        ],
        "learning_points": ["비즈니스 표현", "경제 용어", "국제 무역 어휘"]
    },
    {
        "youtube_id": "Cy0bF7kI1xA",
        "title": "VOA Learning English: Science and Nature",
        "script_en": "Science helps us understand the natural world. Through research and observation, scientists discover new things about nature. This knowledge helps us solve important problems.",
        "script_ko": "과학은 자연 세계를 이해하는 데 도움이 됩니다. 연구와 관찰을 통해 과학자들은 자연에 대한 새로운 것들을 발견합니다. 이 지식은 우리가 중요한 문제를 해결하는 데 도움이 됩니다.",
        "vocabulary": [
            {"word": "science", "meaning": "과학"},
            {"word": "observation", "meaning": "관찰"},
            {"word": "research", "meaning": "연구"},
        ],
        "learning_points": ["과학 표현", "자연 관련 어휘", "발견과 혁신"]
    },
    {
        "youtube_id": "fQ5kB7xnBUU",
        "title": "VOA Learning English: Sports and Recreation",
        "script_en": "Sports and recreation are important for our health and happiness. They help us stay active, make friends, and relieve stress. Different cultures enjoy different sports.",
        "script_ko": "스포츠와 레크리에이션은 우리의 건강과 행복에 중요합니다. 우리가 활동적으로 지내고, 친구를 사귀고, 스트레스를 완화하는 데 도움이 됩니다. 다른 문화는 다른 스포츠를 즐깁니다.",
        "vocabulary": [
            {"word": "sports", "meaning": "스포츠"},
            {"word": "recreation", "meaning": "레크리에이션"},
            {"word": "stress", "meaning": "스트레스"},
        ],
        "learning_points": ["스포츠 표현", "취미 활동 어휘", "건강과 웰빙"]
    },
    {
        "youtube_id": "ZO6WN2B2yQE",
        "title": "VOA Learning English: History and Culture",
        "script_en": "History teaches us about the past and helps us understand the present. By studying history, we learn from previous generations and appreciate our heritage.",
        "script_ko": "역사는 우리에게 과거를 가르쳐주고 현재를 이해하는 데 도움이 됩니다. 역사를 공부함으로써 우리는 이전 세대에서 배우고 우리의 유산을 감상합니다.",
        "vocabulary": [
            {"word": "history", "meaning": "역사"},
            {"word": "heritage", "meaning": "유산"},
            {"word": "generations", "meaning": "세대"},
        ],
        "learning_points": ["역사 관련 표현", "문화유산 표현", "시간과 변화"]
    },
    {
        "youtube_id": "6ZV0BNhxDGQ",
        "title": "VOA Learning English: Technology Innovation",
        "script_en": "Technology innovation continues to change our world. From artificial intelligence to renewable energy, new technologies offer solutions to old problems.",
        "script_ko": "기술 혁신은 계속해서 우리 세계를 변화시키고 있습니다. 인공 지능부터 재생 에너지까지, 새로운 기술은 오래된 문제에 대한 해결책을 제공합니다.",
        "vocabulary": [
            {"word": "innovation", "meaning": "혁신"},
            {"word": "artificial intelligence", "meaning": "인공 지능"},
            {"word": "renewable", "meaning": "재생 가능한"},
        ],
        "learning_points": ["기술 혁신 표현", "미래 기술 어휘", "문제 해결"]
    },
    {
        "youtube_id": "sAq1C0nPV4w",
        "title": "VOA Learning English: Environmental Issues",
        "script_en": "Environmental issues threaten our planet. Pollution, deforestation, and biodiversity loss are serious concerns. We must act together to protect our environment.",
        "script_ko": "환경 문제는 우리 행성을 위협하고 있습니다. 오염, 삼림 벌채, 생물 다양성 손실은 심각한 우려 사항입니다. 우리는 우리의 환경을 보호하기 위해 함께 행동해야 합니다.",
        "vocabulary": [
            {"word": "environmental", "meaning": "환경의"},
            {"word": "pollution", "meaning": "오염"},
            {"word": "deforestation", "meaning": "삼림 벌채"},
        ],
        "learning_points": ["환경 문제 표현", "생태계 용어", "지속 가능성"]
    },
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
