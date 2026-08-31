"""
영어 문법 커리큘럼
매일 다른 주제의 다른 회차를 제시합니다.
같은 주제가 연달아 나오지 않도록 설계되었습니다.
"""

GRAMMAR_CURRICULUM = [
    # 1. 부정사 (Infinitives)
    {
        "id": "infinitive_1",
        "topic": "부정사 기초 (Infinitive Basics)",
        "level": "B1",
        "description": "부정사의 기본 개념과 형태를 이해합니다. 부정사는 'to + 동사원형' 형태로 명사, 형용사, 부사로 기능합니다.",
        "explanation_ko": "부정사(Infinitive)는 동사의 기본형으로, 'to + 동사'의 형태입니다. 문장에서 명사, 형용사, 부사의 역할을 할 수 있습니다.",
        "examples": [
            {"sentence_en": "I want to learn English.", "sentence_ko": "나는 영어를 배우고 싶다."},
            {"sentence_en": "She has a lot of work to do.", "sentence_ko": "그녀는 해야 할 일이 많다."},
            {"sentence_en": "To succeed, you must study hard.", "sentence_ko": "성공하려면, 당신은 열심히 공부해야 한다."}
        ],
        "source": {
            "name": "BBC Learning English",
            "url": "https://www.bbc.co.uk/learningenglish/english/course/intermediate/unit-27/session-1"
        },
        "additional_resources": [
            {"name": "Grammarly Blog - Infinitive", "url": "https://www.grammarly.com/blog/infinitive/"},
            {"name": "Oxford English - Infinitive", "url": "https://www.oxfordlearnersdictionaries.com/definition/english/infinitive"},
            {"name": "EnglishClub.com - Infinitive", "url": "https://www.englishclub.com/grammar/verbs/infinitive.htm"}
        ],
        "quiz": [
            {
                "question": "다음 문장에서 부정사는?",
                "options": ["to learn", "learning", "learned", "learns"],
                "correct": 0,
                "explanation": "'to learn'은 부정사입니다. 'to + 동사원형' 형태입니다."
            },
            {
                "question": "부정사의 역할로 맞는 것은?",
                "options": ["명사, 형용사, 부사만 가능", "명사, 형용사, 부사 모두 가능", "동사만 가능", "명사만 가능"],
                "correct": 1,
                "explanation": "부정사는 문장에서 명사, 형용사, 부사의 역할을 모두 할 수 있습니다."
            },
            {
                "question": "'I want to go home'에서 부정사의 역할은?",
                "options": ["형용사", "명사", "부사", "동사"],
                "correct": 1,
                "explanation": "'to go'는 'want'의 목적어로 기능하므로 명사의 역할을 합니다."
            }
        ]
    },

    # 2. 동명사 (Gerunds)
    {
        "id": "gerund_1",
        "topic": "동명사 기초 (Gerund Basics)",
        "level": "B1",
        "description": "동명사는 '동사 + -ing' 형태로 명사처럼 사용되는 동사입니다. 주어, 목적어, 전치사의 목적어로 사용됩니다.",
        "explanation_ko": "동명사는 '동사 + -ing' 형태로, 문장에서 명사처럼 기능합니다. 주어, 목적어, 전치사의 목적어로 사용됩니다.",
        "examples": [
            {"sentence_en": "Reading books is my hobby.", "sentence_ko": "책 읽기는 내 취미이다."},
            {"sentence_en": "I enjoy playing tennis.", "sentence_ko": "나는 테니스 치기를 즐긴다."},
            {"sentence_en": "She is interested in learning languages.", "sentence_ko": "그녀는 언어 배우기에 관심이 있다."}
        ],
        "source": {
            "name": "Cambridge English",
            "url": "https://dictionary.cambridge.org/grammar/british-grammar/gerunds-ing-forms-used-as-nouns"
        },
        "additional_resources": [
            {"name": "British Council - Gerunds", "url": "https://learnenglish.britishcouncil.org/grammar/intermediate-grammar/gerunds-ing-forms"},
            {"name": "Perfect English Grammar - Gerund", "url": "https://www.perfectenglishgrammar.com/gerund.html"},
            {"name": "Khan Academy - Gerunds", "url": "https://www.khanacademy.org/humanities/grammar/parts-of-speech-101/gerunds-and-participles/v/gerunds"}
        ],
        "quiz": [
            {
                "question": "동명사는 어떤 형태인가?",
                "options": ["동사 + -ed", "동사 + -ing", "to + 동사", "동사 + -s"],
                "correct": 1,
                "explanation": "동명사는 '동사 + -ing' 형태입니다."
            },
            {
                "question": "'Swimming is good for health'에서 동명사는?",
                "options": ["is", "good", "swimming", "health"],
                "correct": 2,
                "explanation": "'swimming'은 동명사로 주어의 역할을 합니다."
            },
            {
                "question": "'I like eating apples'에서 동명사의 역할은?",
                "options": ["주어", "동사", "목적어", "형용사"],
                "correct": 2,
                "explanation": "'eating'은 'like'의 목적어로 기능하므로 명사의 역할을 합니다."
            }
        ]
    },

    # 3. 가정법 (Conditional)
    {
        "id": "conditional_1",
        "topic": "가정법 제1형 (First Conditional)",
        "level": "B1",
        "description": "가정법 제1형은 실현 가능한 미래 상황을 나타냅니다. 'If + 현재형, will + 동사' 구조입니다.",
        "explanation_ko": "가정법 제1형은 'If + 현재형, will + 동사'의 구조로, 실현 가능성이 높은 미래 상황을 표현합니다.",
        "examples": [
            {"sentence_en": "If it rains, I will stay home.", "sentence_ko": "만약 비가 오면, 나는 집에 있을 것이다."},
            {"sentence_en": "If you study hard, you will pass the exam.", "sentence_ko": "만약 당신이 열심히 공부하면, 당신은 시험을 통과할 것이다."},
            {"sentence_en": "If she calls me, I will answer.", "sentence_ko": "만약 그녀가 나에게 전화하면, 나는 받을 것이다."}
        ],
        "source": {
            "name": "BBC Learning English",
            "url": "https://www.bbc.co.uk/learningenglish/english/course/intermediate/unit-33/session-1"
        },
        "additional_resources": [
            {"name": "British Council - Conditionals", "url": "https://learnenglish.britishcouncil.org/grammar/intermediate-grammar/conditionals"},
            {"name": "Perfect English Grammar - First Conditional", "url": "https://www.perfectenglishgrammar.com/first-conditional.html"},
            {"name": "English Grammar Online - Conditionals", "url": "https://www.englishgrammar.org/conditionals/"}
        ],
        "quiz": [
            {
                "question": "가정법 제1형의 구조는?",
                "options": ["If + 현재형, would + 동사", "If + 현재형, will + 동사", "If + 과거형, would + 동사", "If + will + 동사, 현재형"],
                "correct": 1,
                "explanation": "가정법 제1형은 'If + 현재형, will + 동사' 구조입니다."
            },
            {
                "question": "'If you go there, you will see...'의 의미는?",
                "options": ["현재 상황", "실현 가능성 높은 미래", "실현 불가능한 미래", "과거 상황"],
                "correct": 1,
                "explanation": "가정법 제1형은 실현 가능성이 높은 미래 상황을 나타냅니다."
            },
            {
                "question": "다음 중 가정법 제1형을 올바르게 표현한 것은?",
                "options": ["If it will rain, I stay home.", "If it rains, I will stay home.", "If it rained, I would stay home.", "If it will rain, I would stay home."],
                "correct": 1,
                "explanation": "'If it rains, I will stay home.'이 올바른 가정법 제1형 표현입니다."
            }
        ]
    },

    # 4. 수동태 (Passive Voice)
    {
        "id": "passive_1",
        "topic": "수동태 기초 (Passive Voice Basics)",
        "level": "B1",
        "description": "수동태는 행동의 대상이 주어가 되는 문장 구조입니다. 'be + 과거분사'의 형태입니다.",
        "explanation_ko": "수동태는 행동의 대상(object)이 주어(subject)가 되는 문장 구조입니다. 'be + 과거분사' 형태로 표현됩니다.",
        "examples": [
            {"sentence_en": "The letter was written by John.", "sentence_ko": "그 편지는 John에 의해 쓰여졌다."},
            {"sentence_en": "English is spoken in many countries.", "sentence_ko": "영어는 많은 국가에서 말해진다."},
            {"sentence_en": "The cake was baked by my mother.", "sentence_ko": "그 케이크는 내 어머니에 의해 구워졌다."}
        ],
        "source": {
            "name": "Cambridge English",
            "url": "https://dictionary.cambridge.org/grammar/british-grammar/passive"
        },
        "additional_resources": [
            {"name": "BBC Learning English - Passive", "url": "https://www.bbc.co.uk/learningenglish/english/course/intermediate/unit-24/session-1"},
            {"name": "Perfect English Grammar - Passive Voice", "url": "https://www.perfectenglishgrammar.com/passive-voice.html"},
            {"name": "Oxford English - Passive Voice", "url": "https://www.oxfordlearnersdictionaries.com/definition/english/passive_voice"}
        ],
        "quiz": [
            {
                "question": "수동태의 기본 구조는?",
                "options": ["주어 + 동사 + 목적어", "be + 과거분사", "동사 + 주어 + 목적어", "목적어 + be + 동사"],
                "correct": 1,
                "explanation": "수동태는 'be + 과거분사' 구조입니다."
            },
            {
                "question": "'The door was opened by the manager'에서 행동의 주체는?",
                "options": ["The door", "was opened", "the manager", "by"],
                "correct": 2,
                "explanation": "'the manager'가 행동의 주체(by 뒤에 옴)입니다."
            },
            {
                "question": "능동태 'John built the house'를 수동태로 바꾸면?",
                "options": ["The house was built by John.", "John was built the house.", "The house built by John.", "Built the house was by John."],
                "correct": 0,
                "explanation": "'The house was built by John.'이 올바른 수동태 표현입니다."
            }
        ]
    },

    # 5. 과거완료 (Past Perfect)
    {
        "id": "past_perfect_1",
        "topic": "과거완료 기초 (Past Perfect Basics)",
        "level": "B1",
        "description": "과거완료는 과거의 두 사건 중 먼저 일어난 일을 표현합니다. 'had + 과거분사' 형태입니다.",
        "explanation_ko": "과거완료는 'had + 과거분사' 형태로, 과거의 두 사건 중 더 먼저 일어난 일을 나타냅니다.",
        "examples": [
            {"sentence_en": "When I arrived, he had already left.", "sentence_ko": "내가 도착했을 때, 그는 이미 떠났다."},
            {"sentence_en": "She had finished her homework before she went out.", "sentence_ko": "그녀는 나가기 전에 숙제를 끝냈다."},
            {"sentence_en": "By the time we got there, the movie had started.", "sentence_ko": "우리가 거기에 도착했을 때, 영화는 시작되었다."}
        ],
        "source": {
            "name": "British Council",
            "url": "https://learnenglish.britishcouncil.org/grammar/intermediate-grammar/past-perfect"
        },
        "additional_resources": [
            {"name": "Perfect English Grammar - Past Perfect", "url": "https://www.perfectenglishgrammar.com/past-perfect.html"},
            {"name": "BBC Learning English - Past Perfect", "url": "https://www.bbc.co.uk/learningenglish/english/course/intermediate/unit-26/session-1"},
            {"name": "Khan Academy - Past Perfect", "url": "https://www.khanacademy.org/humanities/grammar/parts-of-speech-101/complex-verb-tenses/v/past-perfect-tense"}
        ],
        "quiz": [
            {
                "question": "과거완료의 구조는?",
                "options": ["had + 현재분사", "had + 과거분사", "have + 과거분사", "has + 과거분사"],
                "correct": 1,
                "explanation": "과거완료는 'had + 과거분사' 형태입니다."
            },
            {
                "question": "'When I arrived, he had left.'의 의미는?",
                "options": ["동시에 일어난 두 사건", "먼저 일어난 사건이 clear함", "미래의 일", "현재의 상황"],
                "correct": 1,
                "explanation": "과거완료는 과거의 두 사건 중 먼저 일어난 일을 명확하게 보여줍니다."
            },
            {
                "question": "다음 중 과거완료를 올바르게 표현한 것은?",
                "options": ["He had go there.", "He had went there.", "He had gone there.", "He was gone there."],
                "correct": 2,
                "explanation": "'He had gone there.'가 올바른 과거완료 표현입니다."
            }
        ]
    },

    # 6. 현재완료 (Present Perfect)
    {
        "id": "present_perfect_1",
        "topic": "현재완료 기초 (Present Perfect Basics)",
        "level": "B1",
        "description": "현재완료는 과거에 시작된 일이 현재와 관련이 있는 경우를 나타냅니다. 'have/has + 과거분사' 형태입니다.",
        "explanation_ko": "현재완료는 'have/has + 과거분사' 형태로, 과거에 시작된 일이 현재까지 영향을 미치거나 계속되는 것을 나타냅니다.",
        "examples": [
            {"sentence_en": "I have lived here for 5 years.", "sentence_ko": "나는 여기에 5년 동안 살고 있다."},
            {"sentence_en": "She has finished her project.", "sentence_ko": "그녀는 그녀의 프로젝트를 끝냈다."},
            {"sentence_en": "Have you ever been to Paris?", "sentence_ko": "당신은 파리에 가본 적이 있나?"}
        ],
        "source": {
            "name": "BBC Learning English",
            "url": "https://www.bbc.co.uk/learningenglish/english/course/intermediate/unit-22/session-1"
        },
        "additional_resources": [
            {"name": "Perfect English Grammar - Present Perfect", "url": "https://www.perfectenglishgrammar.com/present-perfect.html"},
            {"name": "British Council - Present Perfect", "url": "https://learnenglish.britishcouncil.org/grammar/intermediate-grammar/present-perfect"},
            {"name": "EnglishClub - Present Perfect", "url": "https://www.englishclub.com/grammar/verb-tense/present-perfect.htm"}
        ],
        "quiz": [
            {
                "question": "현재완료의 구조는?",
                "options": ["have/has + 현재형", "have/has + 과거분사", "had + 과거분사", "will have + 동사"],
                "correct": 1,
                "explanation": "현재완료는 'have/has + 과거분사' 형태입니다."
            },
            {
                "question": "'I have lived here for 5 years'의 의미는?",
                "options": ["과거 5년 동안", "현재 5년 동안 계속 살고 있음", "5년 후에 살 것", "5년 전에 살았음"],
                "correct": 1,
                "explanation": "현재완료는 과거에 시작되어 현재까지 계속되는 상황을 나타냅니다."
            },
            {
                "question": "다음 중 현재완료를 올바르게 표현한 것은?",
                "options": ["She has go there.", "She has gone there.", "She is gone there.", "She went there yet."],
                "correct": 1,
                "explanation": "'She has gone there.'가 올바른 현재완료 표현입니다."
            }
        ]
    }
]

def get_today_grammar(day_number: int) -> dict:
    """날짜 기반으로 오늘의 문법 주제를 선택합니다.

    커리큘럼을 다양하게 순환하면서 같은 주제가 연달아 나오지 않도록 합니다.
    """
    # 문법 주제를 균형있게 분산
    index = (day_number - 1) % len(GRAMMAR_CURRICULUM)
    return GRAMMAR_CURRICULUM[index].copy()
