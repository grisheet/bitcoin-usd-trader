import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

dates = pd.date_range(start='2025-01-01', periods=250, freq='4h')
np.random.seed(42)
close_prices = 65000 + np.cumsum(np.random.randn(250) * 100)
df = pd.DataFrame({'close': close_prices}, index=dates)

df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
df['rsi'] = RSIIndicator(df['close'], window=14).rsi()

df['signal'] = np.where(
    (df['ema50'] > df['ema200']) & (df['rsi'] < 60), 'BUY', 'HOLD')
df['signal'] = np.where(df['ema50'] < df['ema200'], 'SELL', df['signal'])

print('Last 10 BTC-USD candles with YOUR strategy signals')
print(df.tail(10)[['close', 'ema50', 'ema200', 'rsi', 'signal']])
df.to_csv('btc_backtest_results.csv')
print('Full backtest saved to btc_backtest_results.csv')
print('BUY signals = potential entry points')
print('SELL signals = exit points')
print('This is FAKE data - real results may differ')
