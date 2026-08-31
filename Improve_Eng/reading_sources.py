"""
다독(읽기) 콘텐츠 자동 추천
BBC News, Medium, Reddit 등에서 학습자 친화적인 아티클 추천
"""
import feedparser
import requests
import logging
from datetime import date
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


async def fetch_daily_reading_article() -> dict:
    """학습자 친화적인 영문 아티클 추천."""

    sources = [
        {
            "name": "BBC Learning English",
            "rss": "https://feeds.bbci.co.uk/learningenglish/english/features/lingohack/rss.xml"
        },
        {
            "name": "VOA Learning English",
            "rss": "https://learningenglish.voanews.com/api/zovijqmz_q"
        },
        {
            "name": "BBC News - Learning English",
            "rss": "https://feeds.bbci.co.uk/learningenglish/rss.xml"
        },
    ]

    for source in sources:
        try:
            feed = feedparser.parse(source["rss"])
            if feed.entries:
                entry = feed.entries[0]
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")

                if title and link:
                    text = BeautifulSoup(summary, "lxml").get_text()[:300] if summary else ""

                    return {
                        "source": source["name"],
                        "title": title,
                        "url": link,
                        "summary": text,
                        "level": "B1",
                    }
        except Exception as e:
            log.warning(f"Failed to fetch from {source['name']}: {e}")
            continue

    return {
        "source": "BBC Learning English",
        "title": "Daily Reading Article",
        "url": "https://www.bbc.co.uk/learningenglish",
        "summary": "BBC Learning English 웹사이트 방문",
        "level": "B1",
    }


async def fetch_free_books() -> list:
    """저작권 없는 무료 고전 소설 추천 (Project Gutenberg)."""

    popular_books = [
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "level": "B2",
            "url": "https://www.gutenberg.org/ebooks/1342",
            "description": "사랑과 사회 풍자를 다룬 영국 고전 소설"
        },
        {
            "title": "Sherlock Holmes Stories",
            "author": "Arthur Conan Doyle",
            "level": "B1",
            "url": "https://www.gutenberg.org/ebooks/1661",
            "description": "추리 소설의 고전, 단편으로 읽기 좋음"
        },
        {
            "title": "Alice's Adventures in Wonderland",
            "author": "Lewis Carroll",
            "level": "A2",
            "url": "https://www.gutenberg.org/ebooks/11",
            "description": "초급 학습자도 읽을 수 있는 환상 소설"
        },
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "level": "B2",
            "url": "https://www.gutenberg.org/ebooks/4270",
            "description": "1920년대 미국 사회를 배경으로 한 고전 문학"
        },
        {
            "title": "Wuthering Heights",
            "author": "Emily Brontë",
            "level": "B2",
            "url": "https://www.gutenberg.org/ebooks/768",
            "description": "감정적이고 드라마틱한 영국 소설"
        },
    ]

    return popular_books


async def fetch_daily_free_article() -> dict:
    """무료 온라인 아티클 (뉴스, 블로그 등)."""

    sources = [
        {
            "name": "BBC News - Learning English",
            "url": "https://www.bbc.co.uk/learningenglish/english/features/news-report"
        },
        {
            "name": "The Guardian - Essential English",
            "url": "https://www.theguardian.com/"
        },
        {
            "name": "Medium - English Learning",
            "url": "https://medium.com/tag/english-language"
        },
    ]

    article = sources[date.today().day % len(sources)]

    return {
        "title": "Today's Reading Topic",
        "source": article["name"],
        "url": article["url"],
        "level": "B1",
        "description": "웹사이트에서 흥미로운 아티클 선택해서 읽기"
    }
