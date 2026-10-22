# LLM Output Quality Evaluation

This is a simple comparison of human and model judgements (Implementation Plan, Section 13). The model's answers below come from a live run. **Fill in the "My judgement" column yourself**: read each ticker's headlines and decide the tone *before* looking at the model's label.

**Date:** 2026-09-30  **Model:** `llama3.2:3b`  **Headlines per ticker:** 5  **Temperature:** 0.2

## Results

| # | Ticker | Model's label | My judgement | Match? | Time |
|---|--------|---------------|--------------|--------|------|
| 1 | AAPL | Neutral | | ☐ | 9.2 s* |
| 2 | TSLA | Neutral | | ☐ | 5.5 s |
| 3 | MSFT | Positive | | ☐ | 5.1 s |
| 4 | NVDA | Neutral | | ☐ | 5.6 s |
| 5 | AMZN | Positive | | ☐ | 6.1 s |
| 6 | JPM | Neutral | | ☐ | 6.0 s |
| 7 | XOM | Positive | | ☐ | 4.5 s |
| 8 | INTC | Neutral | | ☐ | 4.5 s |
| 9 | BA | Positive | | ☐ | 3.9 s |
| 10 | DIS | Neutral | | ☐ | 4.5 s |

\* The first call includes loading the model into memory.

**Format followed:** 10 / 10 (0 "Unclear")  **Average time:** ~5.5 s  **Agreement with me:** ___ / 10

## Headlines the model saw

<details><summary>Show all 50 headlines</summary>

**AAPL:** Apple's new CEO John Ternus plans on making some changes · OpenAI is releasing newer models faster. Is that a good thing? · Apple Predicted To Sell 6 Million iPhone Duo Handsets This Year · S&P 500 dips, Nasdaq higher after data shows moderate inflation rise · What Is The Case For Waiting On Qualcomm Stock?

**TSLA:** Trump gathers with AI leaders, floats 'self-regulation' as the way to deal with the technology's dangers · Jensen Huang: AI data center push will create 1 million US jobs · S&P 500 dips, Nasdaq higher after data shows moderate inflation rise · SpaceX Just Got a Little Closer to a Tesla Merger · Consumer Confidence Fell to Its Lowest Level Since 2014 and Consumer Stocks Are Already Paying for It

**MSFT:** AI in America has a huge 1.7 million job shortage problem · Dow Jones Futures: Micron Rises On Hot Earnings After Treasury Yields Pressure Stocks · Microsoft (MSFT) Could Be 21% Above Fair Value After ClickHouse Expansion · Was There Any Sign Palantir Stock Would Run? · How This Beaten-Down Quantum Stock Could Rise 150%

**NVDA:** Breaking down Jensen Huang's biggest moves of Q3 2026 · Trump gathers with AI leaders, floats 'self-regulation' as the way to deal with the technology's dangers · Stock Market Today: Dow Knocked Down, Nasdaq Pares Gain; Micron Holds Firm After Earnings Soar · What Changed In Marvell's Story? · Nvidia, AMD Collaborator Teases Breakout To Record High. These Clues Bode Well.

**AMZN:** Elon Musk takes aim at Delta for refusing to use Starlink for Wi-Fi · OpenAI's Dots connect to 4,000 apps and never sleep · Constellation Energy stock climbs on Amazon nuclear power deal · S&P 500 dips, Nasdaq higher after data shows moderate inflation rise · Amazon Tries to Boost Nuclear Power in Maryland After Scrapping Data Center Deal

**JPM:** JPM vs. BAC: The Bank Built to Sustain Dividend Growth When Markets Turn · JPMorgan Stocks Edge Lower as Bank Joins Open Agent-Safety Project · JPMorgan Trades Below 50-Day SMA: Buy, Sell or Hold the Stock? · Jefferies' Q3 IB, Equities Offset Weak Asset Management & Fixed Income · JPMorgan revamps Micron stock price target before earnings

**XOM:** Diesel Prices Are Surging and ExxonMobil Stock Could Benefit · America's Strategic Oil Reserves Are at 44-Year Lows — And Trump Just Gave Away Another 40 Million Barrels · Why Is SLB (SLB) Expanding Its LNG Footprint With A Mozambique Subsea Win? · Sector Update: Energy Stocks Advance Pre-Bell Wednesday · Chevron & ExxonMobil Ink Potential Crude Supply Deals With Vietnam

**INTC:** Stock Market Today: Dow Knocked Down, Nasdaq Pares Gain; Micron Holds Firm After Earnings Soar · What Changed In Marvell's Story? · S&P 500 dips, Nasdaq higher after data shows moderate inflation rise · Is Cerebras' Next Big Thing Already Here? · What Is The Case For Waiting On Qualcomm Stock?

**BA:** Moderna, Cerebras, Jabil, HPE, Cal-Maine, Mattel, and More Stocks That Explain Today's Market · Boeing Just Won a Major Navy Fighter Jet Contract, but Don't Lose Sight of the 737 MAX · Boeing Wins Another Next-Generation Fighter Contract Worth $20 Billion · Pilot-on-Pilot Stabbing Forces Emergency Landing of Israel-Bound Plane · Morgan Stanley Calls Boeing's Fighter Win a 'Major Strategic' Victory

**DIS:** Netflix's Content Commitments Rise: Is Cash Flow Under Pressure? · Disney CEO Makes Another Major Move to Cut Jobs · 4 Media Stocks That Are Worth Watching in a Challenging Industry · Is It Worth Investing in Disney (DIS) Based on Wall Street's Bullish Views? · Disney Stock Holds Steady After Laying Off 300 Tech and HR Employees

</details>

## Observations from reviewing the outputs

These notes come from reading the model's reasoning alongside the headlines. Check them against your own reading.

1. **Irrelevant headlines are the biggest problem, and they come from the data, not the model.** yfinance often returns general market or sector news. For **INTC**, none of the 5 headlines mention Intel. For **TSLA**, only 1 of 5 is about Tesla. "S&P 500 dips, Nasdaq higher…" shows up for 4 different tickers. The model handled INTC well: it pointed out that no headline mentions Intel and answered Neutral.
2. **It misread finance jargon.** For **MSFT**, the model took "Could Be 21% Above Fair Value" as positive, but trading *above* fair value means the stock looks overvalued, which is arguably negative. It also counted "Beaten-Down Quantum Stock Could Rise 150%" as Microsoft news when it isn't.
3. **It hallucinated a connection.** For **AMZN**, the reasoning credits Amazon with "success in connecting with a large number of apps through OpenAI's Dots", but that headline is about OpenAI, not Amazon.
4. **It picked out company-specific news well.** For **BA**, it focused on the fighter-jet contracts and correctly ignored the unrelated airline incident. For **XOM**, it found the two ExxonMobil-specific headlines.
5. **"Neutral" often means "mixed or unrelated".** 6 of the 10 answers were Neutral, usually because the headlines were a mix of topics rather than because the news itself was neutral.
6. **It always followed the format.** With the strict prompt and temperature 0.2, all 10 replies used the `Sentiment:` / `Reasoning:` format, so the parser's "Unclear" fallback was never needed.
7. **It stayed within the limits.** None of the replies predicted a price or gave buy/sell advice.

## Ideas for improvement (for the presentation)

- Keep only headlines that mention the ticker or company name before prompting, which would fix most of problem 1.
- Include the company name (not just the ticker) in the prompt so the model can judge relevance.
- Try `mistral:7b` to see whether a larger model reads jargon better, as in the MSFT case.
