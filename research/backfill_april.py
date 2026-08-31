"""
Daily_index.xlsx 리서치 보고서 시트의 2026-03-31~2026-04-29 누락분 보완
사용: python backfill_april.py
"""
import asyncio
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# fetch_research.main()이 sys.argv[1], sys.argv[2]로 날짜 범위를 읽음
sys.argv = [__file__, "2026-03-31", "2026-04-29"]

import fetch_research as fr

# 현재 주차 파일(_5m1w…) 대신 Daily_index.xlsx 직접 지정
fr.EXCEL_PATH = os.path.join(BASE_DIR, "Daily_index.xlsx")

if __name__ == "__main__":
    print(f"대상 파일: {fr.EXCEL_PATH}")
    print("2026-03-31 ~ 2026-04-29 누락분 수집 시작...\n")
    asyncio.run(fr.main())
    print("\n완료. Daily_index.xlsx를 열어 리서치 보고서 시트를 확인하세요.")
