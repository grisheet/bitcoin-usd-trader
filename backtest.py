# backtest.py - Backtesting Engine for BTC-USD Trading Bot

import pandas as pd
import numpy as np
from indicators import EMAIndicator, RSIIndicator
from strategytester import generate_signals
from riskmanager import calculate_position_size, calculate_stop_loss, calculate_take_profit


def run_backtest(df, initial_capital=10000, risk_pct=0.01):
    """
    Run a backtest on historical price data.
    Returns a DataFrame with trade results and portfolio performance.
    """
    df = df.copy()
    df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    df['signal'] = np.where(
        (df['ema50'] > df['ema200']) & (df['rsi'] < 60), 'BUY',
        np.where(df['ema50'] < df['ema200'], 'SELL', 'HOLD')
    )

    capital = initial_capital
    position = 0  # BTC units held
    entry_price = 0
    trades = []
    portfolio_values = []

    for i, row in df.iterrows():
        price = row['close']
        signal = row['signal']
        portfolio_value = capital + position * price
        portfolio_values.append(portfolio_value)

        if signal == 'BUY' and position == 0 and capital > 0:
            btc_units, position_usd = calculate_position_size(capital, price, risk_pct)
            if position_usd <= capital:
                position = btc_units
                capital -= position_usd
                entry_price = price
                stop_loss = calculate_stop_loss(price)
                take_profit = calculate_take_profit(price)
                trades.append({
                    'type': 'BUY',
                    'price': price,
                    'units': btc_units,
                    'capital': capital,
                    'portfolio': portfolio_value
                })

        elif position > 0:
            if signal == 'SELL' or price <= calculate_stop_loss(entry_price) or price >= calculate_take_profit(entry_price):
                sell_value = position * price
                pnl = sell_value - (position * entry_price)
                capital += sell_value
                trades.append({
                    'type': 'SELL',
                    'price': price,
                    'units': position,
                    'pnl': pnl,
                    'capital': capital,
                    'portfolio': portfolio_value
                })
                position = 0
                entry_price = 0

    final_portfolio = capital + position * df['close'].iloc[-1]
    total_return = (final_portfolio - initial_capital) / initial_capital * 100
    num_trades = len([t for t in trades if t['type'] == 'SELL'])
    winning_trades = len([t for t in trades if t['type'] == 'SELL' and t.get('pnl', 0) > 0])
    win_rate = (winning_trades / num_trades * 100) if num_trades > 0 else 0

    print("\n=== BACKTEST RESULTS ===")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Portfolio: ${final_portfolio:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Number of Trades: {num_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    print("========================\n")

    return trades, portfolio_values, final_portfolio


if __name__ == '__main__':
    # Generate sample data for testing
    dates = pd.date_range(start='2024-01-01', periods=365)
    np.random.seed(42)
    prices = 40000 + np.cumsum(np.random.randn(365) * 500)
    df = pd.DataFrame({'close': prices}, index=dates)
    run_backtest(df)
