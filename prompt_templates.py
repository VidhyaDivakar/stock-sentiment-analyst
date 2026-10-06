"""Prompt templates for the sentiment task."""

PROMPT_TEMPLATE = """You are a financial news sentiment assistant. Based ONLY on the headlines below about {ticker}, \
determine whether the overall news tone is Positive, Negative, or Neutral. \
Do not predict future stock prices. Do not give investment advice.

Headlines:
{headline_list}

Respond in this exact format:
Sentiment: <Positive/Negative/Neutral>
Reasoning: <1-2 sentence explanation based only on the headlines above>"""


def clean_headline(text: str) -> str:
    """Collapse whitespace/newlines so a headline stays on one prompt line."""
    return " ".join(text.split())


def build_prompt(ticker: str, headlines: list[str]) -> str:
    headline_list = "\n".join(f"- {clean_headline(h)}" for h in headlines)
    return PROMPT_TEMPLATE.format(ticker=ticker.strip().upper(), headline_list=headline_list)
