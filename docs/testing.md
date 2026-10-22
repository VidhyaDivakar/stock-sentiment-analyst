# Testing

The automated tests are in `tests/test_components.py`. They mock `yfinance` and Ollama, so they run offline, quickly, and without a model installed.

## Run the tests

```
uv run pytest
```

## What the automated tests cover

| Area | Behavior checked |
| --- | --- |
| Ticker validation | Accepts `AAPL`, `aapl`, `AAPL ` (trailing space), and `BRK-B`. Rejects empty input, whitespace, digits, embedded spaces, over-long input, and `AAPL;DROP`. |
| Headline fetching | Extracts titles and respects the item limit. Returns an empty list for `None`, `[]`, and malformed items. Raises `NewsFetchError` on a network failure. |
| Prompt building | Upper-cases the ticker, cleans whitespace and newlines in headlines, and includes the "no investment advice" instruction. |
| Response parsing | Reads well-formed replies, Markdown and lower-case variants, and replies with a preamble. Falls back to `Unclear` for empty, `None`, off-format, or invalid-label replies. |
| LLM client | Returns the reply content on success. Raises `LLMError` mentioning Ollama when the connection is refused. |

## Manual end-to-end checks

The UI and the real model are checked by hand with `uv run streamlit run app.py`.

| # | Scenario | Steps | Expected result |
| --- | --- | --- | --- |
| 1 | Valid ticker with news | Enter `AAPL`, click **Analyze** | A sentiment label, a short reason, and a list of headlines |
| 2 | Ticker with no news | Enter a valid-looking symbol with no coverage | "No news found" message, no crash |
| 3 | Unknown ticker | Enter `ZZZZQ` | "No news found" message, no crash |
| 4 | Empty input | Leave the box empty, click **Analyze** | Validation message, no network or model call |
| 5 | Ollama not running | Quit Ollama, click **Analyze** | "Could not reach Ollama" message, no stack trace |
| 6 | Model not pulled | Set `DEFAULT_MODEL` to a model you haven't pulled | "Model ... not found. Run: ollama pull ..." |

## Output quality

Judging whether the model's sentiment is *right* can't be automated here. See [Evaluating output quality](prompt-design.md#evaluating-output-quality) for the manual comparison method.

## Not covered

- The Streamlit UI has no automated tests. Scenarios 1 to 6 above are manual.
- Tests use mocked data, so they don't detect changes in the real `yfinance` response format. If headlines stop appearing, check the response shape that `get_headlines` expects (`item["content"]["title"]`).
