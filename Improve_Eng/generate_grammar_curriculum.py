"""
문법 커리큘럼 자동 생성 도구
기존 grammar_curriculum.py를 3개월(90일) 분량으로 확장합니다.
"""

GRAMMAR_TOPICS = [
    # A1 초급 (Simple, Present, Past, Future)
    ("simple_present", "단순 현재형 - 기본 (Simple Present: Positive)", "A1", 1),
    ("simple_present", "단순 현재형 - 의문문과 부정문 (Simple Present: Questions & Negatives)", "A1", 2),
    ("simple_present", "단순 현재형 - 일상 표현과 습관 (Simple Present: Habits & Routines)", "A1", 3),

    ("simple_past", "단순 과거형 - 규칙동사 (Simple Past: Regular Verbs)", "A1", 1),
    ("simple_past", "단순 과거형 - 불규칙동사 (Simple Past: Irregular Verbs)", "A1", 2),
    ("simple_past", "단순 과거형 - 의문문과 부정문 (Simple Past: Questions & Negatives)", "A1", 3),

    ("simple_future", "단순 미래형 - Will (Simple Future: Will)", "A1", 1),
    ("simple_future", "단순 미래형 - Going to (Simple Future: Going to)", "A1", 2),

    ("present_continuous", "현재진행형 - 기본 (Present Continuous)", "A1", 1),
    ("present_continuous", "현재진행형 vs 단순현재형 (Present Continuous vs Simple Present)", "A1", 2),

    ("articles", "관사 - A/An (Articles: A/An)", "A1", 1),
    ("articles", "관사 - The (Articles: The)", "A1", 2),

    ("prepositions", "전치사 - 장소와 방향 (Prepositions: Place & Direction)", "A1", 1),
    ("prepositions", "전치사 - 시간 (Prepositions: Time)", "A1", 2),

    ("personal_pronouns", "인칭대명사 (Personal Pronouns)", "A1", 1),
    ("possessive", "소유격 형용사와 대명사 (Possessive Adjectives & Pronouns)", "A1", 1),

    ("imperative", "명령형 (Imperative)", "A1", 1),
    ("there_is_are", "There is / There are (There is / There are)", "A1", 1),

    # A2 초급-중급 (Continuous tenses)
    ("past_continuous", "과거진행형 (Past Continuous)", "A2", 1),
    ("past_continuous", "과거진행형 vs 단순과거형 (Past Continuous vs Simple Past)", "A2", 2),

    ("can_could", "Can / Could - 능력 (Can / Could: Ability)", "A2", 1),
    ("can_could", "Can / Could - 허가와 요청 (Can / Could: Permission & Request)", "A2", 2),

    ("word_order", "기본 어순 (Basic Word Order)", "A2", 1),
    ("word_order", "부사의 위치 (Adverb Position)", "A2", 2),

    ("negation", "부정문 만들기 (Negation)", "A2", 1),
    ("question_formation", "의문문 만들기 - Yes/No (Question Formation: Yes/No)", "A2", 1),
    ("question_formation", "의문문 만들기 - Wh- Questions (Question Formation: Wh-)", "A2", 2),

    # B1 중급 (Perfect tenses, Passive, etc)
    ("present_perfect", "현재완료 - 기본 (Present Perfect: Basic)", "B1", 1),
    ("present_perfect", "현재완료 - 경험과 최근 변화 (Present Perfect: Experience & Recent Changes)", "B1", 2),
    ("present_perfect", "현재완료 vs 단순과거 (Present Perfect vs Simple Past)", "B1", 3),

    ("present_perfect_continuous", "현재완료진행형 (Present Perfect Continuous)", "B1", 1),
    ("present_perfect_continuous", "현재완료진행형 vs 현재완료 (Present Perfect Continuous vs Present Perfect)", "B1", 2),

    ("past_perfect", "과거완료 (Past Perfect)", "B1", 1),
    ("past_perfect", "과거완료 vs 단순과거 (Past Perfect vs Simple Past)", "B1", 2),

    ("infinitive", "부정사 - 기초 (Infinitive: Basic)", "B1", 1),
    ("infinitive", "부정사 - to의 생략 (Infinitive: Bare Infinitive)", "B1", 2),
    ("infinitive", "부정사 - 목적사용 (Infinitive: Purpose)", "B1", 3),

    ("gerund", "동명사 - 기초 (Gerund: Basic)", "B1", 1),
    ("gerund", "동명사 vs 부정사 (Gerund vs Infinitive)", "B1", 2),
    ("gerund", "동명사 - 전치사 이후 (Gerund: After Prepositions)", "B1", 3),

    ("passive_voice", "수동태 - 기본 (Passive Voice: Basic)", "B1", 1),
    ("passive_voice", "수동태 - 시제별 (Passive Voice: Different Tenses)", "B1", 2),
    ("passive_voice", "수동태 - 전치사 (Passive Voice: With Prepositions)", "B1", 3),

    ("conditionals", "가정법 - 1형 (Conditional: First)", "B1", 1),
    ("conditionals", "가정법 - 2형 (Conditional: Second)", "B1", 2),
    ("conditionals", "가정법 - 3형과 Mixed (Conditional: Third & Mixed)", "B1", 3),

    ("relative_clauses", "관계절 - Who/Whom (Relative Clauses: Who/Whom)", "B1", 1),
    ("relative_clauses", "관계절 - Which/That (Relative Clauses: Which/That)", "B1", 2),
    ("relative_clauses", "관계절 - Whose/Where (Relative Clauses: Whose/Where)", "B1", 3),

    ("reported_speech", "간접화법 - 진술 (Reported Speech: Statements)", "B1", 1),
    ("reported_speech", "간접화법 - 질문과 명령 (Reported Speech: Questions & Orders)", "B1", 2),
    ("reported_speech", "간접화법 - 시제 변화 (Reported Speech: Tense Changes)", "B1", 3),

    ("modal_verbs", "조동사 - Must/Have to (Modal Verbs: Must/Have to)", "B1", 1),
    ("modal_verbs", "조동사 - Should/Ought to (Modal Verbs: Should/Ought to)", "B1", 2),
    ("modal_verbs", "조동사 - May/Might (Modal Verbs: May/Might)", "B1", 3),

    ("comparison", "비교 - Comparative (Comparison: Comparative)", "B1", 1),
    ("comparison", "비교 - Superlative (Comparison: Superlative)", "B1", 2),

    ("phrasal_verbs", "구동사 - 기본 (Phrasal Verbs: Basic)", "B1", 1),
    ("phrasal_verbs", "구동사 - Separable (Phrasal Verbs: Separable)", "B1", 2),
    ("phrasal_verbs", "구동사 - Inseparable (Phrasal Verbs: Inseparable)", "B1", 3),

    # B2-C1 고급
    ("inversion", "도치 - 문학적 표현 (Inversion: Literary)", "B2", 1),
    ("inversion", "도치 - 조건절 (Inversion: Conditional)", "B2", 2),

    ("subjunctive", "접속법 (Subjunctive Mood)", "B2", 1),
    ("subjunctive", "접속법 - I suggest/demand (Subjunctive: I suggest/demand)", "B2", 2),

    ("advanced_passive", "수동태 - 고급 (Passive Voice: Advanced)", "B2", 1),

    ("cleft_sentences", "강조 구문 - It is ... that (Cleft Sentences)", "B2", 1),

    ("advanced_articles", "관사 - 고급 (Articles: Advanced)", "B2", 1),

    ("ellipsis", "생략 - 고급 (Ellipsis)", "B2", 1),
]

