# End-to-End Test Results

These are manual checks against the live system: real yfinance data and the real local Ollama model, with no mocks. They complement the automated unit tests in `tests/` (`uv run pytest`), which mock yfinance and Ollama.

**Date:** 2026-09-30  **Model:** `llama3.2:3b` (Q4_K_M, 3.2B)  **Headlines per ticker:** 5

> **How these were run:** The same sequence of pipeline calls that `app.py` makes (`is_valid_ticker` → `get_headlines` → `ticker_exists` → `build_prompt` → `ask_llm` → `parse_sentiment`) was run from a script against live services. Separately, the Streamlit server was started and its health check returned `ok`. **Still to do:** click through cases 1–4 in the browser once to confirm the on-screen messages, and tick the "UI" column.

| # | Scenario | Input | Expected result | Actual result (pipeline) | Pass? | UI checked? |
|---|----------|-------|-----------------|--------------------------|-------|-------------|
| 1 | Valid ticker with news | `AAPL` | Sentiment label + reasoning | `Neutral` + reasoning, 9.2 s (the first call includes loading the model) | ✅ | ☐ |
| 2 | Valid ticker, no recent news | `CKX` (CKX Lands, real NYSE American stock) | "No recent news found" | `no recent news` | ✅ | ☐ |
| 3 | Nonexistent ticker | `ZZZZQ` | "Ticker not found" | `ticker not found` | ✅ | ☐ |
| 4 | Empty / malformed input | `""`, `123` | Validation error, no network/LLM call | `validation error` for both | ✅ | ☐ |
| 5 | Ollama not running | `AAPL` with `OLLAMA_HOST=127.0.0.1:1` (unreachable) | Friendly "Could not reach Ollama" message | `Could not reach Ollama. Make sure the Ollama app is running.` | ✅ | ☐ |
| 6 | Model not pulled | `BRT`, before `llama3.2:3b` was pulled | Error with `ollama pull` hint | `Model 'llama3.2:3b' not found. Run: ollama pull llama3.2:3b` | ✅ | n/a |
| 7 | No internet *(optional)* | Disconnect Wi-Fi, enter `AAPL` | "Couldn't fetch news right now…" | Not run live (covered by unit test `test_get_headlines_network_error`) | ☐ | ☐ |

For case 5 in the UI, the easiest method is to quit Ollama from the system tray and click **Analyze**.

## Automated test run

`uv run pytest -q` on 2026-09-30:

```
.............................                                            [100%]
29 passed in 15.28s
```

## Notes / issues found

- yfinance writes messages like `HTTP Error 404 … Quote not found for symbol: ZZZZQ` to the terminal for unknown tickers. They only appear in the server console, never in the UI.
- yfinance news isn't always about the requested company. `BRT` returned a headline about *Brimstone Investment (JSE:BRT)*, a different company that shares the symbol, and one headline from October 2025. See [llm_evaluation.md](llm_evaluation.md).
