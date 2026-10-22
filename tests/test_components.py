from unittest.mock import MagicMock, patch

import ollama
import pytest

from history import MAX_RECENT, add_recent, load_recent
from llm_client import LLMError, ask_llm
from news_fetcher import NewsFetchError, _about_pattern, get_headlines, is_valid_ticker, ticker_exists
from prompt_templates import build_prompt
from response_parser import parse_sentiment


# --- is_valid_ticker ---
@pytest.mark.parametrize("t", ["AAPL", "aapl", "AAPL ", "BRK-B", "BTC-USD", "^IXIC"])
def test_valid_tickers(t):
    assert is_valid_ticker(t)


@pytest.mark.parametrize("t", ["", "   ", "123", "AA PL", "TOOLONGTICKER", "AAPL;DROP", "^", "AA^PL"])
def test_invalid_tickers(t):
    assert not is_valid_ticker(t)


# --- get_headlines (yfinance mocked) ---
def _item(title):
    return {"content": {"title": title}}


def test_get_headlines_extracts_and_limits():
    with patch("news_fetcher.yf.Ticker") as T:
        T.return_value.news = [_item("A"), _item("B"), _item("C")]
        assert get_headlines("AAPL", 2) == ["A", "B"]


@pytest.mark.parametrize("news", [None, [], [{}, {"content": None}, {"content": {}}]])
def test_get_headlines_empty_or_malformed(news):
    with patch("news_fetcher.yf.Ticker") as T, patch("news_fetcher.yf.Search") as S:
        T.return_value.news = news
        S.return_value.news = []
        assert get_headlines("ZZZZQ") == []


def test_get_headlines_falls_back_to_search_for_this_ticker():
    with patch("news_fetcher.yf.Ticker") as T, patch("news_fetcher.yf.Search") as S:
        T.return_value.news = []
        S.return_value.news = [
            {"title": "A", "relatedTickers": ["AAPL", "MSFT"]},
            {"title": "Other", "relatedTickers": ["QCOM"]},
            {"title": "No tags"},
            {"title": "B", "relatedTickers": ["AAPL"]},
        ]
        assert get_headlines("aapl", 5) == ["A", "B"]


@pytest.mark.parametrize("exists, expected", [(True, ["A", "B"]), (False, [])])
def test_get_headlines_untagged_search_only_for_real_ticker(exists, expected):
    with patch("news_fetcher.yf.Ticker") as T, patch("news_fetcher.yf.Search") as S,             patch("news_fetcher.ticker_exists", return_value=exists):
        T.return_value.news = []
        S.return_value.news = [{"title": "A", "relatedTickers": ["BBDO"]}, {"title": "B"}]
        assert get_headlines("BBD", 5) == expected


def test_get_headlines_keeps_only_those_naming_the_company():
    with patch("news_fetcher.yf.Ticker") as T, patch("news_fetcher.yf.Search") as S:
        T.return_value.news = []
        S.return_value.quotes = [{"symbol": "GM", "longname": "General Motors Company"}]
        S.return_value.news = [
            {"title": "Stock Market Today: Dow Slips", "relatedTickers": ["GM"]},
            {"title": "GM Plans 500 New Jobs", "relatedTickers": ["GM"]},
            {"title": "General Electric Wins Order", "relatedTickers": ["GM"]},
            {"title": "Why General Motors Gained Today", "relatedTickers": ["GM"]},
            {"title": "GMC Trucks Recalled", "relatedTickers": ["GM"]},
        ]
        assert get_headlines("GM", 5) == ["GM Plans 500 New Jobs", "Why General Motors Gained Today"]


@pytest.mark.parametrize("symbol, name, headline, expected", [
    ("DIS", "The Walt Disney Company", "Disney CEO Makes Another Move", True),
    ("XOM", "ExxonMobil Holdings Corporation", "Diesel Prices Surge and ExxonMobil Could Benefit", True),
    ("LLY", "Eli Lilly and Company", "Fast delivery helps retailers", False),
    ("BTC-USD", "Bitcoin USD", "BTC Price Stalls", True),
    ("BAC", "Bank of America Corporation", "Bank Stocks Slide as Rates Rise", False),
    ("F", "Ford Motor Company", "F-150 Sales Lift Ford", True),
    ("F", "", "Anything at all", None),
])
def test_about_pattern(symbol, name, headline, expected):
    pattern = _about_pattern(symbol, name)
    assert (pattern and bool(pattern.search(headline))) == expected


