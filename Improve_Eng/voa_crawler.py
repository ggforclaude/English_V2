"""
VOA Learning English crawler - 매일 Level 1~3 콘텐츠 수집
"""
import asyncio
import feedparser
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

# VOA Learning English RSS feeds (Level별)
VOA_RSS_URLS = {
    "level1": "https://www.voaspecialenglish.com/api/p/v1/rss/ctee-level-1",
    "level2": "https://www.voaspecialenglish.com/api/p/v1/rss/ctee-level-2",
    "level3": "https://www.voaspecialenglish.com/api/p/v1/rss/ctee-level-3",
}


async def fetch_voa_daily_content(today_date=None) -> dict:
    """
    VOA Learning English에서 오늘의 콘텐츠 가져오기.
    Level 1 우선, 없으면 Level 2, Level 3 순서로 시도.

    Returns:
    {
        "title": str,
        "text": str,
        "audio_url": str,
        "source": "VOA Learning English",
        "level": "Level 1" | "Level 2" | "Level 3",
        "link": str,
    }
    """
    for level_name, rss_url in VOA_RSS_URLS.items():
        try:
            log.info(f"[VOA] Fetching {level_name} from {rss_url}")
            feed = feedparser.parse(rss_url)

            if not feed.entries:
                log.warning(f"[VOA] No entries found for {level_name}")
                continue

            # 최신 항목 선택
            entry = feed.entries[0]

            title = entry.get("title", "VOA Learning English")
            content = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")

            # 오디오 URL 추출 (enclosure 또는 media_content에서)
            audio_url = ""
            if hasattr(entry, "enclosures"):
                for enc in entry.enclosures:
                    if "audio" in enc.type:
                        audio_url = enc.href
                        break

            if not audio_url and hasattr(entry, "media_content"):
                for media in entry.media_content:
                    if "audio" in media.get("type", ""):
                        audio_url = media.get("url", "")
                        break

            # 학위 레벨 추출
            level_num = level_name.split("level")[-1]
            level_text = f"Level {level_num}"

            result = {
                "title": title,
                "text": content[:500],  # 요약본
                "audio_url": audio_url,
                "source": "VOA Learning English",
                "level": level_text,
                "link": link,
                "fetched_at": str(datetime.now()),
            }

            log.info(f"[VOA] Successfully fetched {level_name}: {title}")
            return result

        except Exception as e:
            log.warning(f"[VOA] Failed to fetch {level_name}: {e}")
            continue

    # 모든 시도 실패
    log.error("[VOA] Could not fetch from any VOA level")
    return {
        "title": "VOA Learning English (Fallback)",
        "text": "Daily English learning from Voice of America.",
        "audio_url": "",
        "source": "VOA Learning English",
        "level": "Level 1",
        "link": "https://www.voaspecialenglish.com",
        "fetched_at": str(datetime.now()),
    }


def extract_key_vocabulary(text: str, n: int = 10) -> list[str]:
    """텍스트에서 핵심 단어 추출"""
    import re
    from collections import Counter

    # 단어 추출 (영문만)
    words = re.findall(r'\b[a-z]+\b', text.lower())

    # 불용어 제거
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'it', 'its', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'we', 'they', 'as', 'if', 'than',
    }

    filtered = [w for w in words if w not in stopwords and len(w) > 3]

    # 빈도 계산
    counter = Counter(filtered)
    return [word for word, _ in counter.most_common(n)]
