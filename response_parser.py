"""Parse raw LLM text into a sentiment label + reasoning, with a fallback."""
import re

VALID_LABELS = {"positive": "Positive", "negative": "Negative", "neutral": "Neutral"}


def parse_sentiment(raw_text: str) -> dict:
    """Return {"label", "reasoning", "raw"}. Label is 'Unclear' if the format isn't followed."""
    raw_text = raw_text or ""
    label = "Unclear"
    reasoning = ""

    m = re.search(r"sentiment\s*:\s*\**\s*([A-Za-z]+)", raw_text, re.IGNORECASE)
    if m:
        label = VALID_LABELS.get(m.group(1).lower(), "Unclear")

    r = re.search(r"reasoning\s*:\s*(.+)", raw_text, re.IGNORECASE | re.DOTALL)
    if r:
        reasoning = r.group(1).strip()
    elif label == "Unclear":
        reasoning = raw_text.strip()

    return {"label": label, "reasoning": reasoning, "raw": raw_text}
