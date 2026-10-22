"""Streamlit UI: AI Stock News & Sentiment Analyst."""
import streamlit as st

from history import add_recent, load_recent
from llm_client import DEFAULT_MODEL, LLMError, ask_llm
from news_fetcher import NewsFetchError, get_headlines, is_valid_ticker, ticker_exists
from prompt_templates import build_prompt
from response_parser import parse_sentiment

ICONS = {"Positive": "🟢", "Negative": "🔴", "Neutral": "🟡", "Unclear": "⚪"}


def analyze(ticker: str, max_items: int) -> None:
    if not is_valid_ticker(ticker):
        st.error("Please enter a valid ticker symbol, e.g. AAPL, BTC-USD or ^IXIC.")
        return

    try:
        with st.spinner("Fetching news..."):
            headlines = get_headlines(ticker, max_items)
    except NewsFetchError:
        st.error("Couldn't fetch news right now. Check your internet connection and try again.")
        return

    if not headlines:
        symbol = ticker.strip().upper()
        if ticker_exists(symbol):
            st.info(f"No recent news found for '{symbol}'. Try again later or pick another ticker.")
        elif not symbol.startswith("^") and ticker_exists(f"^{symbol}"):
            st.error(f"Ticker '{symbol}' not found. Indexes start with '^' on Yahoo Finance: try '^{symbol}'.")
        else:
            st.error(f"Ticker '{symbol}' not found. Check the symbol and try again.")
        return

    try:
        with st.spinner("Asking the local model..."):
            raw = ask_llm(build_prompt(ticker, headlines))
    except LLMError as e:
        st.error(str(e))
        return

    result = parse_sentiment(raw)
    add_recent(ticker, result["label"])
    st.subheader(f"{ICONS[result['label']]} Sentiment: {result['label']}")
    if result["reasoning"]:
        st.write(result["reasoning"])
    if result["label"] == "Unclear":
        st.caption("The model didn't follow the expected format, so the raw reply is shown above.")

    with st.expander("Headlines analyzed"):
        for h in headlines:
            st.write(f"- {h}")


st.set_page_config(page_title="AI Stock News & Sentiment Analyst", page_icon="📰")
st.title("📰 AI Stock News & Sentiment Analyst")
st.caption(f"Reads recent headlines and gives a quick sentiment read using a local LLM ({DEFAULT_MODEL} via Ollama).")
st.warning("Not financial advice — for informational exploration only. This does not predict prices.")

ticker = st.text_input("Stock ticker", placeholder="e.g. AAPL")
max_items = st.slider("Headlines to analyze", min_value=3, max_value=10, value=5)

if st.button("Analyze", type="primary"):
    analyze(ticker, max_items)

recent = load_recent()
if recent:
    st.divider()
    st.subheader("Recent searches")
    for r in recent:
        label = r.get("label", "Unclear")
        st.write(f"{ICONS.get(label, '⚪')} **{r['ticker']}** — {label} · {r.get('time', '')}")
