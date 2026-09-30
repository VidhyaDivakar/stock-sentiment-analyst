"""yfinance wrapper: validate tickers and fetch recent news headlines."""
import yfinance as yf


class NewsFetchError(Exception):
    """Raised when news could not be retrieved (network/API problem)."""


def is_valid_ticker(ticker: str) -> bool:
    """Basic check before spending a network/LLM call on garbage input."""
    ticker = ticker.strip().upper()
    if not ticker:
        return False
    # Allow '.' and '-' for tickers like BRK-B / BF.B
    if not ticker.replace(".", "").replace("-", "").isalpha():
        return False
    return len(ticker) <= 6


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
    try:
        news_items = yf.Ticker(ticker.strip().upper()).news or []
    except Exception as e:
        raise NewsFetchError(f"Could not fetch news for {ticker}: {e}") from e

    headlines = []
    for item in news_items:
        title = ((item or {}).get("content") or {}).get("title")
        if title and title.strip():
            headlines.append(title.strip())
        if len(headlines) >= max_items:
            break
    return headlines
