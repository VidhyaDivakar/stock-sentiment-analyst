# Prompt design

The LLM does one narrow task: judge the tone of a handful of headlines. The prompt in `prompt_templates.py` is written to keep it there.

## The prompt

```
You are a financial news sentiment assistant. Based ONLY on the headlines below about {ticker},
determine whether the overall news tone is Positive, Negative, or Neutral.
Do not predict future stock prices. Do not give investment advice.

Headlines:
{headline_list}

Respond in this exact format:
Sentiment: <Positive/Negative/Neutral>
Reasoning: <1-2 sentence explanation based only on the headlines above>
```

`{ticker}` is the upper-cased ticker. `{headline_list}` is one `- headline` line per headline.

## Why each part is there

| Part | Purpose |
| --- | --- |
| "Based ONLY on the headlines below" | Stops the model from using general knowledge about the company. |
| "Do not predict future stock prices. Do not give investment advice." | Keeps output within the app's purpose and avoids advice-like claims. |
| Three fixed labels | Limits the answer to values the app can display and parse. |
| "Respond in this exact format" | Gives a predictable structure that `parse_sentiment` can read. |
| "1-2 sentence explanation" | Keeps replies short and fast. |

## Settings that affect output

- **Temperature 0.2:** Set in `llm_client.py`. A low value makes replies more consistent across repeated runs. Output is still not guaranteed to be identical.
- **Headline count:** The UI lets the user pick 3 to 10. More headlines give the model more context but make requests slower.
- **Headline cleaning:** `clean_headline` collapses whitespace and newlines so each headline stays on one prompt line.

## Handling off-format replies

The model doesn't always follow the format. `parse_sentiment` is tolerant of common variations:

| Model reply | Parsed label |
| --- | --- |
| `Sentiment: Positive` | Positive |
| `**Sentiment:** negative` (Markdown, lower case) | Negative |
| A friendly line, then `Sentiment: Neutral` | Neutral |
| `Sentiment: Bullish` (not an allowed label) | Unclear |
| No `Sentiment:` line at all, or empty reply | Unclear |

When the label is `Unclear` and there is no `Reasoning:` line, the raw reply is shown so the user still sees what the model said.

## Evaluating output quality

There is no automated accuracy score, so quality is checked by hand:

1. Pick 5 to 10 tickers with different news situations.
2. Read the headlines yourself and decide whether you would call them Positive, Negative, or Neutral.
3. Run the app on the same ticker and compare the label and reasoning.
4. Record each mismatch and whether the model's reasoning was grounded in the headlines.

| Ticker | Your label | Model label | Match? | Notes |
| --- | --- | --- | --- | --- |
| | | | | |

Headlines change daily, so save the headlines alongside each row if you want to repeat a comparison later.

## Known limitations

- A 3B model can misread sarcasm, mixed headlines, or financial jargon.
- Sentiment reflects only the few headlines fetched, not the company's fundamentals.
- The app labels tone. It does not say whether a stock will rise or fall.
