"""
한미약품 애널리스트 리포트 종합 분석 → PDF 생성
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── 폰트 등록 ─────────────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont("Malgun",   "C:/Windows/Fonts/malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBd", "C:/Windows/Fonts/malgunbd.ttf"))

# ── 색상 ──────────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#1F4E79")
BLUE    = colors.HexColor("#2E75B6")
LBLUE   = colors.HexColor("#BDD7EE")
LLBLUE  = colors.HexColor("#DEEAF1")
GREEN   = colors.HexColor("#375623")
LGREEN  = colors.HexColor("#E2EFDA")
RED     = colors.HexColor("#C00000")
LRED    = colors.HexColor("#FFE7E7")
YELLOW  = colors.HexColor("#FFF2CC")
GRAY    = colors.HexColor("#595959")
LGRAY   = colors.HexColor("#F2F2F2")
WHITE   = colors.white
BLACK   = colors.black

W, H = A4
ML = 18*mm; MR = 18*mm; MT = 20*mm; MB = 20*mm
TW = W - ML - MR  # 텍스트 폭

# ── 스타일 ────────────────────────────────────────────────────────────────────
def S(name, **kw):
    kw.pop("parent", None)
    defaults = dict(fontName="Malgun", fontSize=9, leading=14, textColor=BLACK)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

styles = {
    "cover_title": S("cover_title", fontName="MalgunBd", fontSize=28,
                     textColor=WHITE, alignment=TA_CENTER, leading=36),
    "cover_sub":   S("cover_sub",   fontName="Malgun",   fontSize=13,
                     textColor=LBLUE, alignment=TA_CENTER, leading=20),
    "cover_meta":  S("cover_meta",  fontName="Malgun",   fontSize=10,
                     textColor=LBLUE, alignment=TA_CENTER),

    "h1": S("h1", fontName="MalgunBd", fontSize=14, textColor=WHITE,
            leading=20, spaceAfter=2),
    "h2": S("h2", fontName="MalgunBd", fontSize=11, textColor=NAVY,
            leading=16, spaceBefore=10, spaceAfter=3),
    "h3": S("h3", fontName="MalgunBd", fontSize=10, textColor=BLUE,
            leading=14, spaceBefore=6, spaceAfter=2),

    "body":  S("body",  fontSize=9,  leading=14, spaceAfter=2),
    "bodyb": S("bodyb", fontName="MalgunBd", fontSize=9, leading=14, spaceAfter=2),
    "small": S("small", fontSize=8,  leading=12, textColor=GRAY),
    "note":  S("note",  fontSize=8,  leading=12, textColor=GRAY, spaceAfter=4),

    "bull": S("bull", fontSize=9, leading=13, leftIndent=10,
              bulletIndent=0, spaceAfter=1),
    "bull2": S("bull2", fontSize=8.5, leading=12, leftIndent=20,
               bulletIndent=10, spaceAfter=1),

    "th": S("th", fontName="MalgunBd", fontSize=8.5, textColor=WHITE,
            alignment=TA_CENTER, leading=12),
    "td": S("td", fontSize=8.5, leading=12, alignment=TA_LEFT),
    "tdc": S("tdc", fontSize=8.5, leading=12, alignment=TA_CENTER),
    "tdr": S("tdr", fontSize=8.5, leading=12, alignment=TA_RIGHT),

    "tag_buy":  S("tag_buy",  fontName="MalgunBd", fontSize=8, textColor=BLUE,
                  alignment=TA_CENTER),
    "tag_hold": S("tag_hold", fontName="MalgunBd", fontSize=8, textColor=RED,
                  alignment=TA_CENTER),
    "tag_up":   S("tag_up",   fontName="MalgunBd", fontSize=8,
                  textColor=colors.HexColor("#375623"), alignment=TA_CENTER),
}

# ── 헬퍼 ──────────────────────────────────────────────────────────────────────
def P(text, style="body"):
    return Paragraph(text, styles[style])

def B(text, indent=1):
    bullet = "•" if indent == 1 else "–"
    sty    = "bull" if indent == 1 else "bull2"
    return Paragraph(f"{bullet}  {text}", styles[sty])

def HR(color=LBLUE, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=4, spaceBefore=4)

def SP(h=4):
    return Spacer(1, h)

def section_header(title, color=NAVY):
    """색 배경 섹션 헤더 반환 (Table 이용)"""
    tbl = Table([[Paragraph(title, styles["h1"])]],
                colWidths=[TW], rowHeights=[22])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ]))
    return tbl

def sub_header(title):
    tbl = Table([[Paragraph(title, styles["h2"])]],
                colWidths=[TW])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LLBLUE),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LINEBELOW", (0,0), (-1,-1), 1, BLUE),
    ]))
    return tbl

def make_table(headers, rows, col_widths=None, hdr_color=NAVY, row_colors=None):
    hdr_row = [Paragraph(h, styles["th"]) for h in headers]
    data    = [hdr_row]
    for i, row in enumerate(rows):
        bg = row_colors[i] if row_colors else (LGRAY if i % 2 == 0 else WHITE)
        data.append([Paragraph(str(c), styles["td"]) for c in row])

    tbl = Table(data, colWidths=col_widths or [TW/len(headers)]*len(headers),
                repeatRows=1)
    style = [
        ("BACKGROUND",   (0,0), (-1,0),  hdr_color),
        ("TEXTCOLOR",    (0,0), (-1,0),  WHITE),
        ("FONTNAME",     (0,0), (-1,0),  "MalgunBd"),
        ("FONTSIZE",     (0,0), (-1,-1), 8.5),
        ("LEADING",      (0,0), (-1,-1), 12),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#C0C0C0")),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]
    for i in range(1, len(rows)+1):
        bg = row_colors[i-1] if row_colors else (LGRAY if (i-1)%2==0 else WHITE)
        style.append(("BACKGROUND", (0,i), (-1,i), bg))
    tbl.setStyle(TableStyle(style))
    return tbl

def box(flowable, bg=LGREEN, border_color=GREEN, pad=8):
    tbl = Table([[flowable]], colWidths=[TW])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), bg),
        ("BOX",          (0,0), (-1,-1), 1,   border_color),
        ("LEFTPADDING",  (0,0), (-1,-1), pad),
        ("RIGHTPADDING", (0,0), (-1,-1), pad),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ]))
    return tbl

# ── 표지 ──────────────────────────────────────────────────────────────────────
def cover_page():
    elems = []
    # 배경 색 블록
    bg = Table([[""]],colWidths=[TW],rowHeights=[70])
    bg.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY)]))
    elems.append(SP(30))
    elems.append(bg)

    # 타이틀 오버레이 방식 대신 별도 블록
    title_block = Table([
        [Paragraph("한미약품 (128940)", styles["cover_title"])],
        [Paragraph("애널리스트 리포트 종합 분석", styles["cover_sub"])],
        [SP(6)],
        [Paragraph("분석 기간: 2025.01.10 ~ 2026.05.07  |  분석 리포트: 65개  |  커버리지 증권사: 11곳",
                   styles["cover_meta"])],
    ], colWidths=[TW])
    title_block.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), NAVY),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 14),
    ]))
    elems.append(title_block)
    elems.append(SP(20))
    elems.append(HR(NAVY, 2))
    elems.append(SP(10))

    # 핵심 요약 박스
    summary_items = [
        P("✦  현재 컨센서스: <b>전원 매수 (Buy/Outperform)</b>  |  평균 목표주가: <b>약 611,000원</b>  |  상승여력: <b>약 40%</b>", "bodyb"),
        SP(4),
        P("✦  에페글레나타이드 국내 3상 성공 (2025.10) → 2026년 4분기 국내 출시 예정", "body"),
        P("✦  에피노페그듀타이드(MSD) MASH 2b상 완료 → 2026년 하반기 결과 발표 예정", "body"),
        P("✦  4Q25 역대 최고 실적 달성: 영업이익 833억원 (+173% YoY)", "body"),
    ]
    inner = Table([[item] for item in summary_items], colWidths=[TW-20])
    inner.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    elems.append(box(inner, bg=LLBLUE, border_color=BLUE, pad=12))
    elems.append(PageBreak())
    return elems

# ── 본문 콘텐츠 ───────────────────────────────────────────────────────────────
def content():
    elems = []

    # ════════════════════════════════════════════════════════
    # 1. 투자 포인트
    # ════════════════════════════════════════════════════════
    elems += [section_header("1.  투자 포인트"), SP(6)]

    points = [
        ("에페글레나타이드", LGREEN, GREEN, [
            "2025.10.28 국내 임상 3상 성공 (40주 체중 감소 -9.75% / 5% 이상 감량 비율 79.4% vs 위약 14.5%)",
            "2025.12 식약처 허가 신청 완료 → <b>2026년 4분기 국내 출시 예정</b>",
            "출시 1년차 목표 매출 1,000억원 (교보증권 달성 가능 판단)",
            "국내 비만 치료제 시장: 4Q25 약 3,038억원 → 2026년 약 7,000억원 전망 (J-curve)",
            "국내 제약사 중 <b>유일한 비만 상업화 파이프라인</b> 보유 — 희소성 최대",
        ]),
        ("에피노페그듀타이드 (MK-6024, MSD 파트너)", LLBLUE, BLUE, [
            "MSD와 MASH 글로벌 2b상 <b>2025.12.29 종료</b> → 탑라인 결과 2026년 하반기 발표 예정",
            "노보 노디스크(아케로 $52억), 로슈(89바이오 $35억) MASH 인수합병 → 시장 가치 재확인",
            "탑라인 긍정 시 대규모 마일스톤 수령 + 에포시페그트루타이드 연쇄 가치 상승 기대",
            "증권사별 NPV 산정 범위: 1,247억원(신한) ~ 1조 6,624억원(iM) — 상당한 상방 여력",
        ]),
        ("에포시페그트루타이드 (자체 MASH 삼중작용제)", YELLOW, colors.HexColor("#BF8F00"), [
            "GLP-1/GIP/GCG 삼중작용 LAPS Triple Agonist — 글로벌 2b상 결과 2026년 하반기 예정",
            "에피노페그듀타이드 탑라인 긍정 시 삼중작용제 기대감 연쇄 상승",
        ]),
        ("차세대 비만 파이프라인: HM15275 · HM17321", LRED, RED, [
            "<b>HM15275</b> (삼중작용 GLP-1): 미국 2상 환자 모집 2026.4 완료 → 2027년 1분기 종료 예정. 기술이전(L/O) 유력 후보",
            "  ┗ 릴리 레타트루타이드 48주차 -24.2% 체중 감소 확인 → 빅파마 수요 증가",
            "<b>HM17321</b> (UCN2 근육보존형 비만): 2025.11 미국 1b상 시작. ADA2026 전임상 데이터 예정",
            "  ┗ 단순 감량을 넘어 근육 유지 수요 충족 → First-in-class 가능성",
        ]),
        ("4Q25 역대 최고 실적 · 2026년 가이던스", LGRAY, GRAY, [
            "4Q25: 매출 4,330억원 (+23%), 영업이익 833억원 (+173%, OPM 19.2%) — 컨센서스 이익 +18% 상회",
            "북경한미 4Q25 매출 1,251억원 (+67%), 영업이익 261억원 (+514%) — 재고 조정 완료",
            "한미정밀화학: 고수익 CDMO 전환 완료, 4Q25 흑자전환",
            "2026년 가이던스: <b>매출 10%↑  |  OPM 15%↑  |  연간 기술이전 1건 이상</b>",
        ]),
    ]

    for title, bg, border, bullets in points:
        items = [P(f"<b>▶  {title}</b>", "h3"), SP(2)]
        for b_text in bullets:
            items.append(B(b_text))
        items.append(SP(2))
        inner = Table([[i] for i in items], colWidths=[TW-20])
        inner.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),
                                   ("TOPPADDING",(0,0),(-1,-1),0),
                                   ("BOTTOMPADDING",(0,0),(-1,-1),0)]))
        elems += [box(inner, bg=bg, border_color=border, pad=10), SP(6)]

    elems += [PageBreak()]

    # ════════════════════════════════════════════════════════
    # 2. 리스크 포인트
    # ════════════════════════════════════════════════════════
    elems += [section_header("2.  리스크 포인트", color=colors.HexColor("#C00000")), SP(6)]

    risks = [
        ("① 에피노페그듀타이드 임상 결과 불확실",
         "EASL(5월) 초록 리스트 부재 → MSD가 하반기 학회로 발표 지연. 결과가 부정적일 경우 신약 가치 급락. "
         "수십 개의 경쟁 파이프라인 존재(노보, 릴리, 아케로/노보, 89바이오/로슈 등)."),
        ("② 1Q26 역기저효과 (단기 실적 부진)",
         "2025년 1분기 MSD 임상시료 대규모 공급 + 롤베돈 DS 공급 기저 소멸 → "
         "1Q26 영업이익 536억원 (-9.1% YoY), 컨센서스 하회."),
        ("③ 에페글레나타이드 시장 점유율 불확실",
         "국내 상업화 영업 역량 검증 미완. 약가 책정 및 건강보험 급여 여부가 핵심 변수. "
         "노보 노디스크(위고비) 등 글로벌 경쟁자 존재."),
        ("④ 거버넌스 리스크 (2025년 상반기, 현재 대부분 해소)",
         "창업주 임종윤 vs. 한미사이언스 경영권 분쟁. 미래에셋증권 20% 할인 독자 적용. "
         "2025년 4월 이후 대부분 해소 — 2026년 리포트에서는 거의 언급 없음."),
        ("⑤ 약가 개편 불확실성",
         "정부 약가 개편 정책에 따라 기존 제품군(로수젯 등) 수익성 영향 가능. "
         "키움증권이 2026년 4월 투자의견 하향의 주된 근거로 제시."),
        ("⑥ MASH 3상 전환까지 장기 시간 소요",
         "2b상 성공 후에도 3상 설계·환자 모집·종료까지 최소 3~4년 필요. "
         "iM증권(정재원): MASH 3상 데이터 가시화는 2028년에야 가능 (가장 보수적 추정)."),
        ("⑦ 에포시페그트루타이드 2b상 결과 미발표",
         "자체 MASH 삼중작용제로 파트너사 없이 단독 진행. 결과 실망 시 추가 L/O 지연 가능."),
    ]

    risk_data = []
    for title, desc in risks:
        risk_data.append([
            Paragraph(title, styles["bodyb"]),
            Paragraph(desc, styles["body"]),
        ])

    risk_tbl = Table(risk_data, colWidths=[55*mm, TW-55*mm])
    risk_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,-1), LRED),
        ("BACKGROUND",   (1,0), (1,-1), WHITE),
        ("FONTNAME",     (0,0), (0,-1), "MalgunBd"),
        ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#E0A0A0")),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LRED, colors.HexColor("#FFF5F5")]*4),
    ]))
    elems += [risk_tbl, SP(6), PageBreak()]

    # ════════════════════════════════════════════════════════
    # 3. 증권사별 애널리스트 주장 요약
    # ════════════════════════════════════════════════════════
    elems += [section_header("3.  증권사별 애널리스트 주장 요약"), SP(8)]

    brokers = [
        {
            "name": "DS투자증권  —  김민정",
            "summary": "가장 공격적인 목표주가 상향 (380,000 → 680,000원). 에페글레나타이드 성공 후 EV/EBITDA 18.5배 적용, '리레이팅 국면 진입' 논거를 가장 강하게 주장. HM17321 SAD 일정을 가장 구체적으로 추적.",
            "rows": [
                ("2025.01.10", "매수", "380,000↓", "4Q24 Preview. 거버넌스 리스크 불확실, 비만 임상 기대"),
                ("2025.07.08", "매수", "400,000↑", "2Q25 Preview. 에피노페그듀타이드 L/O 기대 상향"),
                ("2025.10.15", "매수 (Top Pick)", "470,000↑", "3Q25 Preview. 에페글레나타이드 3상 데이터 임박"),
                ("2025.10.28", "매수", "510,000↑", "에페글레나타이드 3상 성공. Peak sales 9,932억원 추정"),
                ("2026.02.06", "매수", "680,000↑", "4Q25 역대 최고 실적. EV/EBITDA 18.5배 리레이팅"),
                ("2026.04.13", "매수", "680,000 유지", "1Q26 Preview. MSD 기저효과 하회 예상, 2027 본격 성장"),
            ],
        },
        {
            "name": "미래에셋증권  —  김승민",
            "summary": "거버넌스 20% 할인을 가장 강하게·오래 적용. 단 4Q25 역대 최고 실적 확인 후 350,000 → 660,000원으로 단번에 310,000원 상향 (전 증권사 최대폭). 거버넌스 완전 해제 + 실적 정상화 + 파이프라인 재평가 3중 효과.",
            "rows": [
                ("2025.02.05", "매수", "350,000↓", "거버넌스 20% 할인 독자 적용"),
                ("2025.07.28", "매수", "370,000↑", "거버넌스 할인 부분 완화"),
                ("2026.02.06", "매수", "660,000↑", "4Q25 최고 실적 + 거버넌스 할인 완전 해제. Target EV/EBITDA 16.4배 (20% 프리미엄). 파이프라인 가치 2조 5,472억원"),
            ],
        },
        {
            "name": "하나증권  —  김선아",
            "summary": "2025.6 신규 커버리지. 세부 현금흐름(롤베돈 로열티, 길리어드 계약금 등) 분석에 강점. HM15275 IND 승인 시점 등 파이프라인 마일스톤을 가장 상세하게 추적.",
            "rows": [
                ("2025.06.18", "BUY(신규)", "400,000", "신규 커버리지. LAPSCOVERY 희소성, 다중 파이프라인"),
                ("2025.10.28", "BUY", "500,000↑", "에페글레나타이드 3상 성공 상세 분석"),
                ("2025.11.06", "BUY", "500,000 유지", "NDR 후기. HM15275 미국 2상 IND 승인"),
                ("2026.02.06", "BUY", "640,000↑", "4Q25 Review. 길리어드 계약금, 롤베돈 로열티 신규 인식"),
                ("2026.04.13", "BUY", "640,000 유지", "1Q26 Preview. EASL 에피노페그듀타이드 발표 기대"),
            ],
        },
        {
            "name": "교보증권  —  정희령",
            "summary": "전 증권사 중 최고 목표주가(700,000원) 유지. 에페글레나타이드 출시 1년차 1,000억원 달성에 가장 낙관적. 기술이전 유력 후보로 HM15275·HM17321 지목.",
            "rows": [
                ("2025.10.31", "BUY", "510,000↑", "3Q25 Review"),
                ("2026.02.26", "BUY", "700,000↑", "4Q25 Review. 높은 마진 성장률 입증. HM15275·HM17321 기술이전 유력"),
                ("2026.05.07", "BUY", "700,000 유지", "1Q26 Review. 에피노페그듀타이드 MSD 하반기 발표 예상. HM17321 ADA2026"),
            ],
        },
        {
            "name": "iM증권  —  정재원 (전임 장민환)",
            "summary": "분석가 교체(장민환→정재원) 후 분석 깊이 강화. 에페글레나타이드 rNPV 1조 6,624억원으로 가장 상세한 가정 공개. MASH 3상 가시화는 2028년이라는 가장 보수적 시각.",
            "rows": [
                ("2025.01.17", "Buy", "350,000↓", "장민환. 거버넌스 리스크 반영"),
                ("2025.10.31", "Buy", "460,000↑", "정재원(신규). 3Q25 Review. rNPV 에페글레나타이드 1조 6,624억원"),
                ("2026.02.06", "Buy", "630,000↑", "4Q25 Review. 정상화 궤도. MASH 3상 2028년 가능. EV/EBITDA 25.3배"),
            ],
        },
        {
            "name": "키움증권  —  허혜민",
            "summary": "2025.1 중립→매수 업그레이드 후 가장 빠른 재상향. 유일하게 2026.4 Buy→Outperform 하향(약가 개편 불확실성). 목표주가는 동시에 560,000원 상향 — 가치는 높으나 단기 모멘텀 부재 판단.",
            "rows": [
                ("2025.01.13", "Buy(Upgrade)", "330,000↓", "중립→매수 업그레이드. 거버넌스 완화 기대"),
                ("2025.10.28", "Buy", "스팟노트", "에페글레나타이드 3상 성공. BUY & HOLD 전략 유효"),
                ("2026.01.20", "Buy", "550,000↑", "4Q25 역대 최고 전망"),
                ("2026.04.13", "Outperform↓", "560,000↑", "약가개편 불확실성 + 단기 실적 부진. 의견 하향"),
            ],
        },
        {
            "name": "삼성증권  —  서근희/신수한",
            "summary": "에피노페그듀타이드 탑라인 결과 확인 전까지 신약 가치를 제한적으로만 반영하겠다는 신중론. SOTP 신약 가치 2조 3,132억원. Target EV/EBITDA 14배(보수적 적용).",
            "rows": [
                ("2025.07.11", "BUY(신규)", "400,000", "신규 커버리지. 2Q25 Preview"),
                ("2026.01.23", "BUY", "560,000↑", "4Q25 Preview. 에피노페그듀타이드 결과 전 제한적 반영. EV/EBITDA 14배"),
            ],
        },
        {
            "name": "대신증권  —  이희영",
            "summary": "가장 오랜 기간 380,000원 유지(보수적). 거버넌스 할인 해제를 공식 선언(2025.4)한 증권사. 에페글레나타이드 3상 성공 후 두 차례 연속 큰 폭 상향.",
            "rows": [
                ("2025.02.06", "BUY", "380,000 유지", "거버넌스 할인 지속 적용"),
                ("2025.04.16", "BUY", "380,000 유지", "1Q25 Preview. 거버넌스 할인 해제 공식 발표"),
                ("2025.10.16", "BUY", "450,000↑", "3Q25 Preview. 에페글레나타이드 3상 결과 임박"),
                ("2025.10.28", "BUY", "500,000↑", "에페글레나타이드 3상 성공에 긴급 상향"),
            ],
        },
        {
            "name": "신한투자증권  —  이호철/엄민용",
            "summary": "에포시페그트루타이드(MASH 삼중작용제)를 별도로 1,171억원 산정. MASH 경쟁 파이프라인 현황(3상 6개, 2상 6개) 분석이 가장 체계적.",
            "rows": [
                ("2026.01.21", "매수", "560,000 유지", "4Q25 Preview. 비영업가치 3,072억원 상세 산정"),
                ("2026.05.06", "매수", "560,000 유지", "1Q26 Review. HM15275 환자 모집 완료. HM17321 1b상 진입"),
            ],
        },
        {
            "name": "유진투자증권  —  권해순",
            "summary": "MASH 경쟁사 M&A(노보/아케로, 로슈/89바이오) 분석에 특화. 빅파마 M&A를 한미 에피노페그듀타이드 가치 상승의 간접 근거로 가장 적극 활용.",
            "rows": [
                ("2025.02.05", "BUY", "380,000↓", "거버넌스 리스크 반영"),
                ("2025.11.03", "BUY", "510,000↑", "3Q25 Review. MASH 경쟁 환경(노보/아케로, 로슈/89바이오 M&A) 상세 분석"),
            ],
        },
    ]

    for broker in brokers:
        elems.append(KeepTogether([
            sub_header(broker["name"]),
            SP(3),
            P(broker["summary"], "body"),
            SP(4),
            make_table(
                ["날짜", "의견", "목표주가", "핵심 주장"],
                broker["rows"],
                col_widths=[22*mm, 28*mm, 28*mm, TW-78*mm],
            ),
            SP(10),
        ]))

    elems.append(PageBreak())

    # ════════════════════════════════════════════════════════
    # 4. 시기별 분위기 변화
    # ════════════════════════════════════════════════════════
    elems += [section_header("4.  시기별 분위기 변화"), SP(8)]

    periods = [
        ("1기  |  2025년 1~2월", "비관 · 거버넌스 리스크 절정",
         LRED, RED,
         [
             "창업주 임종윤 vs. 한미사이언스 경영권 분쟁이 절정 → 대부분 증권사 목표주가 일제 하향",
             "미래에셋 20% 거버넌스 할인 독자 적용, 최저 330,000(키움)~380,000원(대신·DS·유진)",
             "키움증권 2025.1 중립→매수 업그레이드가 유일한 긍정 신호",
             "키워드: '거버넌스 리스크', '실적 둔화', '파이프라인 가치 재검토'",
         ]),
        ("2기  |  2025년 4~6월", "조심스러운 회복 · 거버넌스 완화 시작",
         LGREEN, GREEN,
         [
             "대신증권 2025.4 거버넌스 할인 해제 공식 발표 — 분쟁 완화 신호탄",
             "1Q25 실적 컨센서스 부합, 비만 임상 3상 일정 구체화",
             "하나증권 2025.6 신규 커버리지 개시 (400,000원), 비만·MASH 이중 모멘텀 본격 조명",
             "키워드: '정상화 시작', '2025년 하반기 모멘텀 대기'",
         ]),
        ("3기  |  2025년 7~8월", "안정적 대기 · 2Q25 실적 견조",
         LLBLUE, BLUE,
         [
             "삼성증권도 신규 커버리지 참여 — 커버리지 확대로 투자자 관심 증가",
             "2Q25 실적 컨센서스 부합, 북경한미 회복 가시화",
             "에피노페그듀타이드 2b상 진행 중 + 에페글레나타이드 3상 결과 임박 — 카탈리스트 대기",
             "키워드: '파이프라인 카탈리스트 대기', '북경한미 회복'",
         ]),
        ("4기  |  2025년 10~11월", "★ 강세 전환 — 에페글레나타이드 3상 성공",
         LGREEN, GREEN,
         [
             "2025.10.28 에페글레나타이드 국내 3상 탑라인 성공 발표 — 결정적 카탈리스트",
             "모든 커버리지 증권사 목표주가 대폭 상향: 360~420,000원대 → 500~510,000원대",
             "3Q25 Review도 견조한 실적 확인 + MASH 경쟁사 M&A로 에피노페그듀타이드 가치 재확인",
             "키워드: '비만 치료제 상업화', '리레이팅 가능성', '국내 유일 희소성'",
         ]),
        ("5기  |  2026년 1월", "기대감 고조 · JPM 헬스케어 컨퍼런스",
         LLBLUE, BLUE,
         [
             "4Q25 역대 최고 실적 예상, JPM 헬스케어에서 MSD 에피노페그듀타이드 언급 모니터링",
             "목표주가 520,000(iM)~560,000원(신한·삼성)대로 추가 상향",
             "EASL(5월) 에피노페그듀타이드 발표 가능성 제기 시작",
             "키워드: '비만+MASH 이중 모멘텀', '4Q25 실적 역대 최고 전망'",
         ]),
        ("6기  |  2026년 2~3월", "★★ 강세 절정 — 목표주가 최고치",
         LGREEN, GREEN,
         [
             "4Q25 영업이익 833억원 (+173%) 확인 — 컨센서스 이익 +18% 대폭 상회",
             "미래에셋 350,000→660,000원 (+310,000원 단번 상향) 상징적. 평균 목표가 630,000원대",
             "거버넌스 할인 완전 해제 + 실적 정상화 + 파이프라인 재평가 3중 효과 확인",
             "키워드: '리레이팅 국면 진입', '에페글레나타이드 출시 원년', '연간 기술이전 1건 이상'",
         ]),
        ("7기  |  2026년 4~5월", "숨 고르기 · 역기저효과 + 발표 지연",
         LRED, RED,
         [
             "1Q26 영업이익 536억원 (-9.1% YoY) — MSD 임상시료 역기저효과로 컨센서스 하회",
             "에피노페그듀타이드 EASL 초록 리스트 부재 → MSD 하반기 학회로 발표 지연",
             "키움증권 유일하게 Buy→Outperform 하향. 주가 440,000원대로 조정 (52주 최고 626,000 대비)",
             "키워드: '잠잠한 상반기, 뜨거울 하반기'(신한), '기다리면 다 나온다'(교보)",
         ]),
    ]

    for period_title, mood, bg, border, bullets in periods:
        items = [
            P(f"<b>{period_title}</b>", "h3"),
            P(f"분위기: <b>{mood}</b>", "bodyb"),
            SP(3),
        ]
        for btext in bullets:
            items.append(B(btext))
        items.append(SP(2))
        inner = Table([[i] for i in items], colWidths=[TW-20])
        inner.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),
                                   ("TOPPADDING",(0,0),(-1,-1),0),
                                   ("BOTTOMPADDING",(0,0),(-1,-1),0)]))
        elems += [box(inner, bg=bg, border_color=border, pad=10), SP(6)]

    elems.append(PageBreak())

    # ════════════════════════════════════════════════════════
    # 5. 컨센서스 & 향후 이벤트
    # ════════════════════════════════════════════════════════
    elems += [section_header("5.  현재 컨센서스 및 향후 핵심 이벤트"), SP(8)]

    elems += [P("▶  2026년 5월 현재 증권사 컨센서스", "h3"), SP(4)]
    consensus_rows = [
        ("교보증권",      "정희령",        "BUY",         "700,000원"),
        ("DS투자증권",    "김민정",        "매수",         "680,000원"),
        ("미래에셋증권",  "김승민",        "매수",         "660,000원"),
        ("하나증권",      "김선아",        "BUY",          "640,000원"),
        ("iM증권",        "정재원",        "Buy",          "630,000원"),
        ("신한투자증권",  "이호철/엄민용", "매수",         "560,000원"),
        ("삼성증권",      "서근희/신수한", "BUY",          "560,000원"),
        ("키움증권",      "허혜민",        "Outperform",   "560,000원"),
        ("대신증권",      "이희영",        "BUY",          "500,000원"),
        ("유진투자증권",  "권해순",        "BUY",          "510,000원"),
        ("IBK투자증권",   "정이수",        "매수",         "530,000원"),
    ]
    elems += [make_table(
        ["증권사", "애널리스트", "투자의견", "목표주가"],
        consensus_rows,
        col_widths=[40*mm, 38*mm, 28*mm, 28*mm],
    ), SP(6)]

    elems += [box(
        P("전원 매수 의견  |  평균 목표주가 약 <b>611,000원</b>  |  현재주가(2026.05) 대비 상승여력 약 <b>40%</b>",
          "bodyb"),
        bg=LLBLUE, border_color=BLUE
    ), SP(12)]

    elems += [P("▶  2026년 하반기 핵심 카탈리스트", "h3"), SP(4)]
    events = [
        ("★★★", "에피노페그듀타이드 2b상 탑라인 발표",
         "MSD(파트너사)가 2026년 하반기 학회(AASLD·ESMO 등)에서 발표 예정. 가장 중요한 주가 촉매. 긍정 시 목표주가 추가 상향 여지."),
        ("★★",  "에페글레나타이드 국내 출시 (4Q26)",
         "식약처 허가 신청 완료(2025.12). 출시 1년차 목표 매출 1,000억원. 국내 비만 시장 2026년 약 7,000억원 전망."),
        ("★★",  "기술이전(L/O) 1건 이상 체결",
         "2026년 회사 가이던스. HM15275(미국 2상 진행) 또는 HM17321(1b상) 유력 후보."),
        ("★",   "에포시페그트루타이드 2b상 결과",
         "자체 개발 MASH 삼중작용제. 2026년 하반기 발표 예정."),
        ("★",   "HM17321 1b상 데이터",
         "UCN2 근육보존형 비만 치료제. ADA2026 전임상 데이터 발표 예정."),
    ]
    event_data = [[P(imp,"bodyb"), P(title,"bodyb"), P(desc,"body")]
                  for imp, title, desc in events]
    event_tbl = Table(event_data, colWidths=[14*mm, 60*mm, TW-74*mm])
    event_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,-1), YELLOW),
        ("BACKGROUND",   (1,0), (1,-1), LLBLUE),
        ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#B0B0B0")),
        ("ALIGN",        (0,0), (0,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),
         [YELLOW, colors.HexColor("#FFF9E6")]*3),
    ]))
    elems += [event_tbl, SP(8)]
    elems += [P("※ 분석 기준일: 2026.05.07  |  본 자료는 증권사 리서치 리포트(65개)를 기반으로 작성된 요약본입니다.",
                "note")]
    return elems

# ── PDF 생성 ──────────────────────────────────────────────────────────────────
OUT = os.path.join(os.path.dirname(__file__), "한미약품_애널리스트_분석보고서.pdf")

def build_pdf():
    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        title="한미약품 애널리스트 리포트 종합 분석",
        author="Research Analysis",
    )
    story = cover_page() + content()
    doc.build(story)
    print(f"저장 완료: {OUT}")

if __name__ == "__main__":
    build_pdf()
