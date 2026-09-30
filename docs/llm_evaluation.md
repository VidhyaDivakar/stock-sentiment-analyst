# LLM Output Quality Evaluation

Simple human-vs-model comparison (Implementation Plan, Section 13). For each ticker: run the app, open **Headlines analyzed**, read the headlines yourself and decide the tone *before* looking at the model's answer. Then record both.

**Date:** ____________  **Model:** `llama3.2:3b`  **Headlines per ticker:** ___

| # | Ticker | My judgement | Model's label | Match? | Notes (why it differed, format issues, etc.) |
|---|--------|--------------|---------------|--------|----------------------------------------------|
| 1 | AAPL | | | ☐ | |
| 2 | TSLA | | | ☐ | |
| 3 | MSFT | | | ☐ | |
| 4 | NVDA | | | ☐ | |
| 5 | AMZN | | | ☐ | |
| 6 | | | | ☐ | |
| 7 | | | | ☐ | |
| 8 | | | | ☐ | |
| 9 | | | | ☐ | |
| 10 | | | | ☐ | |

**Agreement:** ___ / ___ (___ %)  **"Unclear" (format not followed):** ___

## Lessons learned (use in presentation)

- Where did the model and I disagree most? (e.g. mixed headlines, sarcasm, headlines that mention a stock only in passing)
- Did it ever ignore the output format?
- Did it drift into price predictions or advice despite the prompt?
- Would `mistral:7b` (fallback model) be worth the extra time?
