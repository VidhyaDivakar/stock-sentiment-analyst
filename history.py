"""Recent searches, kept in a small local JSON file so they survive restarts."""
import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "recent_searches.json"
MAX_RECENT = 10


def load_recent(path: Path = HISTORY_FILE) -> list[dict]:
    """Return saved searches, newest first; empty list if the file is missing or unreadable."""
    try:
        items = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict) and i.get("ticker")]


def add_recent(ticker: str, label: str, path: Path = HISTORY_FILE) -> list[dict]:
    """Put this search at the top (one entry per ticker) and keep the latest MAX_RECENT."""
    symbol = ticker.strip().upper()
    items = [i for i in load_recent(path) if i["ticker"] != symbol]
    items.insert(0, {"ticker": symbol, "label": label, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
    items = items[:MAX_RECENT]
    try:
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    except OSError:
        pass  # History is a convenience; never fail an analysis over it.
    return items
