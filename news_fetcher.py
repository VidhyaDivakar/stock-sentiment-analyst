"""yfinance wrapper: validate tickers and fetch recent news headlines."""
import re

import yfinance as yf
from yfinance.data import YfData


class NewsFetchError(Exception):
    """Raised when news could not be retrieved (network/API problem)."""


def is_valid_ticker(ticker: str) -> bool:
    """Basic check before spending a network/LLM call on garbage input."""
    ticker = ticker.strip().upper()
    if not ticker:
        return False
    # Allow '.' and '-' for tickers like BRK-B / BF.B / BTC-USD, and a leading '^' for indexes like ^IXIC
    if not ticker.removeprefix("^").replace(".", "").replace("-", "").isalpha():
        return False
    return len(ticker) <= 10


def ticker_exists(ticker: str) -> bool:
    """True if yfinance has recent price data for the ticker.

    Only used after no headlines were found, to tell "unknown ticker" apart from
    "real ticker, no news". On a network/API error we can't tell, so assume it exists.
    """
    try:
        return not yf.Ticker(ticker.strip().upper()).history(period="1mo").empty
    except Exception:
        return True


# Words that say nothing about which company a name belongs to.
_NAME_SUFFIXES = {
    "the", "and", "&", "inc", "incorporated", "corp", "corporation", "company", "co", "com", "ltd",
    "plc", "sa", "s", "a", "nv", "ag", "group", "holdings", "holding", "platforms", "technologies",
    "class", "usd", "composite",
}
_GENERIC_WORDS = {
    "general", "american", "america", "united", "national", "international", "first", "new", "of",
    "bank", "banco", "advanced", "micro", "devices", "business", "machines", "motor", "motors",
    "air", "lines", "airlines", "energy", "home", "health",
}
SEARCH_NEWS_COUNT = 30


def _about_pattern(symbol: str, name: str = "") -> re.Pattern | None:
    """Regex matching a headline that names this ticker or its company, or None if nothing to match on.

    "General Motors Company" (GM) matches "GM" and "General Motors" but not "General Electric".
    """
    base = symbol.removeprefix("^")
    tickers = {base, re.split(r"[-.]", base)[0]}
    parts = [re.escape(t) for t in tickers if len(t) >= 2]  # one-letter tickers match too much

    words = [w for w in re.findall(r"[a-z0-9&'-]+", name.lower()) if w not in _NAME_SUFFIXES]
    names = [w for w in words if len(w) >= 3 and not w.isdigit() and w not in _GENERIC_WORDS]
    if len(words) > 1:
        names += [" ".join(words), "".join(words)]  # "exxon mobil" and "exxonmobil"
    parts += [f"(?i:{re.escape(n)})" for n in names]

    if not parts:
        return None
    return re.compile(r"(?<![A-Za-z0-9])(?:%s)(?![A-Za-z0-9])" % "|".join(parts))


def _company_name(quotes, symbol: str) -> str:
    for quote in quotes or []:
        if isinstance(quote, dict) and quote.get("symbol") == symbol:
            return quote.get("longname") or quote.get("shortname") or ""
    return ""


def get_headlines(ticker: str, max_items: int = 5) -> list[str]:
    """Return up to max_items recent headline strings; empty list if none/unknown ticker."""
    symbol = ticker.strip().upper()
    name = ""
    try:
        news_items = yf.Ticker(symbol).news or []
        titles = [((item or {}).get("content") or {}).get("title") for item in news_items]
        candidates = titles
        if not any(titles):
            # Yahoo's per-ticker news endpoint sometimes returns nothing; its search
            # endpoint still has news, but loosely matched, so keep only items tagged
            # with this ticker.
            # yfinance caches search responses for the life of the process, which would
            # freeze the headlines until the app restarts.
            YfData.cache_get.cache_clear()
            search = yf.Search(symbol, news_count=SEARCH_NEWS_COUNT)
            search_items = search.news or []
            name = _company_name(search.quotes, symbol)
            titles = [
                (item or {}).get("title")
                for item in search_items
                if symbol in ((item or {}).get("relatedTickers") or [])
            ]
            # Yahoo tags some companies' news with a sibling share class only (BBD's
            # stories are tagged BBDO), so for a real ticker take the untagged results.
            if not any(titles) and search_items and ticker_exists(symbol):
                titles = [(item or {}).get("title") for item in search_items]
            # Yahoo naming the company means the ticker is real, so every search result
            # can be checked for it, tagged or not.
            candidates = [(item or {}).get("title") for item in search_items] if name else titles
    except Exception as e:
        raise NewsFetchError(f"Could not fetch news for {ticker}: {e}") from e

    def clean(items):
        return [t.strip() for t in items if t and t.strip()]

    # Yahoo links a story to a ticker even when the company is only mentioned in passing,
    # so keep the headlines that name the company; if none do, keep what Yahoo sent.
    pattern = _about_pattern(symbol, name)
    on_topic = [h for h in clean(candidates) if pattern and pattern.search(h)]
    return (on_topic or clean(titles))[:max_items]
