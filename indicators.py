import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def add_indicators(df):
    df = df.copy()
    df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    return df

def add_signals(df):
    df = df.copy()
    df['signal'] = 'HOLD'
    buy_mask = (df['ema50'] > df['ema200']) & (df['rsi'] < 60)
    df.loc[buy_mask, 'signal'] = 'BUY'
    sell_mask = df['ema50'] < df['ema200']
    df.loc[sell_mask, 'signal'] = 'SELL'
    return df

def process(df):
    df = add_indicators(df)
    df = add_signals(df)
    return df

if __name__ == '__main__':
    dates = pd.date_range('2025-01-01', periods=250, freq='4h')
    np.random.seed(42)
    prices = 65000 + np.cumsum(np.random.randn(250) * 100)
    df = pd.DataFrame({'close': prices}, index=dates)
    df = process(df)
    print('Indicators module test')
    print(df.tail(5)[['close', 'ema50', 'ema200', 'rsi', 'signal']])
    print('Module working correctly!')
