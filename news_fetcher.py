"""yfinance wrapper: validate tickers and fetch recent news headlines."""
import yfinance as yf


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


def get_headlines(ticker: str, max_items: int = 5) -> list[str]:
    """Return up to max_items recent headline strings; empty list if none/unknown ticker."""
    symbol = ticker.strip().upper()
    try:
        news_items = yf.Ticker(symbol).news or []
        titles = [((item or {}).get("content") or {}).get("title") for item in news_items]
        if not any(titles):
            # Yahoo's per-ticker news endpoint sometimes returns nothing; its search
            # endpoint still has news, but loosely matched, so keep only items tagged
            # with this ticker.
            search_items = yf.Search(symbol, news_count=max(max_items, 10)).news or []
            titles = [
                (item or {}).get("title")
                for item in search_items
                if symbol in ((item or {}).get("relatedTickers") or [])
            ]
            # Yahoo tags some companies' news with a sibling share class only (BBD's
            # stories are tagged BBDO), so for a real ticker take the untagged results.
            if not any(titles) and search_items and ticker_exists(symbol):
                titles = [(item or {}).get("title") for item in search_items]
    except Exception as e:
        raise NewsFetchError(f"Could not fetch news for {ticker}: {e}") from e

    headlines = [t.strip() for t in titles if t and t.strip()]
    return headlines[:max_items]
