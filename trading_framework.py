import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.ticker import FuncFormatter


# ── Symbol list ───────────────────────────────────────────────────────────────
def get_nifty_symbols():
    return [
        "TATASTEEL.NS", "JSWSTEEL.NS", "JINDALSTEL.NS", "SAIL.NS", "HINDALCO.NS",
        "VEDL.NS", "HINDZINC.NS", "NATIONALUM.NS", "HINDCOPPER.NS", "NSLNISP.NS",
        "MOIL.NS", "JSL.NS", "APLAPOLLO.NS", "WELCORP.NS", "LLOYDSME.NS",
        "RATNAMANI.NS", "MAHSEAMLES.NS", "HITECH.NS", "VENUSPIPES.NS", "SHYAMMETL.NS", "MIDHANI.NS",
    ]


# ── Data fetch ────────────────────────────────────────────────────────────────
def fetch_stock_data(symbol, start_date, end_date):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            print(f"  No data found for {symbol}")
            return None
        df.reset_index(inplace=True)
        df['Symbol'] = symbol
        return df[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None


# ── Indicators ────────────────────────────────────────────────────────────────
def calculate_rsi(df, window=14):
    if len(df) <= window:
        df['RSI'] = np.nan
        return df
    df['price_change'] = df['Close'].diff()
    df['gain'] = df['price_change'].clip(lower=0)
    df['loss'] = (-df['price_change']).clip(lower=0)
    avg_gain = df['gain'].rolling(window=window, min_periods=1).mean()
    avg_loss = df['loss'].rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
    df['RSI'] = 100 - (100 / (1 + rs))
    return df


def calculate_vwap(df):
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['Price_Volume']  = df['Typical_Price'] * df['Volume']
    df['Date_Only']     = pd.to_datetime(df['Date']).dt.date
    df['Cumulative_Price_Volume'] = df.groupby('Date_Only')['Price_Volume'].cumsum()
    df['Cumulative_Volume']       = df.groupby('Date_Only')['Volume'].cumsum()
    df['VWAP'] = (df['Cumulative_Price_Volume'] /
                  df['Cumulative_Volume'].replace(0, np.finfo(float).eps))
    return df


# ── Signal generation ─────────────────────────────────────────────────────────
def generate_signals(df):
    df['Signal'] = 0
    # Buy: oversold (RSI < 30) AND price above VWAP (bullish confirmation)
    df.loc[(df['RSI'] < 30) & (df['Close'] > df['VWAP']), 'Signal'] = 1
    # Sell: overbought (RSI > 70) AND price below VWAP (bearish confirmation)
    df.loc[(df['RSI'] > 70) & (df['Close'] < df['VWAP']), 'Signal'] = -1
    return df


# ── Back-test ─────────────────────────────────────────────────────────────────
def implement_portfolio_strategy():
    end_date   = datetime.now()
    start_date = end_date - timedelta(days=365)

    symbols           = get_nifty_symbols()
    initial_capital   = 1_000_000          # ₹10 Lakhs
    capital_per_stock = initial_capital / len(symbols)

    all_stock_data = {}
    all_trades     = []    # every completed round-trip trade across all stocks

    for symbol in symbols:
        print(f"Processing {symbol}...")

        df = fetch_stock_data(symbol, start_date, end_date)
        if df is None or len(df) < 15:
            print(f"  Skipping {symbol} – insufficient data")
            continue

        df = calculate_rsi(df)
        df = calculate_vwap(df)
        df = generate_signals(df)

        df['Position']    = 0
        df['Stock_Value'] = 0.0
        # Day 0: no trade has fired yet; the full allocation is held as cash
        df.loc[0, 'Stock_Value'] = capital_per_stock

        current_capital = capital_per_stock
        shares          = 0
        entry_price     = None
        entry_date      = None

        # ── T+1 execution ────────────────────────────────────────────────────
        # Signal confirmed at Day T close → trade executed at Day T+1 open
        for i in range(1, len(df)):
            prev_signal   = df.loc[i - 1, 'Signal']
            prev_position = df.loc[i - 1, 'Position']

            # BUY: signal fired yesterday, flat today → buy at today's open
            if prev_signal == 1 and prev_position == 0:
                entry_price = df.loc[i, 'Open']
                entry_date  = df.loc[i, 'Date']
                shares      = int(current_capital // entry_price)
                if shares > 0:
                    current_capital      -= shares * entry_price
                    df.loc[i, 'Position'] = 1
                else:
                    df.loc[i, 'Position'] = 0   # not enough capital

            # SELL: signal fired yesterday, long today → sell at today's open
            elif prev_signal == -1 and prev_position == 1:
                exit_price   = df.loc[i, 'Open']
                exit_date    = df.loc[i, 'Date']
                pnl          = (exit_price - entry_price) * shares
                holding_days = (pd.to_datetime(exit_date) -
                                pd.to_datetime(entry_date)).days

                all_trades.append({
                    'Symbol':       symbol,
                    'Entry_Date':   entry_date,
                    'Entry_Price':  round(entry_price, 2),
                    'Exit_Date':    exit_date,
                    'Exit_Price':   round(exit_price, 2),
                    'Shares':       shares,
                    'PnL':          round(pnl, 2),
                    'Holding_Days': holding_days,
                    'Status':       'Closed',
                })
                current_capital      += shares * exit_price
                shares                = 0
                entry_price           = None
                entry_date            = None
                df.loc[i, 'Position'] = 0

            else:
                # Hold existing position unchanged
                df.loc[i, 'Position'] = df.loc[i - 1, 'Position']

            # Mark-to-market value for this stock
            df.loc[i, 'Stock_Value'] = current_capital + (shares * df.loc[i, 'Close'])

        # ── Close any position still open at end of data ─────────────────────
        # The portfolio mark-to-market already prices it correctly, but the
        # trade record would be missing without this block.
        if shares > 0 and entry_price is not None:
            exit_price   = df.iloc[-1]['Close']
            exit_date    = df.iloc[-1]['Date']
            pnl          = (exit_price - entry_price) * shares
            holding_days = (pd.to_datetime(exit_date) -
                            pd.to_datetime(entry_date)).days
            all_trades.append({
                'Symbol':       symbol,
                'Entry_Date':   entry_date,
                'Entry_Price':  round(entry_price, 2),
                'Exit_Date':    exit_date,
                'Exit_Price':   round(exit_price, 2),
                'Shares':       shares,
                'PnL':          round(pnl, 2),
                'Holding_Days': holding_days,
                'Status':       'Open (closed at last price)',
            })

        all_stock_data[symbol] = df

    if not all_stock_data:
        print("No stock data processed – check data source / network.")
        return None, None

    # ── Aggregate portfolio value ─────────────────────────────────────────────
    all_dates = set()
    for df in all_stock_data.values():
        all_dates.update(pd.to_datetime(df['Date']).dt.date.tolist())
    all_dates = sorted(all_dates)

    portfolio_df = pd.DataFrame({
        'Date':            all_dates,
        'Portfolio_Value': float(initial_capital),
    })

    for symbol, df in all_stock_data.items():
        df['Date_Only']        = pd.to_datetime(df['Date']).dt.date
        stock_value_series     = pd.Series(df['Stock_Value'].values, index=df['Date_Only'])

        for date in df['Date_Only']:
            mask = portfolio_df['Date'] == date
            if mask.any():
                idx = portfolio_df[mask].index[0]
                portfolio_df.loc[idx, 'Portfolio_Value'] += (
                    stock_value_series.get(date, 0) - capital_per_stock
                )

    portfolio_df['Daily_Return']      = portfolio_df['Portfolio_Value'].pct_change().fillna(0)
    portfolio_df['Cumulative_Return'] = (1 + portfolio_df['Daily_Return']).cumprod() - 1

    if len(portfolio_df) <= 1:
        print("Not enough data to calculate performance metrics.")
        return portfolio_df, {}

    # ── Core return metrics ───────────────────────────────────────────────────
    final_value  = portfolio_df['Portfolio_Value'].iloc[-1]
    total_return = (final_value / initial_capital) - 1
    days = (portfolio_df['Date'].iloc[-1] - portfolio_df['Date'].iloc[0]).days
    annual_return = ((1 + total_return) ** (365 / days) - 1) if days > 0 else total_return

    # Max Drawdown
    rolling_max  = portfolio_df['Portfolio_Value'].cummax()
    drawdown_series = (portfolio_df['Portfolio_Value'] - rolling_max) / rolling_max
    max_drawdown = drawdown_series.min()

    # ── Trade-level metrics ───────────────────────────────────────────────────
    trades_df = pd.DataFrame(all_trades)

    if not trades_df.empty:
        trades_df.to_csv("trade_history.csv", index=False)
        print("\nTrade history exported → trade_history.csv")

    if not trades_df.empty:
        winning = trades_df[trades_df['PnL'] > 0]
        losing  = trades_df[trades_df['PnL'] < 0]

        total_trades  = len(trades_df)
        win_rate      = len(winning) / total_trades
        avg_profit    = winning['PnL'].mean()  if not winning.empty else 0.0
        avg_loss      = losing['PnL'].mean()   if not losing.empty  else 0.0
        avg_holding   = trades_df['Holding_Days'].mean()
        gross_profit  = winning['PnL'].sum()
        gross_loss    = abs(losing['PnL'].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
    else:
        total_trades  = 0
        win_rate      = 0.0
        avg_profit    = 0.0
        avg_loss      = 0.0
        avg_holding   = 0.0
        profit_factor = 0.0

    metrics = {
        'Initial Capital':       f"₹{initial_capital:,.2f}",
        'Final Portfolio Value': f"₹{final_value:,.2f}",
        'Total Return':          f"{total_return:.2%}",
        'Annual Return':         f"{annual_return:.2%}",
        'Total Trades':          total_trades,
        'Win Rate':              f"{win_rate:.2%}",
        'Avg Profit per Trade':  f"₹{avg_profit:,.2f}",
        'Avg Loss per Trade':    f"₹{avg_loss:,.2f}",
        'Max Drawdown':          f"{max_drawdown:.2%}",
        'Avg Holding Period':    f"{avg_holding:.1f} days",
        'Profit Factor':         f"{profit_factor:.2f}",
    }

    # ── Print metrics ─────────────────────────────────────────────────────────
    W = 44
    portfolio_keys = ['Initial Capital', 'Final Portfolio Value', 'Total Return', 'Annual Return']
    trade_keys     = ['Total Trades', 'Win Rate', 'Avg Profit per Trade', 'Avg Loss per Trade',
                      'Max Drawdown', 'Avg Holding Period', 'Profit Factor']

    print("\n" + "=" * W)
    print("       Portfolio Performance Metrics")
    print("=" * W)
    for k in portfolio_keys:
        print(f"  {k:<28} {metrics[k]}")
    print("  " + "-" * (W - 2))
    print("  Trade Statistics")
    print("  " + "-" * (W - 2))
    for k in trade_keys:
        print(f"  {k:<28} {metrics[k]}")
    print("=" * W)

    # ── Plot ──────────────────────────────────────────────────────────────────
    plt.figure(figsize=(6, 4))
    plt.plot(portfolio_df['Date'], portfolio_df['Portfolio_Value'], color='blue')
    plt.title('RSI-VWAP Strategy Portfolio Value')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value (₹)')
    plt.grid(True, alpha=0.3)

    def lakhs_formatter(x, pos):
        return f'₹{x / 1_00_000:.1f}L'

    plt.gca().yaxis.set_major_formatter(FuncFormatter(lakhs_formatter))
    plt.tight_layout()
    plt.savefig("Portfolio_Value.png", dpi=300, bbox_inches="tight")
    plt.show()

    return portfolio_df, metrics


# ── Current signals ───────────────────────────────────────────────────────────
def get_current_signals():
    end_date   = datetime.now()
    start_date = end_date - timedelta(days=30)

    symbols         = get_nifty_symbols()
    current_signals = []

    for symbol in symbols:
        df = fetch_stock_data(symbol, start_date, end_date)
        if df is None or len(df) < 15:
            continue

        df = calculate_rsi(df)
        df = calculate_vwap(df)
        df = generate_signals(df)

        if not df.empty:
            latest      = df.iloc[-1]
            signal_type = {1: "BUY", -1: "SELL"}.get(int(latest['Signal']), "HOLD")
            current_signals.append({
                'Symbol': symbol,
                'Date':   latest['Date'],
                'Close':  round(float(latest['Close']), 2),
                'RSI':    round(float(latest['RSI']),   2),
                'VWAP':   round(float(latest['VWAP']),  2),
                'Signal': signal_type,
            })

    if not current_signals:
        print("No current signals available – check data connection.")
        return pd.DataFrame()

    signals_df = pd.DataFrame(current_signals)

    # ── Export to CSV (date-stamped to avoid overwriting previous runs) ───────
    today      = datetime.now().strftime("%Y-%m-%d")
    signal_csv = f"signals_{today}.csv"
    signals_df.to_csv(signal_csv, index=False)
    print(f"\nSignals exported → {signal_csv}")

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\nCurrent Trading Signals:")
    print(signals_df[['Symbol', 'Close', 'RSI', 'VWAP', 'Signal']].to_string(index=False))

    buy_signals  = signals_df[signals_df['Signal'] == 'BUY']
    sell_signals = signals_df[signals_df['Signal'] == 'SELL']

    print("\nBUY Recommendations:")
    print(
        buy_signals[['Symbol', 'Close', 'RSI', 'VWAP']].to_string(index=False)
        if not buy_signals.empty else "  No buy signals for today"
    )

    print("\nSELL Recommendations:")
    print(
        sell_signals[['Symbol', 'Close', 'RSI', 'VWAP']].to_string(index=False)
        if not sell_signals.empty else "  No sell signals for today"
    )

    return signals_df


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting RSI-VWAP Trading Strategy Analysis...")
    portfolio_df, metrics = implement_portfolio_strategy()
    current_signals       = get_current_signals()