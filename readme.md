# AI Trading Council

AI Trading Council is a Python-based multi-agent stock research and portfolio decision system built as a learning project for experimenting with AI agents, tool use, structured outputs, and multi-agent collaboration.

Three independent investment agents research the market using different investment philosophies. Their recommendations are reviewed by an investment council, returned to the analysts for reconsideration, and then evaluated by a final council that creates a weighted portfolio.

The project currently performs research and portfolio construction only. Automated paper trading is planned for a later phase.

---

## Current Architecture

```text
                   ┌─────────────────────┐
                   │   Research Prompt   │
                   └──────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │   Ava    │    │  Betsy   │    │  Camila  │
        │Aggressive│    │ Balanced │    │Conservat.│
        └────┬─────┘    └────┬─────┘    └────┬─────┘
             │               │               │
             └───────────────┼───────────────┘
                             │
                 Each analyst can use:
                             │
             ┌───────────────┴───────────────┐
             │                               │
             ▼                               ▼
      ┌──────────────┐              ┌────────────────┐
      │  Web Search  │              │ get_stock_data │
      │ News/Events  │              │ Alpha Vantage  │
      └──────────────┘              └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ 24-Hour Cache  │
                                    │ + Rate Limiter │
                                    └────────────────┘

                             │
                             ▼
                   ┌──────────────────┐
                   │ Initial Council  │
                   │     Review       │
                   └────────┬─────────┘
                            │
              Criticism returned to each analyst
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │   Ava    │  │  Betsy   │  │  Camila  │
        │ Revision │  │ Revision │  │ Revision │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                  ┌─────────────────┐
                  │  Final Council  │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │ Final Portfolio │
                  │ Stocks + Weights│
                  └─────────────────┘
```

---

## Investment Agents

### Ava — Aggressive

Ava focuses on higher-risk opportunities with significant upside potential.

Her research can include:

* High-growth companies
* Emerging technologies
* Momentum opportunities
* Event-driven opportunities
* Speculative investments
* Higher-volatility stocks

Ava accepts substantially more risk than the other analysts but must still provide a defensible investment thesis and identify major risks.

### Betsy — Balanced

Betsy attempts to balance growth potential with investment quality and risk.

Her research emphasizes:

* Quality growth
* Profitability
* Reasonable valuation
* Competitive advantages
* Financial strength
* Diversification
* Risk-adjusted return potential

### Camila — Conservative

Camila prioritizes capital preservation and dependable long-term returns.

Her research emphasizes:

* Financial strength
* Consistent profitability
* Durable business models
* Predictable demand
* Reasonable valuations
* Lower volatility
* Downside protection

---

## Research Tools

Each research agent currently has access to two primary sources of information.

### Web Search

Web search allows the agents to investigate current information including:

* Company news
* Earnings developments
* Market events
* Catalysts
* Sentiment
* Recent market developments
* Information that may contradict an investment thesis

This prevents the analysts from relying exclusively on information already contained in the language model.

### Alpha Vantage Fundamentals

The `get_stock_data` function tool provides company fundamental data through Alpha Vantage.

Available information can include:

* Market capitalization
* P/E and forward P/E
* Revenue
* Revenue growth
* Earnings growth
* Profit margins
* Operating margins
* Return on equity
* Return on assets
* Beta
* Moving averages
* Analyst estimates
* Other company fundamentals

The underlying Python function is:

```python
fetch_stock_data(ticker)
```

The agent-facing tool is:

```python
get_stock_data(ticker)
```

Separating the two allows the underlying market-data code to be tested independently of the AI agents.

---

## Market Data Cache

Alpha Vantage data is cached locally in:

```text
stock_data_cache.json
```

Cached data remains valid for 24 hours.

The basic process is:

```text
Agent requests ticker
        │
        ▼
Check local cache
        │
     ┌──┴──┐
     │     │
   Found  Missing
     │     │
     ▼     ▼
 Return   Alpha Vantage
 cached        │
 data          ▼
          Validate response
                │
                ▼
           Save to cache
                │
                ▼
           Return data
```

The cache reduces unnecessary external API requests when multiple analysts investigate the same company.

The cache file is intentionally excluded from Git.

---

## Concurrent API Protection

