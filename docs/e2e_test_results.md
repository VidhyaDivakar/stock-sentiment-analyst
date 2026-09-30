# End-to-End Test Results

Manual checks run against the live app (`uv run streamlit run app.py`). These complement the automated unit tests in `tests/` (`uv run pytest`), which mock yfinance and Ollama.

**Tester:** ____________  **Date:** ____________  **Model:** `llama3.2:3b`

| # | Scenario | Steps | Expected result | Actual result | Pass? |
|---|----------|-------|-----------------|---------------|-------|
| 1 | Valid ticker with news | Enter `AAPL`, click **Analyze** | Sentiment label (Positive/Negative/Neutral) + reasoning; headlines listed in expander | | ☐ |
| 2 | Valid ticker, no recent news | Enter a thinly-covered ticker (try a small-cap you know exists), click **Analyze** | Blue info box: "No recent news found for '…'" — no crash | | ☐ |
| 3 | Nonexistent ticker | Enter `ZZZZQ`, click **Analyze** | Red error: "Ticker 'ZZZZQ' not found" | | ☐ |
| 4 | Empty / malformed input | Leave field empty (then try `123`), click **Analyze** | Red validation error; no spinner, no network/LLM call | | ☐ |
| 5 | Ollama not running | Quit Ollama (tray icon → Quit), enter `AAPL`, click **Analyze** | Red error: "Could not reach Ollama. Make sure the Ollama app is running." — no stack trace | | ☐ |
| 6 | Model not pulled *(optional)* | Temporarily set `DEFAULT_MODEL` to an unpulled model name | Red error with `ollama pull …` hint | | ☐ |
| 7 | No internet *(optional)* | Disconnect Wi-Fi, enter `AAPL` | Red error: "Couldn't fetch news right now…" | | ☐ |

## Automated test run

Paste the output of `uv run pytest -q` here:

```
(paste output)
```

## Notes / issues found

-
