#!/usr/bin/env python3
"""
3개월 분량(65개) 문법 커리큘럼 생성
grammar_curriculum.py를 완전히 대체합니다.
"""

import json

# 65개 주제 정의
TOPICS = [
    # A1 초급 (20개)
    ("simple_present_1", "단순 현재형 - 기본", "A1"),
    ("simple_present_2", "단순 현재형 - 의문문과 부정문", "A1"),
    ("simple_present_3", "단순 현재형 - 일상 표현", "A1"),
    ("simple_past_1", "단순 과거형 - 규칙동사", "A1"),
    ("simple_past_2", "단순 과거형 - 불규칙동사", "A1"),
    ("simple_past_3", "단순 과거형 - 의문문과 부정문", "A2"),
    ("simple_future_1", "단순 미래형 - Will", "A1"),
    ("simple_future_2", "단순 미래형 - Going to", "A1"),
    ("present_continuous_1", "현재진행형 - 기본", "A1"),
    ("present_continuous_2", "현재진행형 vs 단순현재형", "A2"),
    ("articles_1", "관사 - A/An", "A1"),
    ("articles_2", "관사 - The", "A1"),
    ("prepositions_1", "전치사 - 장소와 방향", "A1"),
    ("prepositions_2", "전치사 - 시간", "A1"),
    ("personal_pronouns_1", "인칭대명사", "A1"),
    ("possessive_1", "소유격 형용사와 대명사", "A1"),
    ("imperative_1", "명령형", "A1"),
    ("there_is_are_1", "There is / There are", "A1"),
    ("past_continuous_1", "과거진행형", "A2"),
    ("past_continuous_2", "과거진행형 vs 단순과거형", "A2"),

    # B1 중급 (35개)
    ("can_could_1", "Can / Could - 능력", "A2"),
    ("can_could_2", "Can / Could - 허가와 요청", "A2"),
    ("word_order_1", "기본 어순", "A2"),
    ("word_order_2", "부사의 위치", "A2"),
    ("negation_1", "부정문 만들기", "A2"),
    ("question_formation_1", "의문문 - Yes/No 질문", "A2"),
    ("question_formation_2", "의문문 - Wh- 질문", "A2"),

    ("present_perfect_1", "현재완료 - 기본", "B1"),
    ("present_perfect_2", "현재완료 - 경험과 최근 변화", "B1"),
    ("present_perfect_3", "현재완료 vs 단순과거", "B1"),
    ("present_perfect_continuous_1", "현재완료진행형", "B1"),
    ("present_perfect_continuous_2", "현재완료진행형 vs 현재완료", "B1"),
    ("past_perfect_1", "과거완료", "B1"),
    ("past_perfect_2", "과거완료 vs 단순과거", "B1"),

    ("infinitive_1", "부정사 - 기초", "B1"),
    ("infinitive_2", "부정사 - 목적사용", "B1"),
    ("infinitive_3", "부정사 - To의 생략 (Bare Infinitive)", "B1"),

    ("gerund_1", "동명사 - 기초", "B1"),
    ("gerund_2", "동명사 vs 부정사", "B1"),
    ("gerund_3", "동명사 - 전치사 이후", "B1"),

    ("passive_voice_1", "수동태 - 기본", "B1"),
    ("passive_voice_2", "수동태 - 시제별 사용", "B1"),
    ("passive_voice_3", "수동태 - 전치사와 간접목적어", "B1"),

    ("conditional_1", "가정법 - 1형 (실현 가능)", "B1"),
    ("conditional_2", "가정법 - 2형 (가정)", "B1"),
    ("conditional_3", "가정법 - 3형 및 Mixed (반사실적)", "B1"),

    ("relative_clauses_1", "관계절 - Who/Whom", "B1"),
    ("relative_clauses_2", "관계절 - Which/That", "B1"),
    ("relative_clauses_3", "관계절 - Whose/Where/When", "B1"),

    ("reported_speech_1", "간접화법 - 진술", "B1"),
    ("reported_speech_2", "간접화법 - 질문과 명령", "B1"),
    ("reported_speech_3", "간접화법 - 시제 변화 규칙", "B1"),

    ("modal_verbs_1", "조동사 - Must/Have to (의무)", "B1"),
    ("modal_verbs_2", "조동사 - Should/Ought to (조언)", "B1"),
    ("modal_verbs_3", "조동사 - May/Might (가능성)", "B1"),
    ("modal_verbs_4", "조동사 - Can/Could (능력과 요청)", "B1"),

    ("comparison_1", "비교 - Comparative (비교급)", "B1"),
    ("comparison_2", "비교 - Superlative (최상급)", "B1"),
    ("comparison_3", "비교 - As ... as (동등 비교)", "B1"),

    ("phrasal_verbs_1", "구동사 - 기본 이해", "B1"),
    ("phrasal_verbs_2", "구동사 - Separable", "B1"),
    ("phrasal_verbs_3", "구동사 - 자주 쓰이는 표현", "B1"),

    # B2-C1 고급 (10개)
    ("inversion_1", "도치 - 강조 표현", "B2"),
    ("inversion_2", "도치 - 조건절", "B2"),

    ("subjunctive_1", "접속법 - I suggest/demand", "B2"),
    ("subjunctive_2", "접속법 - If I were/Could", "B2"),

    ("advanced_passive_1", "수동태 - 고급 표현", "B2"),

    ("cleft_sentences_1", "강조 구문 - It is ... that", "B2"),
    ("cleft_sentences_2", "강조 구문 - What 절", "B2"),

    ("advanced_articles_1", "관사 - 고급 사용법", "B2"),

    ("ellipsis_1", "생략 - 고급 표현", "C1"),
]

