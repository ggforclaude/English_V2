"""
뉴스 갈무리: Google News RSS → 토픽별 수집 → Claude 요약
"""
import asyncio
import os
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import quote

import anthropic
import feedparser

from db import get_keywords, get_watchlist

KST = timezone(timedelta(hours=9))

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    return _client


def _kst_now() -> datetime:
    return datetime.now(KST)


# ── 피드 파싱 (동기, executor에서 실행) ────────────────────────────────────────

def _fetch_feed(url: str, start_utc: datetime, end_utc: datetime) -> list[dict]:
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    results = []
    for entry in feed.entries[:30]:
        try:
            pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            continue
        if not (start_utc <= pub <= end_utc):
            continue
        pub_kst = pub.astimezone(KST)
        results.append({
            "title": entry.title,
            "link": entry.link,
            "published": pub_kst.strftime("%m/%d %H:%M"),
            "source": getattr(getattr(entry, "source", None), "title", ""),
        })
    return results


# ── 전체 수집 ────────────────────────────────────────────────────────────────

async def _collect(start_utc: datetime, end_utc: datetime) -> dict[str, list[dict]]:
    keywords = get_keywords()
    watchlist = get_watchlist()

    # (label, url) 쌍 목록
    queries: list[tuple[str, str]] = []
    for kw in keywords:
        queries.append((kw, f"https://news.google.com/rss/search?q={quote(kw)}&hl=ko&gl=KR&ceid=KR:ko"))
        queries.append((kw, f"https://news.google.com/rss/search?q={quote(kw)}&hl=en&gl=US&ceid=US:en"))
    for s in watchlist:
        if s["market"] == "KR":
            queries.append((
                s["name"],
                f"https://news.google.com/rss/search?q={quote(s['name'])}&hl=ko&gl=KR&ceid=KR:ko",
            ))
        else:
            label = f"{s['name']}({s['ticker']})"
            queries.append((
                label,
                f"https://news.google.com/rss/search?q={quote(s['ticker'])}&hl=en&gl=US&ceid=US:en",
            ))

    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, _fetch_feed, url, start_utc, end_utc)
        for _, url in queries
    ]
    fetched = await asyncio.gather(*tasks)

    results: dict[str, list[dict]] = {}
    for (label, _), articles in zip(queries, fetched):
        if not articles:
            continue
        if label not in results:
            results[label] = []
        seen = {a["title"] for a in results[label]}
        for a in articles:
            if a["title"] not in seen:
                results[label].append(a)
                seen.add(a["title"])

    return results


# ── Claude 요약 (동기, executor에서 실행) ─────────────────────────────────────

def _summarize(articles_by_topic: dict, date_range: str) -> str:
    lines: list[str] = []
    for topic, arts in articles_by_topic.items():
        lines.append(f"=== {topic} ===")
        for a in arts[:5]:
            lines.append(f"[{a['published']}] {a['title']}")
        lines.append("")

    try:
        resp = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=(
                "당신은 투자 뉴스 큐레이터입니다. "
                "수집된 뉴스를 토픽별로 핵심 1~2줄씩 한국어로 요약하세요. "
                "전체 250자 이내로 간결하게 작성하세요."
            ),
            messages=[{
                "role": "user",
                "content": f"기간: {date_range}\n\n" + "\n".join(lines),
            }],
        )
        return resp.content[0].text
    except Exception as e:
        return f"요약 생성 오류: {e}"


# ── 메시지 분할 ───────────────────────────────────────────────────────────────

def _split(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        idx = text.rfind("\n", 0, limit)
        if idx == -1:
            idx = limit
        parts.append(text[:idx])
        text = text[idx:].lstrip("\n")
    return parts


# ── 공개 인터페이스 ───────────────────────────────────────────────────────────

async def build_news_digest(scheduled: bool = False) -> list[str]:
    """
    scheduled=True : 어제 07:00 KST ~ 오늘 07:00 KST  (자동 발송용)
    scheduled=False: 지금 기준 24시간 전 ~ 지금         (수동 호출용)
    """
    now = _kst_now()

    if scheduled:
        end_kst = now.replace(hour=7, minute=0, second=0, microsecond=0)
    else:
        end_kst = now

    start_kst = end_kst - timedelta(hours=24)
    start_utc = start_kst.astimezone(timezone.utc)
    end_utc   = end_kst.astimezone(timezone.utc)
    date_range = f"{start_kst.strftime('%m/%d %H:%M')} ~ {end_kst.strftime('%m/%d %H:%M')} KST"

    articles = await _collect(start_utc, end_utc)

    if not articles:
        return [f"📰 <b>뉴스 갈무리</b>\n<i>{date_range}</i>\n\n수집된 뉴스가 없습니다."]

    header = f"📰 <b>뉴스 갈무리</b>\n<i>{date_range}</i>\n"
    body: list[str] = []
    for topic, arts in articles.items():
        body.append(f"\n<b>[{escape(topic)}]</b>")
        for a in arts[:4]:
            src = (
                f" <i>({escape(a['source'])}, {a['published']})</i>"
                if a["source"]
                else f" <i>({a['published']})</i>"
            )
            body.append(f'• <a href="{a["link"]}">{escape(a["title"])}</a>{src}')

    loop = asyncio.get_event_loop()
    summary = await loop.run_in_executor(None, _summarize, articles, date_range)
    footer = f"\n\n📊 <b>AI 요약</b>\n{escape(summary)}"

    return _split(header + "\n".join(body) + footer)
