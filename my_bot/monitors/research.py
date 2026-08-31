"""
리서치 보고서: 네이버 금융 기업 분석 리스트 스크래핑
https://finance.naver.com/research/company_list.naver

실제 컬럼 구조 (tds 인덱스):
  0: 종목명  1: 제목  2: 증권사  3: 첨부(PDF)  4: 작성일  5: 조회수
목표주가 컬럼은 없음 → 제목 텍스트에서 정규식으로 추출
"""
import asyncio
import re
from datetime import datetime, timedelta
from html import escape

import aiohttp
import pytz
from bs4 import BeautifulSoup

# 제목에서 목표주가 추출: "목표주가 105,000원", "TP 88,000원", "목표가 40,000원으로" 등
_TP_RE = re.compile(r'(?:목표주가|목표가|TP)\s*[:\s→↑↓]?\s*([0-9,]+)\s*원?')

KST = pytz.timezone("Asia/Seoul")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.naver.com/research/",
}


# ── 단일 페이지 파싱 ───────────────────────────────────────────────────────────

async def _scrape_page(session: aiohttp.ClientSession, page: int) -> tuple[list[dict], bool]:
    """
    Returns (reports_on_page, should_stop).
    should_stop=True when we hit rows older than the window or table is missing.
    """
    url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            raw = await resp.read()
        html = raw.decode("euc-kr", errors="replace")
    except Exception as e:
        print(f"[research] page {page} 요청 오류: {e}")
        return [], True

    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.type_1")
    if not table:
        return [], True

    reports: list[dict] = []
    for row in table.select("tr"):
        tds = row.select("td")
        if len(tds) < 5:
            continue

        # tds[4] = 작성일 ("26.04.27")
        date_str = tds[4].get_text(strip=True)
        if not date_str or not date_str[0].isdigit():
            continue

        try:
            dt = datetime.strptime(date_str, "%y.%m.%d")
            report_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

        # tds[0] = 종목명
        stock_a = tds[0].select_one("a")
        stock_name = stock_a.get_text(strip=True) if stock_a else tds[0].get_text(strip=True)

        # tds[1] = 제목
        title_a = tds[1].select_one("a")
        title = title_a.get_text(strip=True) if title_a else tds[1].get_text(strip=True)

        # tds[2] = 증권사
        firm = tds[2].get_text(strip=True)

        # tds[3] = 첨부(PDF 링크)
        pdf_a = tds[3].select_one("a")
        pdf_href = ""
        if pdf_a and pdf_a.get("href"):
            href = pdf_a["href"]
            pdf_href = href if href.startswith("http") else f"https://finance.naver.com{href}"

        # 목표주가: 제목에서 정규식 추출
        target_price: int | None = None
        m = _TP_RE.search(title)
        if m:
            try:
                target_price = int(m.group(1).replace(",", ""))
            except ValueError:
                pass

        reports.append({
            "stock_name": stock_name,
            "firm": firm,
            "target_price": target_price,
            "title": title,
            "date": report_date,
            "pdf": pdf_href,
        })

    return reports, False


# ── 다중 페이지 수집 ──────────────────────────────────────────────────────────

async def fetch_research_reports(start_date: str, end_date: str) -> list[dict]:
    """
    start_date, end_date: "YYYY-MM-DD"
    날짜 범위에 속하는 모든 리포트를 반환.
    """
    all_reports: list[dict] = []

    async with aiohttp.ClientSession(headers=_HEADERS) as session:
        for page in range(1, 11):  # 최대 10페이지 (~200개)
            reports, stop = await _scrape_page(session, page)

            for r in reports:
                if start_date <= r["date"] <= end_date:
                    all_reports.append(r)

            # 이 페이지의 최소 날짜가 start_date보다 이르면 더 볼 필요 없음
            dates = [r["date"] for r in reports]
            if dates and min(dates) < start_date:
                break
            if stop:
                break

            await asyncio.sleep(0.4)  # 서버 부하 방지

    return all_reports


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

async def build_research_digest(scheduled: bool = False) -> list[str]:
    """
    scheduled=True : 어제 08:00 KST ~ 오늘 08:00 KST  (자동 발송용)
    scheduled=False: 지금 기준 24시간 전 ~ 지금         (수동 호출용)
    """
    now_kst = datetime.now(pytz.utc).astimezone(KST)

    if scheduled:
        end_kst   = now_kst.replace(hour=8, minute=0, second=0, microsecond=0)
        start_kst = end_kst - timedelta(days=1)
    else:
        end_kst   = now_kst
        start_kst = end_kst - timedelta(hours=24)

    start_date = start_kst.strftime("%Y-%m-%d")
    end_date   = end_kst.strftime("%Y-%m-%d")
    date_range = f"{start_kst.strftime('%m/%d')} ~ {end_kst.strftime('%m/%d')} KST"

    reports = await fetch_research_reports(start_date, end_date)

    if not reports:
        return [f"📋 <b>리서치 보고서</b>\n<i>{date_range}</i>\n\n보고서가 없습니다."]

    # 종목별 그룹화
    by_stock: dict[str, list[dict]] = {}
    for r in reports:
        by_stock.setdefault(r["stock_name"], []).append(r)

    header = (
        f"📋 <b>리서치 보고서</b>\n"
        f"<i>{date_range}</i>\n"
        f"총 <b>{len(reports)}개</b> 보고서\n"
    )
    body: list[str] = []
    for stock_name in sorted(by_stock.keys()):
        body.append(f"\n<b>{escape(stock_name)}</b>")
        for r in by_stock[stock_name]:
            tp      = f" | TP {r['target_price']:,}원" if r["target_price"] else ""
            firm    = escape(r["firm"])
            title   = escape(r["title"][:50])
            pdf_tag = f' <a href="{r["pdf"]}">📄</a>' if r["pdf"] else ""
            body.append(f"  └ {firm}{tp}{pdf_tag}")
            body.append(f'    <i>{title}</i>')

    return _split(header + "\n".join(body))
