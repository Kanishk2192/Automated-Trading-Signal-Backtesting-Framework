# Automated Trading Signal & Backtesting Framework

A Python-based framework for automated trading signal generation, T+1 strategy backtesting, portfolio performance evaluation, and CSV export using an RSI-VWAP trading strategy. 

This project demonstrates the use of an RSI-VWAP trading strategy on 21 metal and metal-related stocks listed on the National Stock Exchange (NSE). The main purpose isn't to identify the most profitable strategy, but rather to automate the repetitive process of technical strategy backtesting and performance evaluation.

---

## Project Overview

Evaluating technical trading strategies manually often involves:

- Inspecting historical price charts
- Recording trades in spreadsheets
- Calculating returns and performance metrics manually
- Repeating the same process for multiple stocks

While manageable for a few trades, this process quickly becomes time-consuming, error-prone, difficult to reproduce, and inefficient while dealing with a large number of stocks.

This project automates the complete workflow, from retrieving market data and signal generation to backtesting, portfolio evaluation, and generating csv exports of trade history and signals.

The objective of this project isn't demonstrating a market-beating trading strategy, but rather **workflow automation**.

---

## Dynamic Market Data & Backtesting

The framework automatically retrieves the latest available market data from Yahoo Finance every time it is executed.

- During market hours, trading signals are generated using the latest available price from the ongoing trading session.
- After market close, signals are generated using the official daily closing prices.
- The backtest automatically uses a rolling one-year analysis window ending on the latest available trading day.
- No manual modification of analysis dates is required.

## Motivation

During my internship, I noticed that backtesting a trading strategy frequently involved manually reviewing historical charts, identifying entry and exit points, and recording trades in spreadsheets for every stock.

So instead of spending hours repeating the same process for every stock, I wanted to automate the entire workflow into a reusable Python framework capable of:

- Retrieving the latest available market data
- Generating trading signals automatically
- Executing realistic T+1 backtests
- Evaluating portfolio performance
- Exporting trading signals and trade history

---

## Key Features

- Automatically retrieves the latest available trading session data from Yahoo Finance
- Technical indicator calculation (RSI and VWAP)
- Rule-based BUY and SELL signal generation
- Realistic **T+1** trade execution
- Portfolio-level backtesting
- Daily mark-to-market portfolio valuation
- Automatic CSV export of trading signals
- Automatic CSV export of trade history
- Portfolio performance visualization
- Portfolio and trade-level performance metrics

---

## Strategy Logic

The current implementation demonstrates the framework using a simple **RSI + VWAP** strategy.

### Why this strategy?

The objective of this strategy is **not** to identify the most profitable trading setup, but to show how a rule-based strategy can be automated and backtested.

It combines two technical indicators:

- **Relative Strength Index (RSI):** Measures momentum and identifies potentially overbought and oversold conditions.
- **Volume Weighted Average Price (VWAP):** Acts as a trend confirmation filter by incorporating both price and trading volume.

The strategy generates signals only when **both indicators agree**, reducing the likelihood of acting on a single indicator in isolation.


### Buy Signal

- RSI < 30
- Closing Price > VWAP

### Sell Signal

- RSI > 70
- Closing Price < VWAP

## Backtesting Assumptions

This framework takes the following assumptions into consideration.

| Assumption | Implementation |
|------------|----------------|
| Initial Capital | ₹100,000 |
| Investment Universe | 21 NSE-listed metal and metal-related stocks. |
| Historical Data | Daily OHLCV data retrieved from Yahoo Finance. The framework automatically uses the latest available market data each time it is executed. |
| Backtest Window | Rolling one-year backtest ending on the latest available trading day. |
| Signal Generation | During market hours, signals are generated using the latest available price from the ongoing trading session. After market close, signals are generated using the official daily closing price. |
| Trade Execution | Signals generated on Day T are executed at the opening price of Day T+1. |
| Portfolio Construction | Equal-weight allocation across all securities. |
| Active Position | Multiple positions across different stocks may be held simultaneously |
| Position Type | Long-only. |
| Shares | Whole shares only (no fractional shares). |
| Portfolio Valuation | Daily mark-to-market using closing prices. |
| Open Positions | Any position remaining open at the end of the dataset is closed using the final available closing price to calculate complete portfolio performance. |

### Trade Execution

Trading signals are generated using the latest available market data retrieved from Yahoo Finance.

