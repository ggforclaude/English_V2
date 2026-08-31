"""
Google Sheets 관리 - v2 새 커리큘럼용
Learning_v2 시트에 데이터 저장
"""
import os
import logging
from datetime import date
from typing import Optional, List

log = logging.getLogger(__name__)

# 새로운 시트 구조
SHEET_LEARNING_V2 = "Learning_v2"  # 새로운 학습 데이터 시트
SHEET_VOA_CACHE = "VOA_Cache"     # VOA 콘텐츠 캐시
SHEET_WEAK_POINTS = "Weak_Points" # 약점 분석 결과

# Learning_v2 시트 컬럼
V2_COLUMNS = [
    "date",           # A: 날짜
    "day_number",     # B: Day 넘버
    "vocab_due",      # C: Anki 복습 카드 수
    "vocab_new",      # D: Anki 신규 카드
    "grammar_topic",  # E: 문법 주제
    "listening_title", # F: VOA 제목
    "listening_level", # G: VOA 레벨
    "output_topic",   # H: 출력(에세이) 주제
    "reading_recommend", # I: 다독 추천 도서
    "questions_correct", # J: 정답 수
    "questions_total",   # K: 총 문제 수
    "accuracy_pct",      # L: 정확도 %
    "level_listening",   # M: 듣기 레벨
    "level_grammar",     # N: 문법 레벨
    "notes",             # O: 메모
]

# VOA_Cache 시트 컬럼
VOA_COLUMNS = [
    "date",
    "level",
    "title",
    "audio_url",
    "text_summary",
    "link",
]

# Weak_Points 시트 컬럼
WEAK_COLUMNS = [
    "analysis_date",
    "domain",
    "weakness",
    "error_rate",
    "error_count",
    "supplemental_generated",
]


class SheetsManagerV2:
    """
    Google Sheets API를 통해 v2 학습 데이터를 관리합니다.
    """

    def __init__(self):
        self.sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
        self._service = None
        self._init_sheets()

    def _init_sheets(self):
        """Google Sheets API 초기화"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            # 서비스 계정 인증
            creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "active-cable-494902-q1-e70695e40677.json")
            if os.path.exists(creds_path):
                creds = service_account.Credentials.from_service_account_file(creds_path)
                self._service = build("sheets", "v4", credentials=creds)
                log.info(f"[Sheets] Initialized with {creds_path}")
            else:
                log.warning("[Sheets] Credentials file not found")
        except Exception as e:
            log.error(f"[Sheets] Initialization failed: {e}")

    async def save_daily_learning(
        self,
        today: date,
        day_number: int,
        anki_stats: dict,
        grammar_content: dict,
        voa_content: dict,
        output_topic: str,
        reading_rec: str,
        questions_correct: int,
        questions_total: int,
        levels: dict,
    ) -> bool:
        """
        오늘의 학습 정보를 Learning_v2 시트에 저장.
        """
        if not self._service or not self.sheet_id:
            log.warning("[Sheets] Service not initialized, skipping save")
            return False

        try:
            accuracy = (questions_correct / questions_total * 100) if questions_total > 0 else 0

            row = [
                str(today),  # A: date
                str(day_number),  # B: day_number
                str(anki_stats.get("today", {}).get("total_due", 0)),  # C: vocab_due
                str(anki_stats.get("today", {}).get("new_cards", 0)),  # D: vocab_new
                grammar_content.get("topic", "")[:50],  # E: grammar_topic
                voa_content.get("title", "")[:50],  # F: listening_title
                voa_content.get("level", "Level 1"),  # G: listening_level
                output_topic[:50],  # H: output_topic
                reading_rec[:50],  # I: reading_recommend
                str(questions_correct),  # J: questions_correct
                str(questions_total),  # K: questions_total
                f"{accuracy:.1f}",  # L: accuracy_pct
                levels.get("listening", "B1"),  # M: level_listening
                levels.get("grammar", "B1"),  # N: level_grammar
                "",  # O: notes
            ]

            # Append 방식으로 저장
            self._service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f"{SHEET_LEARNING_V2}!A:O",
                valueInputOption="USER_ENTERED",
                body={"values": [row]},
            ).execute()

            log.info(f"[Sheets] Saved learning data for {today}")
            return True

        except Exception as e:
            log.error(f"[Sheets] Failed to save learning data: {e}")
            return False

    async def cache_voa_content(
        self,
        today: date,
        level: str,
        title: str,
        audio_url: str,
        text_summary: str,
        link: str,
    ) -> bool:
        """
        VOA 콘텐츠를 캐시하여 나중에 참조 가능하도록 저장.
        """
        if not self._service or not self.sheet_id:
            return False

        try:
            row = [
                str(today),
                level,
                title[:100],
                audio_url,
                text_summary[:200],
                link,
            ]

            self._service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f"{SHEET_VOA_CACHE}!A:F",
                valueInputOption="USER_ENTERED",
                body={"values": [row]},
            ).execute()

            log.info(f"[Sheets] Cached VOA content for {today}")
            return True

        except Exception as e:
            log.error(f"[Sheets] Failed to cache VOA content: {e}")
            return False

    async def save_weak_points(
        self,
        analysis_date: date,
        weak_areas: List[dict],
    ) -> bool:
        """
        약점 분석 결과를 Weak_Points 시트에 저장.
        """
        if not self._service or not self.sheet_id:
            return False

        try:
            rows = []
            for area in weak_areas[:5]:  # 상위 5개만 저장
                row = [
                    str(analysis_date),
                    area.get("domain", ""),
                    area.get("weakness", "")[:100],
                    f"{area.get('error_rate', 0):.1%}",
                    str(area.get("error_count", 0)),
                    "✓",  # supplemental_generated
                ]
                rows.append(row)

            if rows:
                self._service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id,
                    range=f"{SHEET_WEAK_POINTS}!A:F",
                    valueInputOption="USER_ENTERED",
                    body={"values": rows},
                ).execute()

                log.info(f"[Sheets] Saved {len(rows)} weak points for {analysis_date}")
                return True

        except Exception as e:
            log.error(f"[Sheets] Failed to save weak points: {e}")
            return False

    async def get_learning_history(self, days: int = 30) -> List[dict]:
        """
        Learning_v2 시트에서 최근 N일간의 학습 기록 조회.
        """
        if not self._service or not self.sheet_id:
            return []

        try:
            result = self._service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{SHEET_LEARNING_V2}!A:O",
            ).execute()

            rows = result.get("values", [])[1:]  # 헤더 제외

            history = []
            for row in rows[-days:]:  # 최근 N개 행
                if len(row) >= 15:
                    history.append({
                        "date": row[0],
                        "day_number": int(row[1]) if row[1] else 0,
                        "accuracy": float(row[11]) if row[11] else 0,
                        "questions_correct": int(row[9]) if row[9] else 0,
                        "questions_total": int(row[10]) if row[10] else 0,
                    })

            return history

        except Exception as e:
            log.error(f"[Sheets] Failed to get learning history: {e}")
            return []


# 싱글톤 인스턴스
_sheets_v2 = None


async def get_sheets_manager():
    """Google Sheets 관리자 (싱글톤)"""
    global _sheets_v2
    if _sheets_v2 is None:
        _sheets_v2 = SheetsManagerV2()
    return _sheets_v2
