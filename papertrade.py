# papertrade.py - Paper Trading Simulator for BTC-USD Trading Bot

import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from indicators import EMAIndicator, RSIIndicator
from riskmanager import calculate_position_size, calculate_stop_loss, calculate_take_profit

# Paper trading state
portfolio = {
    'cash': 10000.0,
    'btc': 0.0,
    'entry_price': 0.0,
    'stop_loss': 0.0,
    'take_profit': 0.0,
    'trades': []
}


def get_live_price():
    """Fetch the current BTC-USD price from CoinGecko."""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def get_historical_prices(days=30):
    """Fetch historical BTC-USD prices for indicator calculation."""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
        params = {'vs_currency': 'usd', 'days': days, 'interval': 'daily'}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = [p[1] for p in data['prices']]
        return pd.DataFrame({'close': prices})
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None


def generate_signal(df):
    """Generate trading signal from indicators."""
    df['ema50'] = EMAIndicator(df['close'], window=10).ema_indicator()
    df['ema200'] = EMAIndicator(df['close'], window=20).ema_indicator()
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    signal = np.where(
        (df['ema50'] > df['ema200']) & (df['rsi'] < 60), 'BUY',
        np.where(df['ema50'] < df['ema200'], 'SELL', 'HOLD')
    )
    return signal[-1]


def execute_paper_trade(signal, price):
    """Execute a paper trade based on the signal."""
    global portfolio
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if signal == 'BUY' and portfolio['btc'] == 0 and portfolio['cash'] > 0:
        btc_units, position_usd = calculate_position_size(portfolio['cash'], price)
        if position_usd <= portfolio['cash']:
            portfolio['btc'] = btc_units
            portfolio['cash'] -= position_usd
            portfolio['entry_price'] = price
            portfolio['stop_loss'] = calculate_stop_loss(price)
            portfolio['take_profit'] = calculate_take_profit(price)
            trade = {
                'time': timestamp, 'type': 'BUY', 'price': price,
                'units': btc_units, 'value': position_usd
            }
            portfolio['trades'].append(trade)
            print(f"[{timestamp}] PAPER BUY: {btc_units:.6f} BTC @ ${price:,.2f}")
            print(f"  Stop Loss: ${portfolio['stop_loss']:,.2f} | Take Profit: ${portfolio['take_profit']:,.2f}")

    elif portfolio['btc'] > 0:
        should_sell = (
            signal == 'SELL' or
            price <= portfolio['stop_loss'] or
            price >= portfolio['take_profit']
        )
        if should_sell:
            sell_value = portfolio['btc'] * price
            pnl = sell_value - (portfolio['btc'] * portfolio['entry_price'])
            reason = 'SIGNAL' if signal == 'SELL' else ('STOP_LOSS' if price <= portfolio['stop_loss'] else 'TAKE_PROFIT')
            portfolio['cash'] += sell_value
            trade = {
                'time': timestamp, 'type': 'SELL', 'price': price,
                'units': portfolio['btc'], 'value': sell_value,
                'pnl': pnl, 'reason': reason
            }
            portfolio['trades'].append(trade)
            print(f"[{timestamp}] PAPER SELL ({reason}): {portfolio['btc']:.6f} BTC @ ${price:,.2f}")
            print(f"  PnL: ${pnl:,.2f}")
            portfolio['btc'] = 0
            portfolio['entry_price'] = 0


def print_portfolio_status(price):
    """Print current portfolio status."""
    portfolio_value = portfolio['cash'] + portfolio['btc'] * price
    initial = 10000
    pnl_pct = (portfolio_value - initial) / initial * 100
    print(f"\n--- Portfolio Status ---")
    print(f"Cash: ${portfolio['cash']:,.2f}")
    print(f"BTC Held: {portfolio['btc']:.6f} BTC (${portfolio['btc'] * price:,.2f})")
    print(f"Total Value: ${portfolio_value:,.2f}")
    print(f"Total PnL: {pnl_pct:+.2f}%")
    print(f"Total Trades: {len(portfolio['trades'])}")
    print("------------------------\n")


def run_paper_trader(interval_seconds=60):
    """Main paper trading loop."""
    print("Starting BTC-USD Paper Trader...")
    print(f"Initial Capital: ${portfolio['cash']:,.2f}")
    print(f"Checking signals every {interval_seconds} seconds")
    print("Press Ctrl+C to stop\n")

    while True:
        try:
            price = get_live_price()
            if price is None:
                time.sleep(interval_seconds)
                continue

            df = get_historical_prices(days=30)
            if df is None:
                time.sleep(interval_seconds)
                continue

            # Add current price to end of dataframe
            current_row = pd.DataFrame({'close': [price]})
            df = pd.concat([df, current_row], ignore_index=True)

            signal = generate_signal(df)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC: ${price:,.2f} | Signal: {signal}")

            execute_paper_trade(signal, price)
            print_portfolio_status(price)

            time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\nPaper trader stopped.")
            print_portfolio_status(get_live_price() or portfolio['entry_price'])
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval_seconds)


if __name__ == '__main__':
    run_paper_trader(interval_seconds=60)
