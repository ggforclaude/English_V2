"""
자유 질문 핸들러: 일반 텍스트 메시지 → Claude 응답
"""
import asyncio
import os

import anthropic
from telegram import Update
from telegram.ext import ContextTypes

_client: anthropic.Anthropic | None = None

_SYSTEM = (
    "당신은 투자·금융 전문 개인 비서입니다. "
    "주식, 경제, 투자 전략에 관해 명확하고 실용적으로 답변하세요. "
    "최신 실시간 데이터가 필요한 질문에는 지식 한계를 솔직히 밝히세요. "
    "한국어로 답하되 영문 종목명·지표는 그대로 사용하세요."
)


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    return _client


def _ask(question: str) -> str:
    resp = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    return resp.content[0].text


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await update.message.reply_text("🤔 생각 중...")
    try:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, _ask, question)
        # 4096자 제한 분할
        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i : i + 4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Claude 오류: {e}")
