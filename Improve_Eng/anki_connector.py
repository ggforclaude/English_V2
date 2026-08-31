"""
Anki 덱 연결 - NGSL 빈도순 단어 학습
간격 반복(SRS) 기반 복습 일정 조회 및 진행률 추적
"""
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List

log = logging.getLogger(__name__)

# AnkiDroid / AnkiWeb 동기화를 위한 기본 설정
ANKI_CONFIG = {
    "deck_name": "NGSL 빈도순 2800단어",
    "model_name": "기본",
}


class AnkiConnector:
    """
    Anki 덱과의 연결을 관리하는 클래스.
    AnkiConnect (로컬) 또는 AnkiWeb API를 통해 통신.
    """

    def __init__(self):
        # AnkiConnect URL (기본값: 로컬)
        self.anki_url = os.environ.get("ANKI_CONNECT_URL", "http://localhost:8765")
        self.deck_name = ANKI_CONFIG["deck_name"]
        self.is_available = False
        self._check_anki_availability()

    def _check_anki_availability(self):
        """AnkiConnect 서버 가용성 확인"""
        try:
            import requests
            response = requests.post(
                self.anki_url,
                json={"action": "version", "version": 6},
                timeout=2
            )
            self.is_available = response.status_code == 200
            if self.is_available:
                log.info(f"[Anki] AnkiConnect connected at {self.anki_url}")
            else:
                log.warning("[Anki] AnkiConnect available but version check failed")
        except Exception as e:
            log.warning(f"[Anki] AnkiConnect not available: {e}")
            self.is_available = False

    async def get_today_cards(self) -> dict:
        """
        오늘의 복습 카드 정보 조회.

        Returns:
        {
            "total_due": int,      # 오늘 복습해야 할 카드 수
            "new_cards": int,      # 신규 카드
            "learning": int,       # 학습 중인 카드
            "review": int,         # 복습 카드
            "due_dates": [str],    # 앞으로의 복습 일정 (다음 7일)
            "status": "connected" | "offline",
        }
        """
        if not self.is_available:
            return self._get_offline_schedule()

        try:
            import requests
            from datetime import date, datetime as dt

            # Anki의 현재 복습 상태 조회
            deck_stats = self._call_anki("getDeckStats", {"decks": [self.deck_name]})

            if not deck_stats:
                return self._get_offline_schedule()

            stats = deck_stats.get(self.deck_name, {})

            return {
                "total_due": stats.get("due", 0),
                "new_cards": stats.get("new", 0),
                "learning": stats.get("learning", 0),
                "review": stats.get("review", 0),
                "due_dates": self._generate_due_dates(),
                "status": "connected",
                "last_sync": str(datetime.now()),
            }
        except Exception as e:
            log.warning(f"[Anki] Failed to get cards: {e}")
            return self._get_offline_schedule()

    def _get_offline_schedule(self) -> dict:
        """오프라인 상태에서의 기본 복습 일정"""
        return {
            "total_due": 0,
            "new_cards": 20,  # 기본 신규 카드 20개
            "learning": 5,
            "review": 10,
            "due_dates": self._generate_due_dates(),
            "status": "offline",
            "message": "Anki not connected. Using default schedule.",
        }

    def _generate_due_dates(self) -> List[str]:
        """향후 7일간의 예상 복습 일정"""
        from datetime import date
        schedule = []
        for i in range(1, 8):
            future_date = date.today() + timedelta(days=i)
            schedule.append(str(future_date))
        return schedule

    def _call_anki(self, action: str, params: dict):
        """AnkiConnect RPC 호출"""
        try:
            import requests
            payload = {"action": action, "version": 6, **params}
            response = requests.post(self.anki_url, json=payload, timeout=5)
            result = response.json()
            if result.get("error"):
                log.error(f"[Anki] Error: {result['error']}")
                return None
            return result.get("result")
        except Exception as e:
            log.error(f"[Anki] RPC failed: {e}")
            return None

    def get_ngsl_progress(self) -> dict:
        """
        NGSL 2,800 단어 학습 진도율 조회.

        Returns:
        {
            "total_words": 2800,
            "learned": int,      # 학습 완료
            "learning": int,     # 학습 중
            "not_started": int,  # 시작 전
            "progress_pct": float,
        }
        """
        if not self.is_available:
            return {
                "total_words": 2800,
                "learned": 0,
                "learning": 0,
                "not_started": 2800,
                "progress_pct": 0.0,
                "status": "offline"
            }

        try:
            # AnkiConnect에서 카드 상태 조회
            cards = self._call_anki("findCards", {"query": f"deck:{self.deck_name}"})
            if not cards:
                return self._offline_ngsl_progress()

            total = len(cards)
            card_stats = self._call_anki("cardsInfo", {"cards": cards[:100]})  # 샘플링

            learned = sum(1 for c in card_stats if c.get("reps", 0) > 5)
            learning = sum(1 for c in card_stats if 0 < c.get("reps", 0) <= 5)

            return {
                "total_words": 2800,
                "learned": (learned * total) // 100,  # 추정
                "learning": (learning * total) // 100,
                "not_started": total - (learned + learning) * total // 100,
                "progress_pct": (learned / 100) * 100,
                "status": "connected"
            }
        except Exception as e:
            log.warning(f"[Anki] Failed to get NGSL progress: {e}")
            return self._offline_ngsl_progress()

    def _offline_ngsl_progress(self) -> dict:
        """오프라인 NGSL 진도율"""
        return {
            "total_words": 2800,
            "learned": 0,
            "learning": 0,
            "not_started": 2800,
            "progress_pct": 0.0,
            "status": "offline"
        }


# 싱글톤 인스턴스
_anki = None


async def get_anki_stats():
    """Anki 통계 조회 (싱글톤)"""
    global _anki
    if _anki is None:
        _anki = AnkiConnector()

    today_cards = await _anki.get_today_cards()
    ngsl_progress = _anki.get_ngsl_progress()

    return {
        "today": today_cards,
        "ngsl": ngsl_progress,
        "recommendation": _get_study_recommendation(today_cards, ngsl_progress),
    }


def _get_study_recommendation(today_stats: dict, ngsl_stats: dict) -> str:
    """학습 추천"""
    total_due = today_stats.get("total_due", 0)

    if ngsl_stats["progress_pct"] < 10:
        return "단어 학습을 시작하세요. 매일 20~30개의 새 단어로 시작하는 것이 좋습니다."
    elif total_due > 50:
        return f"오늘 {total_due}개의 복습이 있습니다. Anki 앱에서 학습을 진행하세요."
    elif total_due == 0:
        return "오늘의 복습이 모두 완료되었습니다! 내일을 기대하세요."
    else:
        return f"오늘 {total_due}개의 복습이 남아있습니다."
