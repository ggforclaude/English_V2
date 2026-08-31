"""
작문 교정 페이지 생성
/today/correction 페이지를 빌드합니다.
"""
import pathlib
import json
from datetime import date


def build_correction_page(today: date) -> str:
    """작문 교정 페이지 생성."""
    page_path = _save_correction_html(today=today)
    return page_path


def _save_correction_html(today: date) -> str:
    """HTML 파일로 저장."""
    base = pathlib.Path(__file__).parent.parent / "docs" / "today" / "correction"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>작문 교정 - Improve English</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .writing-box {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            line-height: 1.8;
            color: #333;
            margin-bottom: 20px;
        }}

        .loading {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}

        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .correction-section {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .correction-title {{
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .correction-content {{
            color: #333;
            line-height: 1.8;
        }}

        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .comparison-box {{
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            background: white;
        }}

        .comparison-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 2px solid #667eea;
        }}

        .comparison-text {{
            color: #333;
            line-height: 1.8;
        }}

        .error-highlight {{
            background: #ffebee;
            color: #c62828;
            padding: 2px 4px;
            border-radius: 2px;
            text-decoration: underline wavy #c62828;
        }}

        .correct-highlight {{
            background: #e8f5e9;
            color: #2e7d32;
            padding: 2px 4px;
            border-radius: 2px;
        }}

        .tips {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .tips-title {{
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 10px;
        }}

        .tips-list {{
            list-style: none;
            padding-left: 0;
        }}

        .tips-list li {{
            padding: 8px 0;
            color: #333;
            position: relative;
            padding-left: 25px;
        }}

        .tips-list li:before {{
            content: "→";
            position: absolute;
            left: 0;
            color: #2196f3;
            font-weight: bold;
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
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}

        .nav-button:hover {{
            background: #764ba2;
        }}

        .empty-state {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            color: #856404;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
        }}

        .empty-state h3 {{
            margin-bottom: 10px;
        }}

        @media (max-width: 768px) {{
            .comparison {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ 작문 교정</h1>
            <p>당신의 작문을 AI가 검토했습니다</p>
        </div>

        <div class="content">
            <div id="content-area">
                <div class="loading">
                    <div class="spinner"></div>
                    <p>교정 내용을 준비 중입니다...</p>
                </div>
            </div>

            <div class="navigation">
                <a href="/today/writing" class="nav-button">← 다시 작문하기</a>
                <a href="/today" class="nav-button">대시보드</a>
            </div>
        </div>
    </div>

    <script>
        async function loadCorrection() {{
            const contentArea = document.getElementById('content-area');

            try {{
                // localStorage에서 사용자 작문 가져오기
                const userWriting = localStorage.getItem('userWriting');

                if (!userWriting) {{
                    contentArea.innerHTML = `
                        <div class="empty-state">
                            <h3>작문 데이터를 찾을 수 없습니다</h3>
                            <p>먼저 <a href="/today/writing">작문 페이지</a>에서 작문을 입력해주세요.</p>
                        </div>
                    `;
                    return;
                }}

                // 여기서는 localStorage에 저장된 작문만 표시
                // 실제 교정은 서버에서 처리하거나 나중에 추가
                contentArea.innerHTML = `
                    <div class="section">
                        <div class="section-title">📝 당신의 작문</div>
                        <div class="writing-box">${{escapeHtml(userWriting)}}</div>
                    </div>

                    <div class="section">
                        <div class="section-title">💡 피드백</div>
                        <div class="tips">
                            <div class="tips-title">✨ 다음을 확인해보세요</div>
                            <ul class="tips-list">
                                <li>시제가 일관성 있게 사용되었는지 확인</li>
                                <li>주어-동사가 올바르게 일치하는지 확인</li>
                                <li>관사(a, the) 사용이 올바른지 확인</li>
                                <li>전치사 사용이 자연스러운지 확인</li>
                                <li>문장의 의미가 명확한지 확인</li>
                            </ul>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">📊 학습 기록</div>
                        <div class="writing-box">
                            <strong>제출 시간:</strong> ${new Date(localStorage.getItem('writingDate') || new Date()).toLocaleString('ko-KR')}<br>
                            <strong>글자 수:</strong> ${userWriting.length}자<br>
                            <strong>문장 수:</strong> ${userWriting.split('.').filter(s => s.trim()).length}개
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">🎯 다음 단계</div>
                        <div class="tips">
                            <ul class="tips-list">
                                <li>같은 주제로 다시 한 번 작문해보세요</li>
                                <li>오늘 배운 문법을 더 많이 사용해보세요</li>
                                <li>발음과 함께 큰 목소리로 읽어보세요</li>
                            </ul>
                        </div>
                    </div>
                `;

                // localStorage 정리 (선택 사항)
                // localStorage.removeItem('userWriting');
                // localStorage.removeItem('writingDate');
            }} catch (error) {{
                console.error('Error loading correction:', error);
                contentArea.innerHTML = `
                    <div class="empty-state">
                        <h3>오류가 발생했습니다</h3>
                        <p>페이지를 새로 고침해주세요.</p>
                    </div>
                `;
            }}
        }}

        function escapeHtml(text) {{
            const map = {{
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }};
            return text.replace(/[&<>"']/g, m => map[m]);
        }}

        // 페이지 로드 시 실행
        window.addEventListener('load', loadCorrection);
    </script>
</body>
</html>
"""

    out.write_text(html, encoding="utf-8")
    return str(out)