def generate_entry(topic_id, topic_name, level, part):
    """각 주제별 기본 항목 생성"""
    return {
        "id": f"{topic_id}_{part}",
        "topic": topic_name,
        "level": level,
        "description": f"{topic_name}을 학습합니다.",
        "explanation_ko": "설명이 여기에 들어갑니다.",
        "explanation_en": "Explanation goes here.",
        "examples": [
            {"sentence_en": "Example sentence 1", "sentence_ko": "예시 문장 1"},
            {"sentence_en": "Example sentence 2", "sentence_ko": "예시 문장 2"},
            {"sentence_en": "Example sentence 3", "sentence_ko": "예시 문장 3"}
        ],
        "source": {
            "name": "BBC Learning English",
            "url": f"https://www.bbc.co.uk/learningenglish/"
        },
        "additional_resources": [
            {"name": "Perfect English Grammar", "url": "https://www.perfectenglishgrammar.com/"},
            {"name": "EnglishClub", "url": "https://www.englishclub.com/"},
            {"name": "British Council", "url": "https://learnenglish.britishcouncil.org/"}
        ],
        "quiz": [
            {
                "question": "Quiz question 1?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0,
                "explanation": "Explanation for the answer."
            },
            {
                "question": "Quiz question 2?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 1,
                "explanation": "Explanation for the answer."
            },
            {
                "question": "Quiz question 3?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 2,
                "explanation": "Explanation for the answer."
            }
        ]
    }

if __name__ == "__main__":
    import json

    curriculum = []
    for topic_id, topic_name, level, part in GRAMMAR_TOPICS:
        entry = generate_entry(topic_id, topic_name, level, part)
        curriculum.append(entry)

    print(f"총 {len(curriculum)}개 주제 생성됨")
    print(json.dumps(curriculum[:2], indent=2, ensure_ascii=False))