def test_get_headlines_network_error():
    with patch("news_fetcher.yf.Ticker", side_effect=RuntimeError("boom")):
        with pytest.raises(NewsFetchError):
            get_headlines("AAPL")


# --- ticker_exists (yfinance mocked) ---
@pytest.mark.parametrize("empty, expected", [(False, True), (True, False)])
def test_ticker_exists_uses_price_history(empty, expected):
    with patch("news_fetcher.yf.Ticker") as T:
        T.return_value.history.return_value.empty = empty
        assert ticker_exists("AAPL") is expected


def test_ticker_exists_assumes_true_on_error():
    with patch("news_fetcher.yf.Ticker", side_effect=RuntimeError("boom")):
        assert ticker_exists("AAPL") is True


# --- prompt ---
def test_build_prompt_contains_ticker_and_cleaned_headlines():
    p = build_prompt("aapl", ["Apple  beats\nestimates", "Apple sued"])
    assert "AAPL" in p
    assert "- Apple beats estimates" in p
    assert "Do not give investment advice" in p


# --- parse_sentiment ---
def test_parse_well_formed():
    r = parse_sentiment("Sentiment: Positive\nReasoning: Strong earnings.")
    assert r["label"] == "Positive" and r["reasoning"] == "Strong earnings."


def test_parse_case_and_markdown():
    assert parse_sentiment("**Sentiment:** negative\nReasoning: Lawsuits.")["label"] == "Negative"


def test_parse_neutral_with_preamble():
    assert parse_sentiment("Sure!\nSentiment: Neutral\nReasoning: Mixed.")["label"] == "Neutral"


@pytest.mark.parametrize("raw", ["", None, "I think it's fine.", "Sentiment: Bullish"])
def test_parse_fallback_unclear(raw):
    assert parse_sentiment(raw)["label"] == "Unclear"


# --- llm_client error handling (Ollama down) ---
def test_ollama_down_gives_friendly_error():
    with patch("llm_client.ollama.Client") as C:
        C.return_value.chat.side_effect = ConnectionError("refused")
        with pytest.raises(LLMError, match="Ollama"):
            ask_llm("hi")


def test_model_not_pulled_gives_pull_hint():
    with patch("llm_client.ollama.Client") as C:
        C.return_value.chat.side_effect = ollama.ResponseError("model not found", 404)
        with pytest.raises(LLMError, match="ollama pull"):
            ask_llm("hi")


def test_ask_llm_returns_content():
    with patch("llm_client.ollama.Client") as C:
        C.return_value.chat.return_value = {"message": {"content": "ok"}}
        assert ask_llm("hi") == "ok"


# --- recent searches (temp file) ---
def test_recent_newest_first_and_one_entry_per_ticker(tmp_path):
    f = tmp_path / "recent.json"
    add_recent("aapl", "Positive", f)
    add_recent("TSLA", "Negative", f)
    add_recent("AAPL ", "Neutral", f)
    assert [(r["ticker"], r["label"]) for r in load_recent(f)] == [("AAPL", "Neutral"), ("TSLA", "Negative")]


def test_recent_is_capped(tmp_path):
    f = tmp_path / "recent.json"
    for i in range(MAX_RECENT + 3):
        add_recent("T" + chr(65 + i), "Neutral", f)
    assert len(load_recent(f)) == MAX_RECENT


@pytest.mark.parametrize("content", [None, "not json", '{"a": 1}', '[1, {"label": "x"}]'])
def test_recent_missing_or_corrupt_file_is_empty(tmp_path, content):
    f = tmp_path / "recent.json"
    if content is not None:
        f.write_text(content, encoding="utf-8")
    assert load_recent(f) == []
