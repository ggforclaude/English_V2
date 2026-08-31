"""
세이브로(seibro.or.kr) ETF 종목보유현황 API 호출 예시

확인된 정보:
  - 엔드포인트: https://seibro.or.kr/websquare/engine/proworks/callServletService.jsp
  - 서비스 클래스: ksd.safe.bip.cnts.etf.process.EtfMartInfoPTask
  - task 이름:
      secnHoldStatStkPList      → 주식 편입 목록
      secnHoldStatStkPListCnt   → 주식 편입 건수
      secnHoldStatBondPList     → 채권 편입 목록
      secnHoldStatBondPListCnt  → 채권 편입 건수

  - 세션 초기화: https://seibro.or.kr/websquare/control.jsp?w2xPath=/... 에 GET 요청
    → WMONID, JSESSIONID 쿠키 획득
  - 요청 방식: multipart/form-data 또는 application/x-www-form-urlencoded + XML body

실행: python seibro_etf_holdings.py
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
from datetime import datetime, timedelta


# ── 설정 ──────────────────────────────────────────────────────────────────────
BASE_URL   = "https://seibro.or.kr"
SERVLET    = f"{BASE_URL}/websquare/engine/proworks/callServletService.jsp"
INIT_URL   = (
    f"{BASE_URL}/websquare/control.jsp"
    "?w2xPath=/IPORTAL/user/etf/BIP_CNTS06036V.xml&menuNo=186"
)

# 브라우저와 동일한 헤더
HEADERS_INIT = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": BASE_URL,
}

HEADERS_API = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/xml, text/xml, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Content-Type":    "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin":          BASE_URL,
    "Referer":         INIT_URL,
    "X-Requested-With": "XMLHttpRequest",
}


# ── 세션 초기화 ───────────────────────────────────────────────────────────────
def init_session() -> requests.Session:
    """
    세이브로 메인 페이지에 접속해 WMONID, JSESSIONID 쿠키를 획득합니다.
    """
    session = requests.Session()

    # 1단계: 메인 페이지 → WMONID 쿠키 설정
    resp = session.get(BASE_URL, headers=HEADERS_INIT, timeout=15)
    resp.raise_for_status()
    print(f"[세션] 메인 접속 완료 | WMONID={session.cookies.get('WMONID', '없음')}")

    # 2단계: ETF 종목보유현황 페이지 → JSESSIONID 갱신
    resp2 = session.get(INIT_URL, headers=HEADERS_INIT, timeout=15)
    resp2.raise_for_status()
    print(f"[세션] ETF 페이지 접속 완료 | JSESSIONID={session.cookies.get('JSESSIONID', '없음')[:20]}...")

    time.sleep(0.5)   # 서버 부하 방지
    return session


# ── XML 요청 본문 생성 ────────────────────────────────────────────────────────
def build_xml_body(task_name: str, isin: str, std_dt: str,
                   start_page: int = 1, end_page: int = 30,
                   radio2: str = "0") -> str:
    """
    WebSquare callServletService.jsp 에 전송할 XML 요청 본문

    파라미터:
      task_name  : secnHoldStatStkPList | secnHoldStatStkPListCnt
                   secnHoldStatBondPList | secnHoldStatBondPListCnt
      isin       : ETF ISIN (예: KR7069500007)
      std_dt     : 기준일 YYYYMMDD (예: 20240430)
      start_page : 페이지 시작 (기본 1)
      end_page   : 페이지 끝   (기본 30, 페이지당 30건)
      radio2     : "0"=보유비중, "1"=보유수량
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<root>
  <parameters>
    <parameter id="VCTF_ISIN"   value="{isin}"/>
    <parameter id="STD_DT"      value="{std_dt}"/>
    <parameter id="radio2"      value="{radio2}"/>
    <parameter id="START_PAGE"  value="{start_page}"/>
    <parameter id="END_PAGE"    value="{end_page}"/>
  </parameters>
