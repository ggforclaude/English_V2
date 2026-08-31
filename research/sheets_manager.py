"""
Google Sheets 관리 모듈
- Google Sheets API를 사용해 데이터를 읽고 쓴다
- 시트 구조: "최신일자", "누적데이터_리서치", "누적데이터_금시세", "누적데이터_RSI", "누적데이터_지표", "뉴스"
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import pytz

KST = pytz.timezone("Asia/Seoul")

# Google Sheets API 인증
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "sheets_credentials.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_ID", "")  # .env에서 로드

def _get_auth():
    """Google Sheets API 인증 객체 반환"""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"Google 서비스 계정 키 파일이 없습니다: {CREDENTIALS_PATH}")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
    return gspread.authorize(credentials)

def get_spreadsheet():
    """Google Sheets 객체 반환"""
    if not SPREADSHEET_ID:
        raise ValueError("GOOGLE_SHEETS_ID 환경변수가 설정되지 않았습니다.")
    client = _get_auth()
    return client.open_by_key(SPREADSHEET_ID)

def ensure_sheets_exist():
    """필요한 시트들이 있는지 확인하고 없으면 생성"""
    sh = get_spreadsheet()
    required_sheets = [
        "최신일자_리서치",
        "최신일자_금시세",
        "최신일자_RSI",
        "누적데이터_리서치",
        "누적데이터_금시세",
        "누적데이터_RSI",
        "누적데이터_지표",
        "뉴스",
    ]

    existing_sheets = {ws.title for ws in sh.worksheets()}

    for sheet_name in required_sheets:
        if sheet_name not in existing_sheets:
            sh.add_worksheet(title=sheet_name, rows=1000, cols=20)
            print(f"✓ 시트 생성: {sheet_name}")
        else:
            print(f"✓ 시트 확인: {sheet_name}")

def get_sheet(sheet_name: str):
    """특정 시트 객체 반환"""
    sh = get_spreadsheet()
    try:
        return sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"⚠ 시트를 찾을 수 없습니다: {sheet_name}")
        return None

def append_research(data: list[dict]):
    """리서치 데이터 추가 (누적데이터_리서치)
    data: [{"date": "2026-08-24", "company": "삼성전자", "opinion": "매수", "target": "1500", ...}, ...]
    """
    ws = get_sheet("누적데이터_리서치")
    if not ws:
        return

    # 헤더 확인
    if ws.cell(1, 1).value is None:
        headers = ["날짜", "회사", "종목코드", "증권사", "투자의견", "목표주가", "제목", "링크"]
        ws.append_row(headers)

    for item in data:
        row = [
            item.get("date", ""),
            item.get("company", ""),
            item.get("code", ""),
            item.get("broker", ""),
            item.get("opinion", ""),
            item.get("target", ""),
            item.get("title", ""),
            item.get("link", ""),
        ]
        ws.append_row(row)

def append_gold_price(data: dict):
    """금시세 데이터 추가 (누적데이터_금시세)
    data: {"date": "2026-08-24", "price": "75000", "change": "500", "change_percent": "0.67"}
    """
    ws = get_sheet("누적데이터_금시세")
    if not ws:
        return

    if ws.cell(1, 1).value is None:
        headers = ["날짜", "현재가", "변화", "변화율(%)"]
        ws.append_row(headers)

    row = [
        data.get("date", ""),
        data.get("price", ""),
        data.get("change", ""),
        data.get("change_percent", ""),
    ]
    ws.append_row(row)

def append_sector_rsi(data: list[dict]):
    """섹터 RSI 데이터 추가 (누적데이터_RSI)
    data: [{"date": "2026-08-24", "sector": "반도체", "rsi": "72.3"}, ...]
    """
    ws = get_sheet("누적데이터_RSI")
    if not ws:
        return

    if ws.cell(1, 1).value is None:
        headers = ["날짜", "섹터", "RSI"]
        ws.append_row(headers)

    for item in data:
        row = [
            item.get("date", ""),
            item.get("sector", ""),
            item.get("rsi", ""),
        ]
        ws.append_row(row)

def append_indicators(data: dict):
    """투자 지표 데이터 추가 (누적데이터_지표)
    data: {"date": "2026-08-24", "usd_krw": "1300.5", "jpy_krw": "8.5", "eur_krw": "1400",
           "kr_rate": "3.5", "us_rate": "4.2", "kr_bond_3y": "3.2", ..., "vix_kr": "15.2", "vix_us": "18.5"}
    """
    ws = get_sheet("누적데이터_지표")
    if not ws:
        return

    if ws.cell(1, 1).value is None:
        headers = [
            "날짜",
            "USD/KRW", "JPY/KRW", "EUR/KRW",
            "한국기준금리", "미국기준금리",
            "한국국채3Y", "한국국채5Y", "한국국채10Y",
            "미국국채3Y", "미국국채5Y", "미국국채10Y",
            "코스피", "코스닥",
            "VIX(한국)", "VIX(미국)"
        ]
        ws.append_row(headers)

    row = [
        data.get("date", ""),
        data.get("usd_krw", ""),
        data.get("jpy_krw", ""),
        data.get("eur_krw", ""),
        data.get("kr_rate", ""),
        data.get("us_rate", ""),
        data.get("kr_bond_3y", ""),
        data.get("kr_bond_5y", ""),
        data.get("kr_bond_10y", ""),
        data.get("us_bond_3y", ""),
        data.get("us_bond_5y", ""),
        data.get("us_bond_10y", ""),
        data.get("kospi", ""),
        data.get("kosdaq", ""),
        data.get("vix_kr", ""),
        data.get("vix_us", ""),
    ]
    ws.append_row(row)

def append_news(data: dict):
    """뉴스 데이터 추가 (뉴스)
    data: {"date": "2026-08-24", "summary": "요약 텍스트", "raw_messages": "원문 JSON", "timestamp": "2026-08-24 09:05"}
    """
    ws = get_sheet("뉴스")
    if not ws:
        return

    if ws.cell(1, 1).value is None:
        headers = ["날짜", "요약", "원문(JSON)"]
        ws.append_row(headers)

    row = [
        data.get("date", ""),
        data.get("summary", ""),
        data.get("raw_messages", ""),
    ]
    ws.append_row(row)

def update_today_research(data: list[dict]):
    """오늘의 리서치 업데이트 (최신일자_리서치)"""
    ws = get_sheet("최신일자_리서치")
    if not ws:
        return

    # 기존 데이터 삭제 (헤더 유지)
    if ws.row_count > 1:
        ws.delete_rows(2, ws.row_count)

    if ws.cell(1, 1).value is None:
        headers = ["날짜", "회사", "종목코드", "증권사", "투자의견", "목표주가", "제목", "링크"]
        ws.append_row(headers)

    for item in data:
        row = [
            item.get("date", ""),
            item.get("company", ""),
            item.get("code", ""),
            item.get("broker", ""),
            item.get("opinion", ""),
            item.get("target", ""),
            item.get("title", ""),
            item.get("link", ""),
        ]
        ws.append_row(row)

def update_today_indicators(data: dict):
    """오늘의 투자 지표 업데이트 (최신일자_지표) - 한 행만 표시"""
    ws = get_sheet("최신일자_지표") if get_sheet("최신일자_지표") else None

    if not ws:
        sh = get_spreadsheet()
        ws = sh.add_worksheet(title="최신일자_지표", rows=10, cols=20)

    # 기존 데이터 삭제
    if ws.row_count > 1:
        ws.delete_rows(2, ws.row_count)

    if ws.cell(1, 1).value is None:
        headers = [
            "날짜",
            "USD/KRW", "JPY/KRW", "EUR/KRW",
            "한국기준금리", "미국기준금리",
            "한국국채3Y", "한국국채5Y", "한국국채10Y",
            "미국국채3Y", "미국국채5Y", "미국국채10Y",
            "코스피", "코스닥",
            "VIX(한국)", "VIX(미국)"
        ]
        ws.append_row(headers)

    row = [
        data.get("date", ""),
        data.get("usd_krw", ""),
        data.get("jpy_krw", ""),
        data.get("eur_krw", ""),
        data.get("kr_rate", ""),
        data.get("us_rate", ""),
        data.get("kr_bond_3y", ""),
        data.get("kr_bond_5y", ""),
        data.get("kr_bond_10y", ""),
        data.get("us_bond_3y", ""),
        data.get("us_bond_5y", ""),
        data.get("us_bond_10y", ""),
        data.get("kospi", ""),
        data.get("kosdaq", ""),
        data.get("vix_kr", ""),
        data.get("vix_us", ""),
    ]
    ws.append_row(row)

if __name__ == "__main__":
    print("Google Sheets 구조 확인 및 생성...")
    ensure_sheets_exist()
    print("✓ 완료")