The research agents run concurrently using `asyncio.gather()`.

Because multiple agents may request fundamental data at approximately the same time, `market_data.py` uses a shared `threading.Lock`.

This prevents multiple uncached Alpha Vantage requests from executing simultaneously.

The market-data layer also:

* Enforces spacing between Alpha Vantage requests
* Prevents duplicate simultaneous requests
* Protects cache read/write operations
* Rechecks the cache when necessary
* Rejects Alpha Vantage rate-limit responses
* Rejects invalid ticker responses

Ticker aliases can also be normalized before lookup. For example:

```text
BRK.B → BRK-B
```

This prevents different ticker formats from creating unnecessary duplicate requests.

---

## Council Process

After the three analysts complete their independent research, their proposals are passed to the initial council.

The council evaluates:

* Areas of agreement
* Areas of disagreement
* Strength of investment theses
* Potentially overlooked risks
* Portfolio concentration
* Diversification
* Valuation
* Correlated risks

The council then provides separate feedback to Ava, Betsy, and Camila.

Each analyst independently reviews that criticism and decides whether to modify their original five selections.

Analysts are not required to agree with the council.

---

## Final Council

The three revised portfolios are submitted to the final council.

The final council selects between five and ten stocks and assigns each position a portfolio weight.

The council considers:

* Investment quality
* Growth
* Valuation
* Risk
* Diversification
* Overlapping exposures
* Analyst arguments
* Whether each position adds something meaningful to the portfolio

Portfolio weights must sum to exactly:

```text
1.0 (100%)
```

This requirement is also enforced programmatically using Pydantic validation.

---

## Structured Outputs

Pydantic models are used throughout the workflow so agents return predictable structured data instead of arbitrary text.

Current models include:

```text
StockIdea
ResearchProposal
ResearchSession
CouncilDiscussion
FinalPortfolio
PortfolioPosition
FinalCouncilDecision
```

This allows the output of one agent or stage to be reliably passed into the next stage.

---

## Project Structure

```text
ai-trading-council/
│
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
│
└── src/
    └── trading_council/
        │
        ├── __init__.py
        ├── main.py
        │
        ├── agents/
        │   ├── __init__.py
        │   ├── ava.py
        │   ├── betsy.py
        │   ├── camila.py
        │   ├── council.py
        │   └── models.py
        │
        └── tools/
            └── market_data.py
```

---

## Running the Project

Create and activate a Python virtual environment and install the project dependencies.

Environment variables are stored locally in `.env`.

Required variables currently include:

```text
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

Do not commit `.env` to Git.

Run the complete council with:

```powershell
python -m trading_council.main
```

The program will:

1. Run Ava, Betsy, and Camila concurrently.
2. Allow each analyst to conduct current research.
3. Retrieve fundamental data when needed.
4. Produce five recommendations per analyst.
5. Submit all recommendations to the council.
6. Return council criticism to each analyst.
7. Allow each analyst to revise their portfolio.
8. Submit the revised portfolios to the final council.
9. Produce a final weighted portfolio.

---

## Current Status

The project currently supports:

* Multi-agent stock research
* Distinct investment personalities
* Concurrent analyst execution
* Current web research
* Fundamental stock-data tools
* Alpha Vantage integration
* 24-hour market-data caching
* API rate limiting
* Concurrent cache/API protection
* Ticker normalization
* Structured Pydantic outputs
* Council criticism
* Independent analyst revisions
* Final portfolio selection
* Portfolio weighting and validation

---

## Planned Development

Potential next phases include:

* Persisting research and council decisions
* Portfolio/account state
* Available-cash tracking
* Existing-position awareness
* Position sizing and risk rules
* Portfolio rebalancing logic
* Historical decision tracking
* Performance tracking
* Additional market-data tools
* Paper-trading integration
* Order generation and execution
* Trade monitoring
* Automated recurring research cycles

The long-term goal is for the council to move from producing a theoretical 100% portfolio to managing an existing paper portfolio while considering current holdings, available cash, previous decisions, and portfolio risk.

---

## Disclaimer

This project is intended for educational and experimental purposes.

The AI-generated research, recommendations, portfolio weights, and future trading functionality should not be considered financial advice. AI models and external data sources can produce incomplete, inaccurate, or outdated information.