import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "bot_data.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS keywords (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword  TEXT UNIQUE NOT NULL,
                added_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS watchlist (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                ticker   TEXT NOT NULL,
                market   TEXT NOT NULL,
                added_at TEXT NOT NULL,
                UNIQUE(ticker, market)
            );
        """)
        now = datetime.now().isoformat()
        for kw in ["반도체", "AI 투자", "미국 증시", "환율"]:
            c.execute(
                "INSERT OR IGNORE INTO keywords (keyword, added_at) VALUES (?, ?)",
                (kw, now),
            )
        for name, ticker, market in [
            ("삼성전자", "005930", "KR"),
            ("SK하이닉스", "000660", "KR"),
            ("NVIDIA", "NVDA", "US"),
            ("Apple", "AAPL", "US"),
        ]:
            c.execute(
                "INSERT OR IGNORE INTO watchlist (name, ticker, market, added_at) VALUES (?, ?, ?, ?)",
                (name, ticker, market, now),
            )
        c.commit()


# ── keywords ──────────────────────────────────────────────────────────────────

def get_keywords() -> list[str]:
    with _conn() as c:
        return [r[0] for r in c.execute("SELECT keyword FROM keywords ORDER BY id")]


def add_keyword(kw: str) -> bool:
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO keywords (keyword, added_at) VALUES (?, ?)",
                (kw, datetime.now().isoformat()),
            )
            c.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def del_keyword(kw: str) -> bool:
    with _conn() as c:
        cur = c.execute("DELETE FROM keywords WHERE keyword = ?", (kw,))
        c.commit()
        return cur.rowcount > 0


# ── watchlist ──────────────────────────────────────────────────────────────────

def get_watchlist() -> list[dict]:
    with _conn() as c:
        return [
            {"name": r[0], "ticker": r[1], "market": r[2]}
            for r in c.execute(
                "SELECT name, ticker, market FROM watchlist ORDER BY market, name"
            )
        ]


def add_stock(name: str, ticker: str, market: str) -> bool:
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO watchlist (name, ticker, market, added_at) VALUES (?, ?, ?, ?)",
                (name, ticker, market.upper(), datetime.now().isoformat()),
            )
            c.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def del_stock(ticker: str, market: str) -> bool:
    with _conn() as c:
        cur = c.execute(
            "DELETE FROM watchlist WHERE ticker = ? AND market = ?",
            (ticker, market.upper()),
        )
        c.commit()
        return cur.rowcount > 0
