# riskmanager.py - Risk Management for BTC-USD Trading Bot

PORTFOLIO_VALUE = 10000  # Starting portfolio value in USD
RISK_PER_TRADE = 0.01   # Risk 1% per trade
MAX_POSITION_SIZE = 0.25  # Max 25% of portfolio in one trade
STOP_LOSS_PCT = 0.02    # 2% stop loss
TAKE_PROFIT_PCT = 0.04  # 4% take profit (2:1 reward/risk)


def calculate_position_size(portfolio_value, btc_price, risk_pct=RISK_PER_TRADE):
    """
    Calculate position size based on risk percentage.
    Returns number of BTC units to buy.
    """
    risk_amount = portfolio_value * risk_pct
    stop_loss_amount = btc_price * STOP_LOSS_PCT
    position_size_usd = risk_amount / STOP_LOSS_PCT
    position_size_usd = min(position_size_usd, portfolio_value * MAX_POSITION_SIZE)
    btc_units = position_size_usd / btc_price
    return round(btc_units, 6), round(position_size_usd, 2)


def calculate_stop_loss(entry_price, direction='long'):
    """
    Calculate stop loss price.
    """
    if direction == 'long':
        return round(entry_price * (1 - STOP_LOSS_PCT), 2)
    else:
        return round(entry_price * (1 + STOP_LOSS_PCT), 2)


def calculate_take_profit(entry_price, direction='long'):
    """
    Calculate take profit price.
    """
    if direction == 'long':
        return round(entry_price * (1 + TAKE_PROFIT_PCT), 2)
    else:
        return round(entry_price * (1 - TAKE_PROFIT_PCT), 2)


def check_risk_limits(portfolio_value, current_exposure):
    """
    Check if current exposure exceeds risk limits.
    Returns True if within limits, False if exceeded.
    """
    exposure_pct = current_exposure / portfolio_value
    if exposure_pct > MAX_POSITION_SIZE:
        print(f"WARNING: Position size {exposure_pct:.1%} exceeds max {MAX_POSITION_SIZE:.1%}")
        return False
    return True


def risk_report(portfolio_value, btc_price, signal):
    """
    Generate a risk report for a potential trade.
    """
    btc_units, position_usd = calculate_position_size(portfolio_value, btc_price)
    stop_loss = calculate_stop_loss(btc_price)
    take_profit = calculate_take_profit(btc_price)
    risk_amount = portfolio_value * RISK_PER_TRADE
    reward_amount = risk_amount * 2

    print("\n--- RISK MANAGEMENT REPORT ---")
    print(f"Signal: {signal}")
    print(f"BTC Price: ${btc_price:,.2f}")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Position Size: {btc_units} BTC (${position_usd:,.2f})")
    print(f"Stop Loss: ${stop_loss:,.2f} (-{STOP_LOSS_PCT:.1%})")
    print(f"Take Profit: ${take_profit:,.2f} (+{TAKE_PROFIT_PCT:.1%})")
    print(f"Max Risk: ${risk_amount:,.2f} ({RISK_PER_TRADE:.1%} of portfolio)")
    print(f"Potential Reward: ${reward_amount:,.2f}")
    print(f"Reward/Risk Ratio: 2:1")
    print("------------------------------\n")


if __name__ == '__main__':
    # Example usage
    portfolio = 10000
    btc_price = 65000
    signal = 'BUY'
    risk_report(portfolio, btc_price, signal)
