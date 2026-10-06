from unittest.mock import MagicMock, patch

import pytest

from llm_client import LLMError, ask_llm
from news_fetcher import NewsFetchError, get_headlines, is_valid_ticker
from prompt_templates import build_prompt
from response_parser import parse_sentiment


# --- is_valid_ticker ---
@pytest.mark.parametrize("t", ["AAPL", "aapl", "AAPL ", "BRK-B"])
def test_valid_tickers(t):
    assert is_valid_ticker(t)


@pytest.mark.parametrize("t", ["", "   ", "123", "AA PL", "TOOLONGTICKER", "AAPL;DROP"])
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
    with patch("news_fetcher.yf.Ticker") as T:
        T.return_value.news = news
        assert get_headlines("ZZZZQ") == []


def test_get_headlines_network_error():
    with patch("news_fetcher.yf.Ticker", side_effect=RuntimeError("boom")):
        with pytest.raises(NewsFetchError):
            get_headlines("AAPL")


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


def test_ask_llm_returns_content():
    with patch("llm_client.ollama.Client") as C:
        C.return_value.chat.return_value = {"message": {"content": "ok"}}
        assert ask_llm("hi") == "ok"