</root>"""


# ── API 호출 (방법 A: form-encoded + XML) ─────────────────────────────────────
def call_api_formenc(session: requests.Session, task_name: str,
                     isin: str, std_dt: str,
                     start_page: int = 1, end_page: int = 30) -> str | None:
    """
    application/x-www-form-urlencoded 방식으로 호출.
    xml 파라미터에 XML 문자열을 넣어 전송합니다.
    """
    xml_body = build_xml_body(task_name, isin, std_dt, start_page, end_page)

    data = {
        "w2xPath":   "/IPORTAL/user/etf/BIP_CNTS06036V.xml",
        "taskName":  task_name,
        "serviceId": "",          # 빈 값으로 시도
        "xml":       xml_body,
    }

    resp = session.post(SERVLET, headers=HEADERS_API, data=data, timeout=20)
    print(f"[API-A] status={resp.status_code} | task={task_name}")
    return resp.text


# ── API 호출 (방법 B: multipart/form-data) ────────────────────────────────────
def call_api_multipart(session: requests.Session, task_name: str,
                       isin: str, std_dt: str,
                       start_page: int = 1, end_page: int = 30) -> str | None:
    """
    multipart/form-data 방식으로 호출 (Content-Type 헤더를 requests가 자동 설정).
    """
    xml_body = build_xml_body(task_name, isin, std_dt, start_page, end_page)

    headers = {k: v for k, v in HEADERS_API.items() if k != "Content-Type"}

    files = {
        "w2xPath":   (None, "/IPORTAL/user/etf/BIP_CNTS06036V.xml"),
        "taskName":  (None, task_name),
        "serviceId": (None, ""),
        "xml":       (None, xml_body, "application/xml"),
    }

    resp = session.post(SERVLET, headers=headers, files=files, timeout=20)
    print(f"[API-B] status={resp.status_code} | task={task_name}")
    return resp.text


# ── API 호출 (방법 C: 브라우저 네트워크 탭 방식 재현) ─────────────────────────
def call_api_browser_style(session: requests.Session, task_name: str,
                           isin: str, std_dt: str,
                           start_page: int = 1, end_page: int = 30) -> str | None:
    """
    브라우저 개발자 도구에서 캡처한 실제 요청과 최대한 유사하게 재현.
    WebSquare 엔진은 단일 'xml' 키에 전체 요청을 담는 방식 사용.

    실제 브라우저에서 개발자도구 → Network 탭 → callServletService.jsp 요청을
    'Copy as cURL' 해서 확인한 후 이 함수를 수정하세요.
    """
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<w2xSys>
  <taskList>
    <task name="{task_name}" serviceClass="ksd.safe.bip.cnts.etf.process.EtfMartInfoPTask">
      <inBlock>
        <VCTF_ISIN>{isin}</VCTF_ISIN>
        <STD_DT>{std_dt}</STD_DT>
        <radio2>0</radio2>
        <START_PAGE>{start_page}</START_PAGE>
        <END_PAGE>{end_page}</END_PAGE>
      </inBlock>
    </task>
  </taskList>
</w2xSys>"""

    data = {
        "w2xPath":  "/IPORTAL/user/etf/BIP_CNTS06036V.xml",
        "taskName": task_name,
        "xml":      xml_payload,
    }

    resp = session.post(SERVLET, headers=HEADERS_API, data=data, timeout=20)
    print(f"[API-C] status={resp.status_code} | task={task_name}")
    return resp.text