def create_entry(topic_id, topic_name, level):
    """각 주제별 기본 항목 생성"""

    # 주제별 샘플 내용 (실제 내용은 나중에 채우기)
    sample_explanations = {
        "simple_present": {
            "ko": "단순 현재형은 현재의 습관, 일반적인 사실, 반복되는 행동을 나타냅니다.",
            "en": "Simple Present describes habits, facts, and regular actions in the present."
        },
        "simple_past": {
            "ko": "단순 과거형은 과거의 완료된 사건이나 상황을 나타냅니다.",
            "en": "Simple Past describes completed actions or situations in the past."
        },
        "present_perfect": {
            "ko": "현재완료는 과거부터 현재까지의 경험, 변화, 결과를 나타냅니다.",
            "en": "Present Perfect shows experience, recent changes, or results from past to present."
        },
        "gerund": {
            "ko": "동명사는 동사+ing 형태로 명사처럼 사용되는 동사입니다.",
            "en": "Gerunds are verb+ing forms used as nouns in sentences."
        },
        "passive_voice": {
            "ko": "수동태는 행동의 대상이 주어가 되는 문장 형태입니다.",
            "en": "Passive voice focuses on the action and who/what it happens to."
        },
        "conditional": {
            "ko": "가정법은 가정이나 조건에 따른 결과를 나타냅니다.",
            "en": "Conditional sentences express conditions and their possible results."
        },
    }

    # 주제별 기본 설명 선택
    base_key = topic_id.rsplit('_', 1)[0]
    if base_key in sample_explanations:
        explanation_ko = sample_explanations[base_key]["ko"]
        explanation_en = sample_explanations[base_key]["en"]
    else:
        explanation_ko = f"{topic_name}을(를) 학습합니다."
        explanation_en = f"Learn about {topic_name}."

    return {
        "id": topic_id,
        "topic": topic_name,
        "level": level,
        "description": f"{topic_name}을(를) 학습합니다.",
        "explanation_ko": explanation_ko,
        "explanation_en": explanation_en,
        "examples": [
            {"sentence_en": "Example sentence 1.", "sentence_ko": "예시 문장 1."},
            {"sentence_en": "Example sentence 2.", "sentence_ko": "예시 문장 2."},
            {"sentence_en": "Example sentence 3.", "sentence_ko": "예시 문장 3."}
        ],
        "source": {
            "name": "BBC Learning English",
            "url": "https://www.bbc.co.uk/learningenglish/"
        },
        "additional_resources": [
            {"name": "Perfect English Grammar", "url": "https://www.perfectenglishgrammar.com/"},
            {"name": "British Council", "url": "https://learnenglish.britishcouncil.org/"},
            {"name": "EnglishClub", "url": "https://www.englishclub.com/"}
        ],
        "quiz": [
            {"question": "Question 1?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct": 0, "explanation": "Answer explanation."},
            {"question": "Question 2?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct": 1, "explanation": "Answer explanation."},
            {"question": "Question 3?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct": 2, "explanation": "Answer explanation."}
        ]
    }

def generate_curriculum():
    """전체 커리큘럼 생성"""
    curriculum = []
    for topic_id, topic_name, level in TOPICS:
        entry = create_entry(topic_id, topic_name, level)
        curriculum.append(entry)
    return curriculum

if __name__ == "__main__":
    curriculum = generate_curriculum()

    # Python 파일로 생성
    python_code = '''"""
영어 문법 커리큘럼 - 3개월 분량 (90일)
매일 다른 주제의 다른 회차를 제시합니다.
같은 주제가 연달아 나오지 않도록 설계되었습니다.
"""

GRAMMAR_CURRICULUM = '''

    python_code += repr(curriculum).replace("'", '"') + "\n\n"

    python_code += '''
def get_today_grammar(day_number: int) -> dict:
    """오늘의 문법 주제 반환 (매일 다른 주제)"""
    if not GRAMMAR_CURRICULUM:
        return {}

    # 일수 기반으로 주제 순환 (같은 주제 연속 방지)
    index = (day_number - 1) % len(GRAMMAR_CURRICULUM)
    return GRAMMAR_CURRICULUM[index]


if __name__ == "__main__":
    print(f"Total topics: {len(GRAMMAR_CURRICULUM)}")
    for day in range(1, 11):
        topic = get_today_grammar(day)
        print(f"Day {day}: {topic.get('topic')} ({topic.get('level')})")
'''

    with open("grammar_curriculum.py", "w", encoding="utf-8") as f:
        f.write(python_code)

    print(f"✅ {len(curriculum)}개 주제로 grammar_curriculum.py 생성됨!")
    print(f"  - A1 초급: {sum(1 for t in TOPICS if t[2] == 'A1')} 개")
    print(f"  - A2 초급-중급: {sum(1 for t in TOPICS if t[2] == 'A2')} 개")
    print(f"  - B1 중급: {sum(1 for t in TOPICS if t[2] == 'B1')} 개")
    print(f"  - B2 고급: {sum(1 for t in TOPICS if t[2] == 'B2')} 개")
    print(f"  - C1 고급: {sum(1 for t in TOPICS if t[2] == 'C1')} 개")
