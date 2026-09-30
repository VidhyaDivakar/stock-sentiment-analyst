# Presentation & Demo Script (5–10 min)

## Before you present (checklist)

- [ ] Ollama running; `ollama list` shows `llama3.2:3b`
- [ ] Warm up the model: run one analysis before presenting (the first call is slow while the model loads)
- [ ] App already open in the browser (`uv run streamlit run app.py`)
- [ ] Internet connected (yfinance needs it)
- [ ] README and workflow diagram open in another tab
- [ ] Backup: screenshot in `docs/screenshots/` in case the live demo fails

---

## 1. Problem & audience (~1 min)

> "Checking how a stock is being talked about means opening several articles and judging the tone yourself. It's slow and repetitive. This app is a quick gut check for retail investors and learners: type a ticker, and a local AI reads the latest headlines and tells you if the tone is positive, negative or neutral, and why."

> "It's **not** a price predictor and **not** financial advice. The app shows that disclaimer at the top."

## 2. Live demo (~2–3 min)

1. **Best case.** Type `AAPL` and click **Analyze**.
   - Point out the spinners: first fetching news, then asking the local model.
   - Read out the sentiment label and reasoning.
   - Open **Headlines analyzed**: "The model only sees these headlines, nothing else."
2. **Slider.** "You can choose 3–10 headlines. More headlines give more context but a slower answer."
3. **Edge case: bad ticker.** Type `ZZZZQ`: "ticker not found", no crash.
4. **Edge case: empty input.** Click Analyze with no input: validation message, and no model call is wasted.
5. *(Optional, if time allows)* Quit Ollama and run again to show the friendly "Could not reach Ollama" message.

## 3. Workflow walkthrough (~1–2 min)

Show the Mermaid diagram in the README:

> "Ticker in → validate → fetch news with yfinance → build a prompt → send to the local Ollama model → parse the reply → display. Every step that can fail has its own friendly message."

Mention the prompt design: the model must answer with `Sentiment:` / `Reasoning:`, is told to use only the headlines and never predict prices, and runs at a low temperature (0.2) for consistent answers. If it ignores the format, the parser falls back to "Unclear" instead of crashing.

## 4. Tools & why (~1 min)

| Tool | Why |
|------|-----|
| Ollama + `llama3.2:3b` | Free, open-source, runs locally on 16 GB RAM, no paid API, no training |
| yfinance | Free news data, no API key |
| Streamlit | Fastest way to build a usable UI in Python |
| uv | Simple, fast dependency management |
| pytest | Unit tests with yfinance and Ollama mocked, so they run offline |

## 5. Challenges & next steps (~1–2 min)

**Challenges** (fill in from your experience):
- Finding the right field for the headline in yfinance's news data (`content.title`)
- Getting a small 3B model to follow the output format reliably
- Telling "ticker doesn't exist" apart from "ticker has no news"
- Results from `docs/llm_evaluation.md`: agreement rate and where the model got it wrong

**What I'd improve next:**
- A confidence score next to the label
- Saving past queries in SQLite to track sentiment over time
- Comparing several tickers side by side
- Trying `mistral:7b` for better reasoning

## Closing line

> "In short: free, local and private. It turns a few minutes of reading headlines into a few seconds, and it's honest about its limits."
