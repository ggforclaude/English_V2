from html import escape

from telegram import Update
from telegram.ext import ContextTypes

from db import (
    add_keyword, add_stock, del_keyword, del_stock,
    get_keywords, get_watchlist,
)
from monitors.news import build_news_digest
from monitors.research import build_research_digest


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>개인 투자 봇입니다.</b>\n\n"
        "• 매일 <b>07:00 KST</b> — 키워드·종목 뉴스 갈무리\n"
        "• 매일 <b>08:20 KST</b> — 전체 리서치 보고서\n"
        "• 언제든 자유롭게 질문하면 Claude가 답변\n\n"
        "/help 로 전체 명령어 확인",
        parse_mode="HTML",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 <b>명령어 목록</b>\n\n"
        "<b>즉시 조회</b>\n"
        "/뉴스 — 지금 바로 뉴스 갈무리 (최근 24시간)\n"
        "/리서치 — 지금 바로 리서치 보고서\n"
        "/설정 — 현재 종목·키워드 확인\n\n"
        "<b>키워드 관리</b>\n"
        "/키워드추가 [키워드]\n"
        "/키워드삭제 [키워드]\n\n"
        "<b>종목 관리</b>\n"
        "/종목추가 [이름] [티커] [KR/US]\n"
        "  예) /종목추가 카카오 035720 KR\n"
        "  예) /종목추가 Tesla TSLA US\n"
        "/종목삭제 [티커] [KR/US]\n"
        "  예) /종목삭제 035720 KR\n\n"
        "<b>자유 질문</b>\n"
        "명령어 없이 텍스트 입력 → Claude 답변",
        parse_mode="HTML",
    )


async def cmd_mychatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        f"🪪 Chat ID: <code>{uid}</code>\n.env 파일의 MY_CHAT_ID 에 입력하세요.",
        parse_mode="HTML",
    )


async def cmd_news_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ 뉴스 수집 중...")
    try:
        msgs = await build_news_digest(scheduled=False)
        for msg in msgs:
            await update.message.reply_text(
                msg, parse_mode="HTML", disable_web_page_preview=True
            )
    except Exception as e:
        await update.message.reply_text(f"❌ 오류: {e}")


async def cmd_research_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ 리서치 보고서 수집 중...")
    try:
        msgs = await build_research_digest(scheduled=False)
        for msg in msgs:
            await update.message.reply_text(
                msg, parse_mode="HTML", disable_web_page_preview=True
            )
    except Exception as e:
        await update.message.reply_text(f"❌ 오류: {e}")


async def cmd_add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("사용법: /키워드추가 [키워드]")
        return
    kw = " ".join(context.args)
    if add_keyword(kw):
        await update.message.reply_text(f"✅ 키워드 추가: <b>{escape(kw)}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text(f"이미 존재하는 키워드입니다: {escape(kw)}", parse_mode="HTML")


async def cmd_del_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("사용법: /키워드삭제 [키워드]")
        return
    kw = " ".join(context.args)
    if del_keyword(kw):
        await update.message.reply_text(f"🗑 키워드 삭제: <b>{escape(kw)}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text(f"키워드를 찾을 수 없습니다: {escape(kw)}", parse_mode="HTML")


async def cmd_add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text(
            "사용법: /종목추가 [이름] [티커] [KR/US]\n"
            "예) /종목추가 카카오 035720 KR"
        )
        return
    name, ticker, market = context.args[0], context.args[1].upper(), context.args[2].upper()
    if market not in ("KR", "US"):
        await update.message.reply_text("시장은 KR 또는 US로 입력하세요.")
        return
    if add_stock(name, ticker, market):
        await update.message.reply_text(
            f"✅ 종목 추가: <b>{escape(name)}</b> ({ticker}, {market})", parse_mode="HTML"
        )
    else:
        await update.message.reply_text(f"이미 존재하는 종목입니다: {ticker} ({market})")


async def cmd_del_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "사용법: /종목삭제 [티커] [KR/US]\n"
            "예) /종목삭제 035720 KR"
        )
        return
    ticker, market = context.args[0].upper(), context.args[1].upper()
    if del_stock(ticker, market):
        await update.message.reply_text(f"🗑 종목 삭제: {ticker} ({market})")
    else:
        await update.message.reply_text(f"종목을 찾을 수 없습니다: {ticker} ({market})")


async def cmd_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = get_keywords()
    watchlist = get_watchlist()

    kw_text = "\n".join(f"  • {escape(k)}" for k in keywords) if keywords else "  (없음)"
    kr = [s for s in watchlist if s["market"] == "KR"]
    us = [s for s in watchlist if s["market"] == "US"]
    kr_text = "\n".join(f"  • {escape(s['name'])} ({s['ticker']})" for s in kr) or "  (없음)"
    us_text = "\n".join(f"  • {escape(s['name'])} ({s['ticker']})" for s in us) or "  (없음)"

    await update.message.reply_text(
        f"⚙️ <b>현재 설정</b>\n\n"
        f"<b>뉴스 키워드</b>\n{kw_text}\n\n"
        f"<b>한국 종목</b>\n{kr_text}\n\n"
        f"<b>미국 종목</b>\n{us_text}\n\n"
        f"<b>자동 발송</b>\n"
        f"  • 뉴스: 매일 07:00 KST\n"
        f"  • 리서치: 매일 08:20 KST",
        parse_mode="HTML",
    )
