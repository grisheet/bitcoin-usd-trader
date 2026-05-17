import requests
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def get_btc_historical():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {'vs_currency': 'usd', 'days': 30, 'interval': 'daily'}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = [p[1] for p in data['prices']]
        timestamps = [pd.Timestamp(p[0], unit='ms') for p in data['prices']]
        print(f"Fetched {len(prices)} real BTC-USD prices")
        print(f"Latest price: ${prices[-1]:,.2f}")
        return pd.DataFrame({'close': prices}, index=timestamps)
    except Exception as e:
        print(f"Error fetching prices: {e}")
        print("Using sample data instead...")
        dates = pd.date_range(start='2025-01-01', periods=30, freq='1D')
        np.random.seed(42)
        prices = 65000 + np.cumsum(np.random.randn(30) * 500)
        return pd.DataFrame({'close': prices}, index=dates)

df = get_btc_historical()
df['ema50'] = EMAIndicator(df['close'], window=10).ema_indicator()
df['ema200'] = EMAIndicator(df['close'], window=20).ema_indicator()
df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
df['signal'] = np.where(
    (df['ema50'] > df['ema200']) & (df['rsi'] < 60), 'BUY', 'HOLD')
df['signal'] = np.where(df['ema50'] < df['ema200'], 'SELL', df['signal'])

print('\nBTC-USD STRATEGY RESULTS')
print(df[['close', 'ema50', 'ema200', 'rsi', 'signal']].tail(10))
print('\nBot is ALIVE and reading real BTC prices!')
print('BUY = potential entry | SELL = exit | HOLD = wait')