# ── 응답 파싱 ─────────────────────────────────────────────────────────────────
def parse_response(xml_text: str) -> list[dict]:
    """
    XML 응답에서 편입 종목 목록을 추출합니다.
    응답 구조 예시:
      <root>
        <grid1>
          <row>
            <KOR_SECN_NM>삼성전자</KOR_SECN_NM>
            <HOLD_IMPO>30.5</HOLD_IMPO>
            <VCTF_QTY>1000</VCTF_QTY>
          </row>
          ...
        </grid1>
      </root>
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"[파싱 오류] XML 파싱 실패: {e}")
        print(f"[응답 원문]\n{xml_text[:500]}")
        return []

    # 에러 응답 확인
    warning = root.find(".//WARNING") or root.find(".//warning")
    if warning is not None:
        msg_elem = warning.find(".//msg")
        msg = msg_elem.get("value") if msg_elem is not None else "알 수 없는 오류"
        print(f"[서버 오류] {msg}")
        return []

    # grid1(주식) 또는 grid2(채권) 행 추출
    rows = root.findall(".//grid1/row") or root.findall(".//grid2/row")
    if not rows:
        # 구조가 다를 경우 모든 row 태그 탐색
        rows = root.findall(".//row")

    result = []
    for row in rows:
        record = {child.tag: child.text for child in row}
        result.append(record)

    return result


# ── 전체 건수 조회 ────────────────────────────────────────────────────────────
def get_total_count(session: requests.Session, isin: str, std_dt: str,
                    asset_type: str = "stk") -> int:
    """
    asset_type: "stk" (주식) 또는 "bond" (채권)
    """
    task = f"secnHoldStat{'Stk' if asset_type == 'stk' else 'Bond'}PListCnt"
    # 방법 A 먼저 시도
    xml_text = call_api_formenc(session, task, isin, std_dt)

    try:
        root = ET.fromstring(xml_text)
        cnt_elem = root.find(".//LIST_CNT")
        if cnt_elem is not None and cnt_elem.text:
            return int(cnt_elem.text)
    except Exception:
        pass
    return 0


# ── 전체 편입 종목 조회 (페이지네이션) ────────────────────────────────────────
def get_all_holdings(session: requests.Session, isin: str,
                     std_dt: str = "", asset_type: str = "stk") -> list[dict]:
    """
    페이지네이션을 처리하여 전체 편입 종목을 반환합니다.

    isin      : ETF ISIN 코드 (예: KR7069500007)
    std_dt    : 기준일 YYYYMMDD. 비어있으면 오늘 기준 최근 영업일 사용
    asset_type: "stk" (주식ETF) 또는 "bond" (채권ETF)
    """
    if not std_dt:
        # 오늘이 월요일이면 금요일 기준
        today = datetime.today()
        if today.weekday() == 0:
            std_dt = (today - timedelta(days=3)).strftime("%Y%m%d")
        elif today.weekday() == 6:
            std_dt = (today - timedelta(days=2)).strftime("%Y%m%d")
        else:
            std_dt = today.strftime("%Y%m%d")

    task_list = f"secnHoldStat{'Stk' if asset_type == 'stk' else 'Bond'}PList"

    PAGE_SIZE = 30
    all_records = []
    page = 1

    while True:
        start = (page - 1) * PAGE_SIZE + 1
        end   = page * PAGE_SIZE

        # 방법 A 시도 → 실패 시 방법 C 시도
        xml_text = call_api_formenc(session, task_list, isin, std_dt, start, end)
        records = parse_response(xml_text)

        if not records:
            # 방법 C로 재시도
            print(f"[재시도] 방법 C로 page={page} 재시도 중...")
            xml_text = call_api_browser_style(session, task_list, isin, std_dt, start, end)
            records = parse_response(xml_text)

        if not records:
            break

        all_records.extend(records)

        if len(records) < PAGE_SIZE:
            break   # 마지막 페이지

        page += 1
        time.sleep(0.3)   # 서버 부하 방지

    return all_records


# ── 디버그: 실제 요청/응답 원문 출력 ─────────────────────────────────────────
def debug_raw_request(session: requests.Session, isin: str, std_dt: str):
    """
    requests.PreparedRequest를 사용해 실제 전송되는 내용을 출력합니다.
    브라우저 개발자도구와 비교할 때 사용하세요.
    """
    task_name = "secnHoldStatStkPList"
    xml_body  = build_xml_body(task_name, isin, std_dt, 1, 30)

    data = {
        "w2xPath":  "/IPORTAL/user/etf/BIP_CNTS06036V.xml",
        "taskName": task_name,
        "xml":      xml_body,
    }

    req = requests.Request("POST", SERVLET, headers=HEADERS_API, data=data)
    prepared = session.prepare_request(req)

    print("=" * 60)
    print("[디버그] 실제 요청 내용")
    print(f"URL: {prepared.url}")
    print(f"Headers:")
    for k, v in prepared.headers.items():
        print(f"  {k}: {v}")
    print(f"\nBody (앞 1000자):")
    body = prepared.body
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    print(body[:1000])
    print("=" * 60)

    resp = session.send(prepared, timeout=20)
    print(f"[응답] status={resp.status_code}")
    print(f"[응답] 앞 2000자:\n{resp.text[:2000]}")
    return resp.text


# ── 메인 실행 ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 예시: KODEX 삼성그룹 (069500 → ISIN: KR7069500007)
    # 실제 ISIN은 KRX 또는 SEIBro 검색으로 확인하세요
    TEST_ISIN  = "KR7069500007"   # KODEX 200
    TEST_DATE  = "20240430"       # 기준일 (최근 영업일)

    print("=" * 60)
    print("세이브로 ETF 종목보유현황 API 테스트")
    print("=" * 60)

    # 1. 세션 초기화
    session = init_session()

    # 2. 디버그 모드: 실제 요청/응답 원문 출력
    print("\n[STEP 1] 디버그 요청 (원문 확인)")
    raw = debug_raw_request(session, TEST_ISIN, TEST_DATE)

    # 3. 방법 B (multipart) 시도
    print("\n[STEP 2] multipart 방식 시도")
    raw_b = call_api_multipart(session, "secnHoldStatStkPList",
                               TEST_ISIN, TEST_DATE, 1, 30)
    print(f"응답(앞 500자):\n{raw_b[:500]}")

    # 4. 전체 편입 종목 조회
    print("\n[STEP 3] 전체 편입 종목 조회")
    holdings = get_all_holdings(session, TEST_ISIN, TEST_DATE, "stk")

    if holdings:
        print(f"\n총 {len(holdings)}개 종목 확인")
        print(f"{'종목명':<20} {'보유비중':>8} {'보유수량':>12}")
        print("-" * 45)
        for h in holdings[:10]:
            name   = h.get("KOR_SECN_NM", "")
            weight = h.get("HOLD_IMPO", "")
            qty    = h.get("VCTF_QTY", "")
            print(f"{name:<20} {weight:>8} {qty:>12}")
    else:
        print("편입 종목을 가져오지 못했습니다.")
        print("브라우저 개발자도구(F12) → Network 탭에서 실제 요청을 확인하세요.")
        print("  1. https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/etf/BIP_CNTS06036V.xml&menuNo=186 접속")
        print("  2. Network 탭 열기 → callServletService.jsp 필터링")
        print("  3. 요청 클릭 → Headers / Payload 탭에서 실제 파라미터 확인")
        print("  4. 'Copy as cURL' → 이 코드와 비교하여 차이점 수정")

    # 5. 결과 JSON 저장
    if holdings:
        out_path = "seibro_test_result.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(holdings, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {out_path}")
