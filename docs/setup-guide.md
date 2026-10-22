# Setup and troubleshooting guide

This guide takes you from a clean machine to a running app. Each step ends with a check, so you know it worked before moving on.

## Prerequisites

| Requirement | Why | Check |
| --- | --- | --- |
| Python 3.13 or later | Version set in `pyproject.toml` | `python --version` |
| [uv](https://docs.astral.sh/uv/) | Installs dependencies and runs commands | `uv --version` |
| [Ollama](https://ollama.com/download) | Runs the LLM locally | `ollama --version` |
| About 16 GB RAM | Comfortable headroom for a 3B-parameter model | n/a |
| Internet connection | `yfinance` fetches news from the network | n/a |

## 1. Install and start Ollama

1. Download and install Ollama from [ollama.com/download](https://ollama.com/download).
2. Start the Ollama app. On Windows it runs in the system tray.

**Check:** Run `ollama list`. It prints a table (possibly empty) without an error.

## 2. Pull the model

```
ollama pull llama3.2:3b
```

**Check:** Run `ollama list`. `llama3.2:3b` appears in the list.

To confirm the model responds, run `ollama run llama3.2:3b`, type a short question, and exit with `/bye`.

## 3. Install dependencies

From the project folder:

```
uv sync
```

This creates `.venv/` and installs `streamlit`, `yfinance`, `ollama`, and the `pytest` dev dependency.

**Check:** `uv run pytest` passes. The tests mock yfinance and Ollama, so they don't need the network or a running model.

## 4. Run the app

```
uv run streamlit run app.py
```

Open the local URL that Streamlit prints (usually `http://localhost:8501`).

**Check:** Enter `AAPL`, leave the slider at 5, and click **Analyze**. You should see a sentiment label, a short reason, and a collapsible list of the headlines analyzed. The first request can take longer while the model loads into memory.

## Configuration

These values live in code, not in a config file.

| Setting | Where | Default |
| --- | --- | --- |
| Model name | `DEFAULT_MODEL` in `llm_client.py` | `llama3.2:3b` |
| Request timeout | `timeout` argument of `ask_llm` in `llm_client.py` | 120 seconds |
| Temperature | `options` in `ask_llm` | 0.2 |
| Headlines analyzed | Slider in `app.py` | 5 (range 3 to 10) |

## Troubleshooting

### "Could not reach Ollama. Make sure the Ollama app is running."

**Cause:** The app can't connect to the Ollama service.
**Fix:** Start the Ollama app, then click **Analyze** again. `ollama list` should work in a terminal before you retry.

### "Model 'llama3.2:3b' not found. Run: ollama pull llama3.2:3b"

**Cause:** Ollama is running, but the model hasn't been downloaded.
**Fix:** Run `ollama pull llama3.2:3b`. If you changed `DEFAULT_MODEL`, pull that model name instead.

### "Couldn't fetch news right now. Check your internet connection and try again."

**Cause:** `yfinance` could not reach its data source.
**Fix:** Check your connection and try again. Rate limiting or a temporary outage on the data source can also cause this. Wait a few minutes before retrying.

### "No news found for 'XYZ'"

**Cause:** The ticker doesn't exist, or the source returned no recent articles for it.
**Fix:** Check the symbol. Try a large, active ticker such as `AAPL` or `MSFT` to confirm the rest of the pipeline works.

### "Please enter a valid ticker symbol"

**Cause:** The input failed validation before any network call. Tickers must be letters only, with optional `.` or `-`, and at most 6 characters.
**Fix:** Enter a symbol such as `AAPL` or `BRK-B`.

### Sentiment shows "Unclear"

**Cause:** The model didn't follow the `Sentiment: ... / Reasoning: ...` format, so the parser used its fallback. The raw reply is shown as the reasoning.
**Fix:** Click **Analyze** again. A larger model (for example `mistral:7b`) follows the format more reliably, but is slower.

### The request is very slow or times out

**Cause:** A 3B model on CPU only can take several seconds per request, and loading the model the first time is slower. Requests longer than the 120-second timeout fail with an error.
**Fix:** Lower the **Headlines to analyze** slider, close memory-heavy apps, and avoid models larger than 7B on a 16 GB machine.

### `uv` or `python` is not recognized

**Cause:** The tool isn't installed or isn't on your `PATH`.
**Fix:** Install it, then open a new terminal window so the updated `PATH` takes effect.
