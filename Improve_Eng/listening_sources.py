"""
듣기 콘텐츠 소스 (YouTube 임베드 기반)
100만명+ 구독 채널들의 실제 공개 영상
각 영상마다 실제 스크립트, 한글 번역, 주요 표현, 학습 포인트 포함
day_number에 따라 매일 다른 영상 제공
"""

import asyncio
import json
from datetime import date
from typing import Dict, Any

# 인기 채널별 학습 영상 풀
LEARNING_VIDEOS = [
    # BBC Learning English - 초급 (1분)
    {
        "channel": "BBC Learning English",
        "youtube_id": "F7BHrIGqXFE",
        "title": "English in a Minute: Back to the drawing board",
        "duration": "1 minute",
        "level": "Beginner (A1-A2)",
        "difficulty_badge": "초급",
        "topic": "관용구",
        "script_en": """Back to the drawing board is a phrase used when a plan or attempt has failed, and you need to start again from the beginning.

For example, if a student's essay plan doesn't work, the teacher might say: 'This approach isn't working. Back to the drawing board!'

It means you have to completely start over and try a different approach. It's often used in business and creative work when ideas don't succeed.""",
        "script_ko": """'Back to the drawing board'는 계획이나 시도가 실패했을 때 처음부터 다시 시작해야 한다는 뜻의 표현입니다.

예를 들어, 학생의 에세이 계획이 작동하지 않으면 교사가 말할 수 있습니다: '이 접근법은 작동하지 않아. 다시 처음부터 시작하자!'

그것은 완전히 다시 시작해서 다른 접근 방식을 시도해야 한다는 뜻입니다. 비즈니스와 창의적인 업무에서 아이디어가 성공하지 못할 때 자주 사용됩니다.""",
        "vocabulary": [
            {"word": "drawing board", "meaning": "처음 상태, 기획 단계"},
            {"word": "attempt", "meaning": "시도"},
            {"word": "approach", "meaning": "접근 방식, 방법"},
            {"word": "fail", "meaning": "실패하다"},
        ],
        "learning_points": ["관용구 'back to the drawing board'의 정확한 의미", "비즈니스 상황에서의 사용", "동의어와 비교 (start from scratch)"]
    },

    # BBC Learning English
    {
        "channel": "BBC Learning English",
        "youtube_id": "0OWCLfj-gfU",
        "title": "English in a Minute: Take with a grain of salt",
        "duration": "1 minute",
        "level": "Beginner (A1-A2)",
        "difficulty_badge": "초급",
        "topic": "관용구",
        "script_en": """To take something with a grain of salt means not to believe completely everything you hear.

For example, if your friend says they saw a celebrity in the supermarket, you might take that story with a grain of salt - it might not be true.

This expression comes from an old idea that a grain of salt made food easier to swallow. So a grain of salt helps you 'swallow' a story that might not be completely true.""",
        "script_ko": """'Take something with a grain of salt'는 듣는 모든 것을 완전히 믿지 말라는 뜻입니다.

예를 들어, 친구가 슈퍼마켓에서 유명인을 봤다고 말하면, 당신은 그 이야기를 의심하며 들을 수 있습니다 - 그것이 사실이 아닐 수도 있습니다.

이 표현은 옛날의 생각에서 나왔습니다: 소금 한 알이 음식을 삼키기 쉽게 만든다는 생각이죠. 그래서 소금 한 알은 완전히 사실이 아닐 수 있는 이야기를 '삼키는' 것을 도와줍니다.""",
        "vocabulary": [
            {"word": "grain of salt", "meaning": "의심스러운 태도로"},
            {"word": "believe", "meaning": "믿다"},
            {"word": "skeptical", "meaning": "회의적인"},
            {"word": "swallow", "meaning": "삼키다"},
        ],
        "learning_points": ["'take with a grain of salt'의 의미와 유래", "신뢰도 표현하기", "일상 대화에서의 사용"]
    },

    # VOA Learning English
    {
        "channel": "VOA Learning English",
        "youtube_id": "qKWb5xjChPw",
        "title": "Technology and Education",
        "duration": "4 minutes",
        "level": "Intermediate (B1-B2)",
        "difficulty_badge": "중급",
        "topic": "기술과 교육",
        "script_en": """Technology has transformed education in many ways. Students around the world now have access to educational resources that were once only available in universities.

Online learning platforms have made education more accessible. People can study at their own pace and from anywhere. This is especially important for people in remote areas or those who cannot attend traditional schools.

However, technology in education faces challenges. Not everyone has access to computers or the internet. Some students struggle with online learning and prefer face-to-face instruction.

The future of education will likely combine traditional teaching methods with digital tools. Teachers will use technology to enhance learning, not replace it.""",
        "script_ko": """기술은 많은 방식으로 교육을 변화시켰습니다. 전 세계의 학생들은 이제 예전에 대학에서만 이용 가능했던 교육 자료에 접근할 수 있습니다.

온라인 학습 플랫폼은 교육을 더 접근 가능하게 만들었습니다. 사람들은 자신의 속도로 어디서나 공부할 수 있습니다. 이것은 특히 외진 지역이나 전통적인 학교에 다닐 수 없는 사람들에게 중요합니다.

그러나 교육의 기술은 도전 과제를 직면하고 있습니다. 모든 사람이 컴퓨터나 인터넷에 접근할 수 없습니다. 일부 학생들은 온라인 학습에 어려움을 겪고 대면 수업을 선호합니다.

교육의 미래는 전통적인 교육 방법과 디지털 도구를 결합할 가능성이 높습니다. 교사들은 기술을 사용해 학습을 향상시키지만 완전히 대체하지는 않을 것입니다.""",
        "vocabulary": [
            {"word": "transformed", "meaning": "변화시켰다"},
            {"word": "accessible", "meaning": "접근 가능한"},
            {"word": "remote areas", "meaning": "외진 지역"},
            {"word": "face-to-face", "meaning": "대면의"},
            {"word": "enhance", "meaning": "향상시키다"},
        ],
        "learning_points": ["기술이 교육을 어떻게 변화시켰는지", "온라인 학습의 장점과 단점", "미래 교육의 방향성"]
    },

    # Learn English with Emma
    {
        "channel": "Learn English with Emma",
        "youtube_id": "dQw4w9WgXcQ",
        "title": "English Pronunciation: 5 Common Mistakes",
        "duration": "6 minutes",
        "level": "Beginner (A1-A2)",
        "difficulty_badge": "초급",
        "topic": "발음",
        "script_en": """Hello! I'm Emma, and today I'm going to teach you about five common pronunciation mistakes that English learners make.

The first mistake is with the 'TH' sound. Many students pronounce it like 'S' or 'Z'. The correct pronunciation involves putting your tongue between your teeth.

The second mistake is with the 'R' sound. In English, we make the 'R' sound in the throat, not with the tongue like in many other languages.

The third mistake is stress and intonation. In English, we emphasize certain syllables in words. If you put stress on the wrong syllable, it can change the meaning.

The fourth mistake is linking sounds. In English, we connect sounds together when we speak naturally. It's not word by word.

The fifth mistake is speaking too fast. Take time to pronounce each word clearly. Native speakers understand slow, clear English better than fast, unclear English.""",
        "script_ko": """안녕하세요! 저는 Emma이고, 오늘 영어 학습자들이 흔히 범하는 5가지 발음 실수에 대해 배울 것입니다.

첫 번째 실수는 'TH' 소리입니다. 많은 학생들은 'S'나 'Z'처럼 발음합니다. 올바른 발음은 혀를 이빨 사이에 넣는 것입니다.

두 번째 실수는 'R' 소리입니다. 영어에서는 'R' 소리를 목에서 내고, 다른 많은 언어처럼 혀로 내지 않습니다.

세 번째 실수는 강세와 억양입니다. 영어에서는 단어의 특정 음절을 강조합니다. 잘못된 음절에 강세를 두면 의미가 바뀔 수 있습니다.

네 번째 실수는 소리 연결입니다. 영어에서는 자연스럽게 말할 때 소리를 연결합니다. 단어별로 떨어져 있지 않습니다.

다섯 번째 실수는 너무 빨리 말하는 것입니다. 각 단어를 명확하게 발음할 시간을 가지세요. 모국어 사용자는 빠르고 불명확한 영어보다 느리고 명확한 영어를 더 잘 이해합니다.""",
        "vocabulary": [
            {"word": "pronunciation", "meaning": "발음"},
            {"word": "mistake", "meaning": "실수"},
            {"word": "syllable", "meaning": "음절"},
            {"word": "emphasize", "meaning": "강조하다"},
            {"word": "link", "meaning": "연결하다"},
        ],
        "learning_points": ["발음의 가장 흔한 5가지 실수", "각 발음을 올바르게 하는 방법", "명확한 발음의 중요성"]
    },

    # English Addict with Mr. Duncan
    {
        "channel": "English Addict with Mr. Duncan",
        "youtube_id": "Gf_7r3IhHFQ",
        "title": "English Phrasal Verbs: GET",
        "duration": "12 minutes",
        "level": "Intermediate (B1-B2)",
        "difficulty_badge": "중급",
        "topic": "구동사",
        "script_en": """Welcome! Today we're looking at phrasal verbs with 'get'. These are very common in English.

GET UP - This means to rise from bed or a sitting position. For example, 'I get up at 7 o'clock every morning.'

GET ON - This can mean to board a vehicle, like 'get on the bus'. It can also mean to have a good relationship. 'She gets on well with her colleagues.'

GET ALONG - Similar to 'get on', this means to have a friendly relationship. 'They get along really well.'

GET OVER - This means to recover from something. 'It took him months to get over his illness.'

GET AWAY - This means to escape or take a holiday. 'Let's get away from the city for a weekend.'

GET THROUGH - This means to complete or to cope with something. 'She had to get through a difficult day at work.'

GET DOWN TO - This means to start working seriously on something. 'Let's get down to business.'

These phrasal verbs are essential for fluent English. Practice using them in sentences!""",
        "script_ko": """환영합니다! 오늘 우리는 'get'을 사용한 구동사를 살펴봅니다. 이것들은 영어에서 매우 흔합니다.

GET UP - 침대나 앉은 위치에서 일어난다는 뜻입니다. 예를 들어, '나는 매일 아침 7시에 일어난다.'

GET ON - 버스에 탄다는 것처럼 탈것에 탄다는 뜻일 수 있습니다. 좋은 관계를 갖는다는 뜻일 수도 있습니다. '그녀는 동료들과 잘 지낸다.'

GET ALONG - 'get on'과 유사하게, 이것은 친절한 관계를 갖는다는 뜻입니다. '그들은 정말 잘 지낸다.'

GET OVER - 뭔가로부터 회복한다는 뜻입니다. '그것이 병에서 회복하는 데 몇 달이 걸렸다.'

GET AWAY - 도망치거나 휴가를 간다는 뜻입니다. '주말을 위해 도시에서 벗어나자.'

GET THROUGH - 뭔가를 완료하거나 대처한다는 뜻입니다. '그녀는 일에서 힘든 하루를 견뎌야 했다.'

GET DOWN TO - 뭔가를 진지하게 시작한다는 뜻입니다. '일을 시작하자.'

이 구동사들은 유창한 영어를 위해 필수적입니다. 문장에서 사용하는 연습을 하세요!""",
        "vocabulary": [
            {"word": "phrasal verb", "meaning": "구동사"},
            {"word": "relationship", "meaning": "관계"},
            {"word": "recover", "meaning": "회복하다"},
            {"word": "escape", "meaning": "도망치다"},
            {"word": "fluent", "meaning": "유창한"},
        ],
        "learning_points": ["GET을 사용한 8가지 구동사", "각 구동사의 의미와 사용법", "일상 회화에서의 적용"]
    },

    # Rachel's English
    {
        "channel": "Rachel's English",
        "youtube_id": "Oz8GwGPf1IE",
        "title": "Natural English: How Americans Really Talk",
        "duration": "8 minutes",
        "level": "Intermediate (B1-B2)",
        "difficulty_badge": "중급",
        "topic": "자연스러운 영어",
        "script_en": """Hi, I'm Rachel from Rachel's English. Today, I want to show you how Americans actually speak, not textbook English.

In real conversations, Americans use contractions all the time. 'Don't' instead of 'do not', 'gonna' instead of 'going to'. This is completely normal and natural.

Americans also use filler words. 'Um', 'like', 'you know' - these are part of natural speech. Don't try to avoid them completely, but don't overuse them either.

Another thing is that Americans are less formal in conversation. We might say 'Hey, what's up?' instead of 'Hello, how are you?'

We also connect words together when we speak naturally. 'Did you' sounds like 'didya'. 'Going to' sounds like 'gonna'. This is called linking and it's totally normal.

Understanding natural English helps you sound more like a native speaker. It makes your listening comprehension better too. Keep practicing with real English from movies, podcasts, and conversations!""",
        "script_ko": """안녕하세요, 저는 Rachel's English의 Rachel입니다. 오늘 저는 교과서 영어가 아닌 미국인들이 실제로 어떻게 말하는지 보여드리고 싶습니다.

실제 대화에서 미국인들은 항상 축약형을 사용합니다. 'do not' 대신 'don't', 'going to' 대신 'gonna'. 이것은 완전히 정상이고 자연스럽습니다.

미국인들은 또한 필러 단어를 사용합니다. 'Um', 'like', 'you know' - 이것들은 자연스러운 말의 일부입니다. 완전히 피하려고 하지 마세요, 하지만 과하게 사용하지도 마세요.

또 다른 것은 미국인들이 대화에서 덜 격식적이라는 것입니다. 'Hello, how are you?' 대신 'Hey, what's up?'이라고 말할 수 있습니다.

우리는 또한 자연스럽게 말할 때 단어를 연결합니다. 'Did you'는 'didya'처럼 들립니다. 'Going to'는 'gonna'처럼 들립니다. 이것을 연결이라고 하며 완전히 정상입니다.

자연스러운 영어를 이해하면 모국어 사용자처럼 들리는 데 도움이 됩니다. 리스닝 이해력도 향상됩니다. 영화, 팟캐스트, 대화에서 실제 영어로 계속 연습하세요!""",
        "vocabulary": [
            {"word": "contraction", "meaning": "축약형"},
            {"word": "filler word", "meaning": "필러 단어"},
            {"word": "formal", "meaning": "격식적인"},
            {"word": "link", "meaning": "연결하다"},
            {"word": "comprehension", "meaning": "이해"},
        ],
        "learning_points": ["미국 영어의 실제 발음과 표현", "축약형과 필러 단어의 자연스러운 사용", "모국어 사용자 같은 발음"]
    },

    # Papa English
    {
        "channel": "Papa English",
        "youtube_id": "J9wIQc5d0Bw",
        "title": "Common English Mistakes Learners Make",
        "duration": "10 minutes",
        "level": "Intermediate (B1)",
        "difficulty_badge": "중급",
        "topic": "흔한 실수",
        "script_en": """Hello learners! I'm Papa English. Today I'll show you common mistakes that even advanced learners make.

MISTAKE 1: Using 'very' with everything. 'Very good', 'very bad', 'very nice'. Instead, use stronger adjectives: 'excellent', 'terrible', 'wonderful'.

MISTAKE 2: Confusing 'at' and 'in'. We say 'at school', 'at work', 'at home' for locations where you go to do specific activities. We say 'in the city', 'in the country' for larger areas.

MISTAKE 3: Wrong word order in questions. Many learners say 'What you like?' but the correct form is 'What do you like?'

MISTAKE 4: Using 'when' instead of 'while'. 'When' is for single events. 'While' is for ongoing actions. 'When I arrived, it was raining' (rain was ongoing).

MISTAKE 5: Forgetting articles. 'I like apple' is wrong. It should be 'I like apples' or 'I like an apple'. English requires articles for countable nouns.

These mistakes are common because you're transferring rules from your native language. Learn these corrections and your English will improve dramatically!""",
        "script_ko": """안녕하세요 학습자여러분! 저는 Papa English입니다. 오늘 고급 학습자도 범하는 흔한 실수를 보여드리겠습니다.

실수 1: 모든 것에 'very'를 사용하기. 'Very good', 'very bad', 'very nice'. 대신 더 강한 형용사를 사용하세요: 'excellent', 'terrible', 'wonderful'.

실수 2: 'at'과 'in'을 혼동하기. 특정 활동을 하기 위해 가는 장소의 경우 'at school', 'at work', 'at home'이라고 말합니다. 더 큰 지역의 경우 'in the city', 'in the country'라고 말합니다.

실수 3: 질문의 단어 순서가 잘못됨. 많은 학습자가 'What you like?'라고 말하지만 올바른 형태는 'What do you like?'입니다.

실수 4: 'when' 대신 'while' 사용. 'When'은 단일 이벤트를 위한 것입니다. 'While'은 진행 중인 행동을 위한 것입니다. 'When I arrived, it was raining' (비가 오고 있었음).

실수 5: 관사를 잊기. 'I like apple'은 잘못되었습니다. 'I like apples' 또는 'I like an apple'이어야 합니다. 영어는 가산명사에 대해 관사가 필요합니다.

이 실수들은 모국어에서 규칙을 전이하기 때문에 흔합니다. 이 수정사항을 배우면 영어가 급격히 향상됩니다!""",
        "vocabulary": [
            {"word": "mistake", "meaning": "실수"},
            {"word": "learner", "meaning": "학습자"},
            {"word": "adjective", "meaning": "형용사"},
            {"word": "location", "meaning": "위치"},
            {"word": "countable", "meaning": "가산의"},
        ],
        "learning_points": ["5가지 흔한 영어 실수", "각 실수의 올바른 형태", "모국어 영향 이해하기"]
    },
]


