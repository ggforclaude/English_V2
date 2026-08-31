"""
투자 지표 수집 모듈 (환율, 금리, VIX, 지수)
- 환율: USD/KRW, JPY/KRW, EUR/KRW
- 금리: 한국/미국 기준금리 + 국채 3/5/10년물
- VIX: 한국(KOSPI 200 VIX), 미국(S&P 500 VIX)
- 지수: 코스피, 코스닥
"""
import aiohttp
import asyncio
import logging
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import json

KST = pytz.timezone("Asia/Seoul")
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# 환율 수집 (네이버 금융)
# ─────────────────────────────────────────────────────────────────

async def fetch_exchange_rates() -> dict:
    """환율 정보 수집"""
    rates = {}
    pairs = [
        ("USD", "KRW", "USDKRW"),  # USD/KRW
        ("JPY", "KRW", "JPYKRW"),  # JPY/KRW
        ("EUR", "KRW", "EURKRW"),  # EUR/KRW
    ]

    async with aiohttp.ClientSession() as session:
        for from_curr, to_curr, code in pairs:
            try:
                url = f"https://m.stock.naver.com/api/exchanges/{code}.json"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        rate = data.get("rate", 0)
                        key = f"{from_curr}/{to_curr}".lower().replace("/", "_")
                        rates[key] = round(float(rate), 2)
                        log.info(f"✓ {from_curr}/{to_curr}: {rate}")
                    else:
                        log.warning(f"⚠ {from_curr}/{to_curr} 수집 실패 (HTTP {resp.status})")
            except Exception as e:
                log.error(f"⚠ {from_curr}/{to_curr} 수집 오류: {e}")
                rates[f"{from_curr}/{to_curr}".lower().replace("/", "_")] = ""

    return rates

# ─────────────────────────────────────────────────────────────────
# 금리 수집 (한국은행, FRED)
# ─────────────────────────────────────────────────────────────────

async def fetch_interest_rates() -> dict:
    """금리 정보 수집"""
    rates = {}

    # 한국 기준금리 (한국은행 - 일반 공개 데이터 기반)
    # 실제로는 매일 바뀌지 않으므로 캐시나 수동 업데이트 권장
    # 여기서는 네이버 금융 API 사용 시도
    try:
        async with aiohttp.ClientSession() as session:
            # 한국 기준금리
            url = "https://api.finance.naver.com/sise?code=INTEREST_RATE_KR"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    kr_rate = data.get("value", 0)
                    rates["kr_rate"] = round(float(kr_rate), 2)
                    log.info(f"✓ 한국 기준금리: {kr_rate}%")
    except Exception as e:
        log.warning(f"⚠ 한국 기준금리 수집 오류: {e}")
        rates["kr_rate"] = ""

    # 미국 기준금리 (FRED API - 무료이지만 API 키 필요)
    # 여기서는 mock 데이터 사용 (실제로는 FRED 또는 다른 소스 필요)
    try:
        # FRED API 키가 있으면 활용, 없으면 스킵
        fred_key = os.getenv("FRED_API_KEY", "")
        if fred_key:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.stlouisfed.org/fred/series/FEDFUNDS/observations?api_key={fred_key}&limit=1&sort_order=desc"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data["observations"]:
                            us_rate = float(data["observations"][0]["value"])
                            rates["us_rate"] = round(us_rate, 2)
                            log.info(f"✓ 미국 기준금리: {us_rate}%")
    except Exception as e:
        log.warning(f"⚠ 미국 기준금리 수집 오류: {e}")

    if "us_rate" not in rates:
        rates["us_rate"] = ""

    # 국채 수익률은 별도 API 또는 웹 스크래핑 필요
    # 여기서는 placeholder
    for key in ["kr_bond_3y", "kr_bond_5y", "kr_bond_10y", "us_bond_3y", "us_bond_5y", "us_bond_10y"]:
        rates[key] = ""

    return rates

# ─────────────────────────────────────────────────────────────────
# VIX 수집 (네이버 금융)
# ─────────────────────────────────────────────────────────────────

async def fetch_vix() -> dict:
    """VIX 지수 수집"""
    vix_data = {}

    async with aiohttp.ClientSession() as session:
        # 한국 VIX (VKOSPI)
        try:
            url = "https://m.stock.naver.com/api/index/VKOSPI"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vix_kr = data.get("value", 0)
                    vix_data["vix_kr"] = round(float(vix_kr), 2)
                    log.info(f"✓ 한국 VIX (VKOSPI): {vix_kr}")
                else:
                    log.warning(f"⚠ 한국 VIX 수집 실패 (HTTP {resp.status})")
                    vix_data["vix_kr"] = ""
        except Exception as e:
            log.error(f"⚠ 한국 VIX 수집 오류: {e}")
            vix_data["vix_kr"] = ""

        # 미국 VIX (^VIX)
        try:
            url = "https://m.stock.naver.com/api/index/VIX"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vix_us = data.get("value", 0)
                    vix_data["vix_us"] = round(float(vix_us), 2)
                    log.info(f"✓ 미국 VIX: {vix_us}")
                else:
                    log.warning(f"⚠ 미국 VIX 수집 실패 (HTTP {resp.status})")
                    vix_data["vix_us"] = ""
        except Exception as e:
            log.error(f"⚠ 미국 VIX 수집 오류: {e}")
            vix_data["vix_us"] = ""

    return vix_data

# ─────────────────────────────────────────────────────────────────
# 지수 수집 (코스피, 코스닥)
# ─────────────────────────────────────────────────────────────────

async def fetch_indices() -> dict:
    """지수 정보 수집"""
    indices = {}

    async with aiohttp.ClientSession() as session:
        # 코스피
        try:
            url = "https://m.stock.naver.com/api/index/KOSPI"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    kospi = data.get("value", 0)
                    indices["kospi"] = round(float(kospi), 2)
                    log.info(f"✓ 코스피: {kospi}")
                else:
                    indices["kospi"] = ""
        except Exception as e:
            log.error(f"⚠ 코스피 수집 오류: {e}")
            indices["kospi"] = ""

        # 코스닥
        try:
            url = "https://m.stock.naver.com/api/index/KOSDAQ"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    kosdaq = data.get("value", 0)
                    indices["kosdaq"] = round(float(kosdaq), 2)
                    log.info(f"✓ 코스닥: {kosdaq}")
                else:
                    indices["kosdaq"] = ""
        except Exception as e:
            log.error(f"⚠ 코스닥 수집 오류: {e}")
            indices["kosdaq"] = ""

    return indices

# ─────────────────────────────────────────────────────────────────
# 통합 함수
# ─────────────────────────────────────────────────────────────────

async def main() -> dict:
    """모든 지표 수집"""
    log.info("=== 투자 지표 수집 시작 ===")

    exchange = await fetch_exchange_rates()
    interest = await fetch_interest_rates()
    vix = await fetch_vix()
    indices = await fetch_indices()

    all_indicators = {
        "date": datetime.now(KST).strftime("%Y-%m-%d"),
        "time": datetime.now(KST).strftime("%H:%M"),
        **exchange,
        **interest,
        **vix,
        **indices,
    }

    log.info(f"=== 지표 수집 완료: {len(all_indicators)}개 ===")
    return all_indicators

if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    indicators = asyncio.run(main())
    print(json.dumps(indicators, indent=2))
