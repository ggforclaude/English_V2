"""
개인 투자 텔레그램 봇

기능:
  - 매일 07:00 KST: 키워드·종목 뉴스 갈무리 (Google News + Claude 요약)
  - 매일 08:20 KST: 네이버 금융 전체 리서치 보고서
  - 실시간: 자유 질문 → Claude 답변
  - 명령어: /뉴스 /리서치 /키워드추가 /종목추가 등

실행:
  python main.py
"""

import datetime
import logging
import os

import pytz
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from db import init_db
from handlers.chat import handle_message
from handlers.commands import (
    cmd_add_keyword, cmd_add_stock,
    cmd_config, cmd_del_keyword, cmd_del_stock,
    cmd_help, cmd_mychatid, cmd_news_now,
    cmd_research_now, cmd_start,
)
from monitors.news import build_news_digest
from monitors.research import build_research_digest

load_dotenv()
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID", "0"))
KST        = pytz.timezone("Asia/Seoul")


# ── 스케줄 작업 ───────────────────────────────────────────────────────────────

async def _send_msgs(bot, msgs: list[str]):
    for msg in msgs:
        await bot.send_message(
            chat_id=MY_CHAT_ID,
            text=msg,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


async def job_news(context):
    logger.info("뉴스 갈무리 시작")
    await context.bot.send_message(MY_CHAT_ID, "⏳ 뉴스 수집 중...")
    try:
        msgs = await build_news_digest(scheduled=True)
        await _send_msgs(context.bot, msgs)
    except Exception as e:
        logger.exception("뉴스 작업 오류")
        await context.bot.send_message(MY_CHAT_ID, f"❌ 뉴스 오류: {e}")


async def job_research(context):
    logger.info("리서치 보고서 수집 시작")
    await context.bot.send_message(MY_CHAT_ID, "⏳ 리서치 보고서 수집 중...")
    try:
        msgs = await build_research_digest(scheduled=True)
        await _send_msgs(context.bot, msgs)
    except Exception as e:
        logger.exception("리서치 작업 오류")
        await context.bot.send_message(MY_CHAT_ID, f"❌ 리서치 오류: {e}")


# ── 봇 초기화 및 실행 ──────────────────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN 미설정. .env 파일을 확인하세요.")
        return
    if MY_CHAT_ID == 0:
        print("❌ MY_CHAT_ID 미설정. .env 파일을 확인하세요.")
        print("   텔레그램에서 봇에게 /mychatid 를 보내면 ID를 확인할 수 있습니다.")
        return

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # 나 외에는 아무도 명령어 사용 불가
    me = filters.User(user_id=MY_CHAT_ID)

    app.add_handler(CommandHandler("start",      cmd_start,        filters=me))
    app.add_handler(CommandHandler("help",       cmd_help,         filters=me))
    app.add_handler(CommandHandler("mychatid",   cmd_mychatid))        # 누구나 사용 (최초 설정용)
    app.add_handler(CommandHandler("뉴스",        cmd_news_now,     filters=me))
    app.add_handler(CommandHandler("리서치",      cmd_research_now, filters=me))
    app.add_handler(CommandHandler("키워드추가",   cmd_add_keyword,  filters=me))
    app.add_handler(CommandHandler("키워드삭제",   cmd_del_keyword,  filters=me))
    app.add_handler(CommandHandler("종목추가",     cmd_add_stock,    filters=me))
    app.add_handler(CommandHandler("종목삭제",     cmd_del_stock,    filters=me))
    app.add_handler(CommandHandler("설정",        cmd_config,       filters=me))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & me, handle_message)
    )

    # 스케줄 등록
    jq = app.job_queue
    jq.run_daily(job_news,     time=datetime.time(7,  0,  tzinfo=KST), name="news")
    jq.run_daily(job_research, time=datetime.time(8, 20, tzinfo=KST), name="research")

    logger.info(f"✅ 봇 시작 (Chat ID: {MY_CHAT_ID})")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
