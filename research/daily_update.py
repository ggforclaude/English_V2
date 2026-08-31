"""
Daily_index.xlsx 일일 업데이트 마스터 스크립트
  - 리서치 보고서 (fetch_research.py)      ← 매일
  - 금 시세       (gold_price.py)          ← 매일
  - 섹터 RSI      (sector_rsi.py)          ← 매일 (주간 파일 없으면 신규 생성)
  - ETF 분석      (etf_analysis.py)        ← 주간 파일이 새로 생기는 날만 (sector_rsi 이후)
매일 08:30 KST 스케줄러에서 실행.
공휴일/휴무 등으로 실행이 며칠 스킵돼도 각 모듈이 "마지막 저장일 이후"를 다시 확인해
자동으로 공백을 메우도록 설계됨 (요일 하드코딩 대신 파일 상태 기반 판단).
"""
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
import pytz

# research/ 폴더를 sys.path에 추가해 모듈 import 가능하게
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

LOG_PATH = os.path.join(BASE_DIR, "fetch_log.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

KST = pytz.timezone("Asia/Seoul")


async def run_research():
    import fetch_research
    log.info("=== [1/3] 리서치 보고서 시작 ===")
    try:
        await fetch_research.main()
        log.info("=== [1/3] 리서치 보고서 완료 ===")
    except Exception as e:
        log.error(f"=== [1/3] 리서치 보고서 오류: {e} ===", exc_info=True)


async def run_gold():
    import gold_price
    log.info("=== [2/3] 금 시세 시작 ===")
    try:
        await gold_price.main()
        log.info("=== [2/3] 금 시세 완료 ===")
    except Exception as e:
        log.error(f"=== [2/3] 금 시세 오류: {e} ===", exc_info=True)


def run_sector_rsi():
    import sector_rsi
    log.info("=== [3/3] 섹터 RSI 시작 ===")
    try:
        sector_rsi.main()
        log.info("=== [3/3] 섹터 RSI 완료 ===")
    except Exception as e:
        log.error(f"=== [3/3] 섹터 RSI 오류: {e} ===", exc_info=True)


def _week_excel_path(monday) -> str:
    """주어진 월요일이 속한 주의 Excel 파일 경로."""
    m = monday.month
    w = (monday.day - 1) // 7 + 1
    y = monday.year
    return os.path.join(BASE_DIR, f"Daily_index_{m}m{w}w{y}.xlsx")


def _current_week_excel_path(today) -> str:
    monday = today - timedelta(days=today.weekday())
    return _week_excel_path(monday)


def _prev_week_excel_path(today) -> str:
    """이전 주 월요일 기준 Excel 파일 경로."""
    monday      = today - timedelta(days=today.weekday())
    prev_monday = monday - timedelta(days=7)
    return _week_excel_path(prev_monday)


async def run_research_backfill(prev_excel: str, start_date, end_date) -> None:
    """이전 주 파일에 누락된 리서치 보고서 소급 반영 (누락 범위는 호출자가 동적으로 계산)."""
    import fetch_research
    s, e = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    log.info(f"=== [0-1] 이전 주 리서치 소급 시작: {s} ~ {e} → {os.path.basename(prev_excel)} ===")
    try:
        await fetch_research.main(start_date=s, end_date=e, excel_path=prev_excel)
        log.info("=== [0-1] 이전 주 리서치 소급 완료 ===")
    except Exception as ex:
        log.error(f"=== [0-1] 이전 주 리서치 소급 오류: {ex} ===", exc_info=True)


async def run_gold_backfill(prev_excel: str, start_date, end_date) -> None:
    """이전 주 파일에 누락된 금 시세 소급 반영."""
    import gold_price
    s, e = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    log.info(f"=== [0-2] 이전 주 금 시세 소급 시작: {s} ~ {e} → {os.path.basename(prev_excel)} ===")
    try:
        await gold_price.main(start_date=s, end_date=e, excel_path=prev_excel)
        log.info("=== [0-2] 이전 주 금 시세 소급 완료 ===")
    except Exception as ex:
        log.error(f"=== [0-2] 이전 주 금 시세 소급 오류: {ex} ===", exc_info=True)


def run_rsi_backfill(prev_excel: str, today) -> None:
    """이전 주 파일의 섹터 RSI가 뒤처져 있으면 마저 채움 (이미 최신이면 자동으로 no-op)."""
    import sector_rsi
    log.info(f"=== [0-3] 이전 주 섹터 RSI 점검: {os.path.basename(prev_excel)} ===")
    try:
        sector_rsi.daily_update_excel(prev_excel, today)
        log.info("=== [0-3] 이전 주 섹터 RSI 점검 완료 ===")
    except Exception as ex:
        log.error(f"=== [0-3] 이전 주 섹터 RSI 점검 오류: {ex} ===", exc_info=True)


async def run_prev_week_backfill(now_kst) -> None:
    """새 주의 첫 실행(월요일이 아니어도 됨 — 휴무/공휴일로 월요일 실행이 스킵된 경우 포함)에
    직전 주 파일의 누락 구간(리서치/금 시세/RSI)을 동적으로 계산해 소급 반영."""
    import fetch_research
    import gold_price

    today       = now_kst.date()
    prev_excel  = _prev_week_excel_path(today)
    prev_sunday = today - timedelta(days=today.weekday() + 1)  # 이번 주 시작 전 마지막 일요일

    if not os.path.exists(prev_excel):
        log.warning(f"=== [0] 이전 주 파일 없음, 소급 건너뜀: {os.path.basename(prev_excel)} ===")
        return

    # 각 모듈의 마지막 저장일부터 지난주 일요일까지를 누락 구간으로 간주.
    # 하드코딩된 "금~일" 대신 실제 파일 상태를 봄으로써 목~금 등 더 이른 공백도 함께 잡는다.
    # 마지막 저장일(latest_research)은 그날 08:30 실행분만 반영된 상태일 수 있으므로
    # +1일이 아니라 그날 자체부터 다시 스캔해 당일 오후 발간분 누락을 방지한다.
    # (researchId 기준 dedup이라 이미 있는 항목을 다시 받아도 중복 저장되지 않는다.)
    latest_research = fetch_research._latest_existing_date(prev_excel)
    research_start = (
        datetime.strptime(latest_research, "%Y-%m-%d").date()
        if latest_research else today - timedelta(days=3)
    )
    if research_start <= prev_sunday:
        await run_research_backfill(prev_excel, research_start, prev_sunday)
    else:
        log.info("=== [0-1] 이전 주 리서치: 이미 최신 상태, 소급 불필요 ===")

    latest_gold = gold_price._latest_existing_date(prev_excel)
    gold_start = (
        datetime.strptime(latest_gold, "%Y-%m-%d").date() + timedelta(days=1)
        if latest_gold else today - timedelta(days=3)
    )
    if gold_start <= prev_sunday:
        await run_gold_backfill(prev_excel, gold_start, prev_sunday)
    else:
        log.info("=== [0-2] 이전 주 금 시세: 이미 최신 상태, 소급 불필요 ===")

    # RSI는 daily_update_excel이 자체적으로 "이미 최신"이면 no-op 처리하므로 조건 없이 호출
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_rsi_backfill, prev_excel, today)