During market hours, signals are generated using the latest available price from the ongoing trading session. After market close, signals are generated using the official daily closing price.

Trades are executed at the opening price of the next available trading day **(T+1)**, reducing look-ahead bias and providing a more realistic simulation of trade execution.

---

## Workflow

```
Yahoo Finance
        │
        ▼
Latest available OHLCV Data
        │
        ▼
Technical Indicator Calculation
(RSI + VWAP)
        │
        ▼
Trading Signal Generation
        │
        ▼
T+1 Trade Execution
        │
        ▼
Portfolio Construction
        │
        ▼
Portfolio Performance Evaluation
        │
        ▼
CSV Exports & Visualization
```

---

## Performance Metrics

### Portfolio Metrics

- Initial Capital
- Final Portfolio Value
- Total Return
- Annual Return

### Trade Metrics

- Total Trades
- Win Rate
- Average Profit per Trade
- Average Loss per Trade
- Max. Drawdown
- Average Holding Period
- Profit Factor

---

## Output Files

The framework automatically generates the following outputs:

| File | Description |
|------|-------------|
| `signals.csv` | Current BUY / SELL / HOLD signals |
| `trade_history.csv` | Complete trade log with entry, exit, P&L, and holding period |
| `Portfolio_Value.png` | Portfolio equity curve |

These outputs can be used for additional analysis, visualization, or integration into other trading workflows.

---
---

## Sample Outputs

The following screenshots show sample outputs generated by the framework during a backtest.

### Portfolio Equity Curve

![Portfolio Equity Curve](images/portfolio_equity_curve.png)

The framework tracks the portfolio's daily value throughout the backtest and visualizes the resulting equity curve, allowing strategy performance to be evaluated over time.

---

### Portfolio Performance Metrics

![Portfolio Performance Metrics](images/portfolio_metrics.png)

At the end of each backtest, the framework automatically calculates key portfolio and trade-level performance metrics, including returns, win rate, drawdown, holding period, and profit factor.

---

### Trading Signals

![Trading Signals](images/trading_signals.png)

For every stock in the portfolio, the framework computes the technical indicators and generates BUY, SELL, or HOLD signals based on the predefined strategy rules.

---

### Actionable Trading Signals

![Buy & Sell Recommendations](images/buy_sell_recommendation.png)

To make the output easier to interpret, actionable BUY and SELL recommendations are also presented separately, allowing users to quickly identify potential trading opportunities.

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical computations |
| Matplotlib | Portfolio visualization |
| yfinance | Historical market data retrieval |
| datetime | Historical date range management |

---

## Current Limitations

In order to demonstrate an automated backtesting workflow, certain real-world market considerations have been intentionally simplified. 

| Limitation | Description |
|------------|-------------|
| RSI Calculation | Uses a 14-period Simple Moving Average (SMA) instead of Wilder's smoothing method |
| VWAP Calculation | Uses a daily approximation based on OHLCV data rather than true intraday VWAP |
| Transaction Costs | Brokerage fees and other transaction costs are not considered |
| Slippage | Trade execution assumes no slippage between expected and actual execution prices |
| Taxes | Taxes and other statutory charges are not included |
| Portfolio Rebalancing | No periodic portfolio rebalancing is performed |
| Position Type | Only long positions are supported |
| Intraday Trading | The framework currently operates on daily market data only |

---

## Repository Structure

```
Automated-Trading-Signal-Backtesting-Framework/
│
├── trading_framework.py
├── README.md
├── requirements.txt
├── LICENSE
│
├── outputs/
│   ├── signals.csv
│   ├── trade_history.csv
│   └── Portfolio_Value.png
│
└── images/
    ├── portfolio_performance.png
    ├── trading_signals.png
    └── terminal_output.png
```

---

## Future Enhancements 

Potential extensions include:

- Wilder's RSI implementation
- Intraday VWAP using minute-level market data
- Additional technical indicators (MACD, ADX, Bollinger Bands, Supertrend)
- Position sizing and risk management
- Portfolio rebalancing
- Transaction cost and slippage modelling
- Benchmark comparison against market indices
- Benchmark comparison against a Buy-and-Hold strategy
---

## Disclaimer

This project has been developed for educational and research purposes only.

The trading strategy included in this repository is intended solely to demonstrate the capabilities of the automated backtesting framework and should not be interpreted as financial advice or a recommendation to buy or sell any security.

---

## Feedback

Constructive feedback and suggestions are always welcome.

