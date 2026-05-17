import pandas as pd

from src.indicators import add_indicators
from src.scoring import calculate_total_score
from src.config import MIN_SCORE, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT, MAX_HOLD_DAYS


def simulate_trade(
    entry_price,
    future_data,
    stop_loss_percent=STOP_LOSS_PERCENT,
    take_profit_percent=TAKE_PROFIT_PERCENT,
    max_hold_days=MAX_HOLD_DAYS,
):
    stop_price   = entry_price * (1 - stop_loss_percent)
    target_price = entry_price * (1 + take_profit_percent)
    days         = min(max_hold_days, len(future_data))

    for i in range(days):
        candle = future_data.iloc[i]
        low    = candle["Low"]
        high   = candle["High"]

        # Stop-first: mai prudent și mai realist
        if low <= stop_price:
            return {"result": "loss", "return_pct": -stop_loss_percent, "days_held": i + 1}

        if high >= target_price:
            return {"result": "win", "return_pct": take_profit_percent, "days_held": i + 1}

    final_close = future_data.iloc[days - 1]["Close"]
    return_pct  = (final_close - entry_price) / entry_price

    return {"result": "timeout", "return_pct": round(return_pct, 4), "days_held": days}


def run_backtest_on_stock(
    data,
    spy_data=None,
    min_score=MIN_SCORE,
    stop_loss_percent=STOP_LOSS_PERCENT,
    take_profit_percent=TAKE_PROFIT_PERCENT,
    max_hold_days=MAX_HOLD_DAYS,
):
    """
    Rulează backtest pe o singură acțiune.
    - Pornește de la bara 250 (necesar pentru EMA200, Z-score, RS 60 zile)
    - SPY slice aliniat pe dată, nu pe index numeric
    """
    data   = add_indicators(data)
    trades = []

    for i in range(250, len(data) - max_hold_days):
        historical_data = data.iloc[:i]

        # SPY slice aliniat pe dată — evită desincronizare index
        spy_slice = None
        if spy_data is not None and not spy_data.empty:
            current_date = data.index[i]
            spy_slice    = spy_data.loc[:current_date]

        score_data = calculate_total_score(historical_data, spy_slice)

        if score_data["eliminated"]:
            continue

        if score_data["total_score"] < min_score:
            continue

        entry_price = data.iloc[i]["Close"]
        future_data = data.iloc[i + 1 : i + max_hold_days + 1]

        trade_result = simulate_trade(
            entry_price=entry_price,
            future_data=future_data,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent,
            max_hold_days=max_hold_days,
        )

        trades.append({
            "date":            data.index[i],
            "entry":           round(entry_price, 2),
            "score":           score_data["total_score"],
            "graph_score":     score_data["graph_score"],
            "statistic_score": score_data["statistic_score"],
            "result":          trade_result["result"],
            "return_pct":      trade_result["return_pct"],
            "days_held":       trade_result["days_held"],
        })

    return pd.DataFrame(trades)