def run_etf_analysis():
    """월요일 전용: sector_rsi 완료(tops cache 갱신) 후 ETF 분석 시트 추가"""
    import etf_analysis
    log.info("=== [4/4] ETF 분석 시작 ===")
    try:
        etf_analysis.run_weekly_update()
        log.info("=== [4/4] ETF 분석 완료 ===")
    except Exception as e:
        log.error(f"=== [4/4] ETF 분석 오류: {e} ===", exc_info=True)


async def async_main():
    now_kst = datetime.now(KST)
    log.info("=" * 55)
    log.info(f"Daily_index 업데이트 시작: {now_kst.strftime('%Y-%m-%d %H:%M:%S KST')}")
    log.info("=" * 55)

    is_new_week = not os.path.exists(_current_week_excel_path(now_kst.date()))

    # 이번 주 파일이 아직 없으면(=이번 주 첫 실행) 이전 주 파일의 누락 구간을 소급 반영.
    # 월요일 여부가 아니라 파일 존재 여부로 판단 — 월요일 자체가 휴무/공휴일로 스킵돼도
    # 화요일 이후 첫 실행에서 정상적으로 지난주 뒷정리가 이뤄진다.
    if is_new_week:
        await run_prev_week_backfill(now_kst)

    # 리서치 + 금 시세는 비동기 → 병렬 실행
    await asyncio.gather(
        run_research(),
        run_gold(),
    )

    # 섹터 RSI (동기 pykrx) → executor로 실행
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_sector_rsi)

    # ETF 분석은 이번 주 파일이 새로 만들어졌을 때만, sector_rsi 완료 후 실행
    # (월요일 실행이 스킵되고 화요일에 처음 파일이 생성돼도 정상적으로 뒤따라 실행됨)
    if is_new_week:
        await loop.run_in_executor(None, run_etf_analysis)

    log.info("=" * 55)
    log.info("Daily_index 업데이트 완료")
    log.info("=" * 55)


if __name__ == "__main__":
    asyncio.run(async_main())
