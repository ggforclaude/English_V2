"""
발음 평가 페이지 생성
/today/pronunciation 페이지를 빌드합니다.
단어 + 문장으로 발음 연습
"""
import pathlib
import json
from datetime import date


def build_pronunciation_page(today: date, daily_words: dict) -> str:
    """발음 페이지 생성."""
    page_path = _save_pronunciation_html(today=today, daily_words=daily_words)
    return page_path


def _save_pronunciation_html(today: date, daily_words: dict) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "pronunciation"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    words = daily_words.get("words", [])
    words_json = json.dumps(words, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="/English_V2/">
    <title>발음 평가 - Improve English</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
            margin-bottom: 10px;
        }}

        .instructions {{
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }}

        .content {{
            padding: 40px;
        }}

        .intro {{
            background: #fff5f7;
            border-left: 4px solid #f5576c;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            color: #333;
            line-height: 1.6;
        }}

        .intro-title {{
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 10px;
        }}

        /* 탭 스타일 */
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
        }}

        .tab-btn {{
            padding: 12px 24px;
            border: none;
            background: none;
            cursor: pointer;
            font-weight: bold;
            font-size: 1em;
            color: #999;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}

        .tab-btn.active {{
            color: #f5576c;
            border-bottom-color: #f5576c;
        }}

        .tab-btn:hover {{
            color: #f5576c;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* 카드 그리드 */
        .practice-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .practice-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            transition: all 0.3s;
            cursor: pointer;
        }}

        .practice-card:hover {{
            border-color: #f5576c;
            box-shadow: 0 5px 20px rgba(245, 87, 108, 0.15);
        }}

        .card-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 10px;
        }}

        .card-subtitle {{
            font-size: 0.9em;
            color: #999;
            margin-bottom: 15px;
            font-style: italic;
        }}

        .card-content {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.6;
            color: #555;
            min-height: 60px;
        }}

        .button-group {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }}

        .btn {{
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9em;
            transition: all 0.3s;
        }}

        .btn-record {{
            background: #f5576c;
            color: white;
        }}

        .btn-record:hover {{
            background: #d63447;
        }}

        .btn-record.recording {{
            background: #dc3545;
            animation: pulse 1s infinite;
        }}

        .btn-play {{
            background: #667eea;
            color: white;
        }}

        .btn-play:hover {{
            background: #5568d3;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}

        .status {{
            font-size: 0.85em;
            color: #999;
            text-align: center;
            margin-bottom: 10px;
        }}

        .result {{
            background: #f0f8f7;
            border-left: 4px solid #38ef7d;
            padding: 12px;
            border-radius: 4px;
            font-size: 0.85em;
            color: #28a745;
            display: none;
        }}

        .result.active {{
            display: block;
        }}

        /* 통계 */
        .summary {{
            background: #fff8f0;
            border-left: 4px solid #f5576c;
            padding: 25px;
            border-radius: 8px;
            margin-top: 30px;
        }}

        .summary-title {{
            font-weight: bold;
            color: #f5576c;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}

        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}

        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #f5576c;
        }}

        .stat-label {{
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }}

        .navigation {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}

        .nav-button {{
            display: inline-block;
            padding: 12px 30px;
            margin: 0 10px;
            background: #f5576c;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #d63447;
        }}

        @media (max-width: 768px) {{
            .content {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .practice-grid {{
                grid-template-columns: 1fr;
            }}

            .summary-stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 발음 평가</h1>
            <p>오늘의 단어와 문장으로 발음을 연습하세요</p>
            <div class="instructions">
                🎙️ 마이크 권한이 필요합니다 | 조용한 환경 권장
            </div>
        </div>

        <div class="content">
            <div class="intro">
                <div class="intro-title">📝 발음 연습 방법</div>
                1. 단어를 클릭하면 원어민 발음이 재생됩니다<br>
                2. "🎤 녹음하기" 버튼을 누르고 천천히 발음해보세요<br>
                3. 녹음이 끝나면 자동으로 인식됩니다<br>
                4. 반복해서 연습하고 정확도를 높이세요
            </div>

            <!-- 탭 -->
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('words')">📝 단어 연습</button>
                <button class="tab-btn" onclick="switchTab('sentences')">📄 문장 연습</button>
            </div>

            <!-- 단어 탭 -->
            <div id="words" class="tab-content active">
                <div class="practice-grid" id="wordsContainer"></div>
            </div>

            <!-- 문장 탭 -->
            <div id="sentences" class="tab-content">
                <div class="practice-grid" id="sentencesContainer"></div>
            </div>

            <!-- 통계 -->
            <div class="summary">
                <div class="summary-title">📊 오늘의 연습 현황</div>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-number" id="totalItems">0</div>
                        <div class="stat-label">총 항목</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="recordedItems">0</div>
                        <div class="stat-label">녹음한 항목</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="avgScore">0%</div>
                        <div class="stat-label">평균 정확도</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="navigation">
            <a href="today/words" class="nav-button">← 단어로</a>
            <a href="today" class="nav-button">홈 →</a>
        </div>
    </div>

    <script>
        const wordsData = {words_json};
        let recordingStats = {{}};
        let currentTab = 'words';

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const synth = window.speechSynthesis;

        function switchTab(tab) {{
            currentTab = tab;
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            document.querySelector(`[onclick="switchTab('${{tab}}'"]`).classList.add('active');
            updateStats();
        }}

        function renderPracticeCards() {{
            if (!wordsData || wordsData.length === 0) {{
                document.getElementById('wordsContainer').innerHTML = '<p style="text-align: center; color: #999;">단어 데이터를 불러올 수 없습니다.</p>';
                document.getElementById('sentencesContainer').innerHTML = '<p style="text-align: center; color: #999;">문장 데이터를 불러올 수 없습니다.</p>';
                return;
            }}

            // 단어 카드
            const wordsContainer = document.getElementById('wordsContainer');
            wordsContainer.innerHTML = '';
            wordsData.forEach((word, idx) => {{
                const card = createCard(word.word, word.pronunciation || '', word.meaning_ko || '', 'word', idx);
                wordsContainer.appendChild(card);
                recordingStats[`word_${{idx}}`] = {{ recorded: false, score: 0 }};
            }});

            // 문장 카드
            const sentencesContainer = document.getElementById('sentencesContainer');
            sentencesContainer.innerHTML = '';
            wordsData.forEach((word, idx) => {{
                if (word.example_en) {{
                    const card = createCard(word.example_en, '', word.example_en, 'sentence', idx);
                    sentencesContainer.appendChild(card);
                    recordingStats[`sentence_${{idx}}`] = {{ recorded: false, score: 0 }};
                }}
            }});

            document.getElementById('totalItems').textContent = wordsData.length * 2;
            updateStats();
        }}

        function createCard(text, pronunciation, meaning, type, idx) {{
            const card = document.createElement('div');
            card.className = 'practice-card';
            const id = `${{type}}_${{idx}}`;

            card.innerHTML = `
                <div class="card-title" onclick="playText('${{text}}')">${{text}}</div>
                <div class="card-subtitle">${{type === 'word' ? '단어' : '문장'}}</div>
                ${{pronunciation ? `<div class="card-subtitle">${{pronunciation}}</div>` : ''}}
                ${{meaning && type === 'word' ? `<div class="card-content">${{meaning}}</div>` : `<div class="card-content">${{text}}</div>`}}
                <div class="button-group">
                    <button class="btn btn-record" onclick="startRecording('${{id}}', this, '${{text}}')" data-text="${{text}}">
                        🎤 녹음하기
                    </button>
                    <button class="btn btn-play" onclick="playText('${{text}}')">
                        🔊 표준발음
                    </button>
                </div>
                <div class="button-group">
                    <button class="btn btn-play" id="playback_${{id}}" onclick="playRecording('${{id}}')" style="display:none;">
                        🎙️ 내 발음 듣기
                    </button>
                </div>
                <div class="status" data-id="${{id}}"></div>
                <div class="result" data-id="${{id}}"></div>
            `;

            return card;
        }}

        function playText(text) {{
            if (!synth) {{
                alert('브라우저가 음성 재생을 지원하지 않습니다');
                return;
            }}

            synth.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.8;
            synth.speak(utterance);
        }}

        let mediaRecorder;
        let audioChunks = {{}};

        function startRecording(id, button, text) {{
            if (!SpeechRecognition) {{
                alert('Chrome, Edge, Safari를 사용해주세요.');
                return;
            }}

            button.textContent = '🎙️ 녹음 중...';
            button.classList.add('recording');
            button.disabled = true;

            const statusEl = document.querySelector(`[data-id="${{id}}"].status`);
            statusEl.textContent = '듣고 있습니다...';

            // MediaRecorder로 실제 음성 녹음
            navigator.mediaDevices.getUserMedia({{ audio: true }})
                .then(stream => {{
                    audioChunks[id] = [];
                    mediaRecorder = new MediaRecorder(stream);

                    mediaRecorder.ondataavailable = (event) => {{
                        audioChunks[id].push(event.data);
                    }};

                    mediaRecorder.onstop = () => {{
                        stream.getTracks().forEach(track => track.stop());
                    }};

                    mediaRecorder.start();

                    // SpeechRecognition으로 음성 인식
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'en-US';
                    recognition.continuous = false;

                    recognition.onresult = (event) => {{
                        let recognized = '';
                        for (let i = event.resultIndex; i < event.results.length; i++) {{
                            recognized += event.results[i][0].transcript;
                        }}

                        const score = calculateSimilarity(text.toLowerCase(), recognized.toLowerCase());
                        recordingStats[id].recorded = true;
                        recordingStats[id].score = score;

                        const resultEl = document.querySelector(`[data-id="${{id}}"].result`);
                        resultEl.classList.add('active');
                        resultEl.innerHTML = `✅ 인식: "${{recognized}}" | 정확도: ${{score}}%`;
                        statusEl.textContent = score >= 80 ? '🎉 좋습니다!' : '다시 시도해보세요';

                        mediaRecorder.stop();

                        // "내 발음 듣기" 버튼 표시
                        const playbackBtn = document.getElementById(`playback_${{id}}`);
                        if (playbackBtn) {{
                            playbackBtn.style.display = 'block';
                        }}

                        updateStats();
                    }};

                    recognition.onerror = () => {{
                        statusEl.textContent = '❌ 인식 실패. 다시 시도하세요.';
                        mediaRecorder.stop();
                    }};

                    recognition.onend = () => {{
                        button.textContent = '🎤 녹음하기';
                        button.classList.remove('recording');
                        button.disabled = false;
                    }};

                    recognition.start();
                }})
                .catch(error => {{
                    statusEl.textContent = '❌ 마이크 접근 권한 필요';
                    button.textContent = '🎤 녹음하기';
                    button.classList.remove('recording');
                    button.disabled = false;
                }});
        }}

        function playRecording(id) {{
            if (!audioChunks[id] || audioChunks[id].length === 0) {{
                alert('녹음된 음성이 없습니다.');
                return;
            }}

            const audioBlob = new Blob(audioChunks[id], {{ type: 'audio/wav' }});
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
        }}

        function calculateSimilarity(target, recognized) {{
            const words = recognized.split(' ');
            for (let word of words) {{
                if (word.includes(target) || target.includes(word)) {{
                    return 100;
                }}
            }}

            let score = 0;
            for (let i = 0; i < Math.min(target.length, recognized.length); i++) {{
                if (target[i] === recognized[i]) score++;
            }}
            score = Math.round((score / target.length) * 100);
            return Math.max(0, Math.min(100, score));
        }}

        function updateStats() {{
            let recordedCount = 0;
            let totalScore = 0;
            let scoredCount = 0;

            for (let id in recordingStats) {{
                if (recordingStats[id].recorded) {{
                    recordedCount++;
                    totalScore += recordingStats[id].score;
                    scoredCount++;
                }}
            }}

            document.getElementById('recordedItems').textContent = recordedCount;
            if (scoredCount > 0) {{
                const avgScore = Math.round(totalScore / scoredCount);
                document.getElementById('avgScore').textContent = avgScore + '%';
            }}
        }}

        // 초기화
        renderPracticeCards();
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
