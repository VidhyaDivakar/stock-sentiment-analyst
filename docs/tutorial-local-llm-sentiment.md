# Tutorial: Build a local LLM sentiment app with Ollama, yfinance, and Streamlit

In this tutorial, you'll build an app that fetches recent news headlines for a stock and uses a local LLM to label their tone as Positive, Negative, or Neutral. Everything runs on your machine, with no API keys or paid services.

This tutorial walks through the finished project in this repository. The full code is in the repo, so you can read each module as you go.

## What you'll learn

- How to call a local model through Ollama from Python
- How to write a prompt that asks for a predictable output format
- How to parse model output defensively when the model ignores the format
- How to handle failures at the point where they happen

## Before you begin

Complete steps 1 to 3 of the [setup guide](setup-guide.md): install Ollama, pull `llama3.2:3b`, and run `uv sync`.

## Step 1: Check that Python can reach the model

Create a scratch file and send one hardcoded prompt:

```python
import ollama

response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Say hello in 5 words"}],
)
print(response["message"]["content"])
```

Run it with `uv run python scratch.py`. You should see a short greeting.

If you get a connection error, Ollama isn't running. See [Troubleshooting](setup-guide.md#troubleshooting).

## Step 2: Fetch headlines

`news_fetcher.py` wraps `yfinance`. Two decisions matter here:

1. **Validate before fetching.** `is_valid_ticker` rejects empty or malformed input so you don't spend a network call on it.
2. **Treat missing data as normal.** `yfinance` may return `None`, an empty list, or items without a title. `get_headlines` skips anything it can't read and returns an empty list when nothing is usable.

```python
from news_fetcher import get_headlines

print(get_headlines("AAPL", 5))   # a list of headline strings
print(get_headlines("ZZZZQ", 5))  # [] with no crash
```

## Step 3: Build the prompt

`prompt_templates.py` combines the ticker and headlines into one prompt. The prompt does three things:

- Limits the model to the headlines ("Based ONLY on the headlines below")
- Rules out price predictions and advice
- Requests an exact two-line format: `Sentiment:` then `Reasoning:`

See [Prompt design](prompt-design.md) for the reasoning behind each line.

```python
from prompt_templates import build_prompt

print(build_prompt("aapl", ["Apple beats estimates", "Apple faces new lawsuit"]))
```

## Step 4: Call the model

`llm_client.py` sends the prompt to Ollama with a low temperature (0.2) so replies are more consistent. It turns low-level failures into one `LLMError` with a message the user can act on, such as "Could not reach Ollama" or "Model not found. Run: ollama pull ...".

```python
from llm_client import ask_llm
from prompt_templates import build_prompt

raw = ask_llm(build_prompt("AAPL", ["Apple beats estimates"]))
print(raw)
```

## Step 5: Parse the reply

A small model won't always follow the requested format, so don't assume it will. `parse_sentiment` extracts the label and reasoning, accepts Markdown and case variations, and falls back to `Unclear` when the reply doesn't match.

```python
from response_parser import parse_sentiment

print(parse_sentiment("Sentiment: Positive\nReasoning: Strong earnings."))
print(parse_sentiment("I think it's fine."))  # label is "Unclear"
```

## Step 6: Wire it into Streamlit

`app.py` runs the steps in order and stops with a clear message at the first failure: invalid ticker, news fetch error, no news, or model error. `st.spinner` shows progress during the two slow steps.

Start the app:

```
uv run streamlit run app.py
```

Enter `AAPL` and click **Analyze**. You should see a label, a short reason, and an expandable list of the headlines used.

## Step 7: Test it

Run the automated tests, which mock the network and the model:

```
uv run pytest
```

Then check the failure paths by hand: an empty ticker, `ZZZZQ`, and quitting Ollama before clicking **Analyze**. See [Testing](testing.md) for the full list.

## Next steps

- Compare the model's labels with your own reading of the headlines, using the method in [Prompt design](prompt-design.md#evaluating-output-quality).
- Try `mistral:7b` by changing `DEFAULT_MODEL` in `llm_client.py`, and note the trade-off between format reliability and speed.

> **Disclaimer:** This tool labels the tone of news headlines. It does not predict prices and is not financial advice.