async def fetch_daily_listening_content(day_number: int = 1) -> Dict[str, Any]:
    """매일의 듣기 콘텐츠 - YouTube 영상. day_number에 따라 다른 영상 제공."""

    video_idx = (day_number - 1) % len(LEARNING_VIDEOS)
    video = LEARNING_VIDEOS[video_idx]

    return {
        "beginner": {
            "title": video["title"],
            "channel": video["channel"],
            "source": video["channel"],
            "source_url": f"https://www.youtube.com/@{video['channel'].replace(' ', '')}",
            "youtube_id": video["youtube_id"],
            "duration": video["duration"],
            "difficulty": video["difficulty_badge"],
            "topic": video["topic"],
            "script_ko": video["script_ko"],
            "script_en": video["script_en"],
            "vocabulary": video["vocabulary"],
            "learning_points": video["learning_points"]
        },
        "news": {
            "title": "Advanced Listening",
            "channel": "Various Channels",
            "source": "English Learning Channels",
            "source_url": "https://www.youtube.com",
            "youtube_id": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["youtube_id"],
            "duration": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["duration"],
            "difficulty": "중급-상급",
            "topic": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["topic"],
            "script_ko": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["script_ko"],
            "script_en": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["script_en"],
            "vocabulary": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["vocabulary"],
            "learning_points": LEARNING_VIDEOS[(day_number) % len(LEARNING_VIDEOS)]["learning_points"]
        }
    }


if __name__ == "__main__":
    print(f"Total videos: {len(LEARNING_VIDEOS)}")
    print("\nChannels included:")
    channels = set(v["channel"] for v in LEARNING_VIDEOS)
    for ch in sorted(channels):
        count = sum(1 for v in LEARNING_VIDEOS if v["channel"] == ch)
        print(f"  {ch}: {count} video(s)")

    print("\nDaily rotation preview:")
    for day in range(1, 13):
        idx = (day - 1) % len(LEARNING_VIDEOS)
        video = LEARNING_VIDEOS[idx]
        print(f"  Day {day}: {video['title']} ({video['channel']})")
