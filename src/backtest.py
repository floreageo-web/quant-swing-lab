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
    """
    Simulează un trade simplu cu stop loss, take profit și timeout.

    Logică stop-first: dacă o lumânare atinge atât stop cât și target,
    stop-ul câștigă — abordare conservatoare și mai realistă (intraday
    stop-ul e de obicei lovit înainte de revenire).
    """
    stop_price   = entry_price * (1 - stop_loss_percent)
    target_price = entry_price * (1 + take_profit_percent)

    days = min(max_hold_days, len(future_data))

    for i in range(days):
        candle = future_data.iloc[i]
        low    = candle["Low"]
        high   = candle["High"]

        hit_stop   = low <= stop_price
        hit_target = high >= target_price

        # Stop-first: mai prudent și mai realist
        if hit_stop:
            return {
                "result":     "loss",
                "return_pct": -stop_loss_percent,
                "days_held":  i + 1,
            }

        if hit_target:
            return {
                "result":     "win",
                "return_pct": take_profit_percent,
                "days_held":  i + 1,
            }

    # Timeout — exit la close-ul ultimei zile
    final_close = future_data.iloc[days - 1]["Close"]
    return_pct  = (final_close - entry_price) / entry_price

    return {
        "result":     "timeout",
        "return_pct": round(return_pct, 4),
        "days_held":  days,
    }


def run_backtest_on_stock(
    data,
    min_score=MIN_SCORE,
    stop_loss_percent=STOP_LOSS_PERCENT,
    take_profit_percent=TAKE_PROFIT_PERCENT,
    max_hold_days=MAX_HOLD_DAYS,
):
    """
    Rulează backtest pe o singură acțiune.

    Notă: add_indicators e aplicat pe întreg dataframe-ul înainte de loop
    pentru performanță. Asta introduce un look-ahead bias minor pe indicatori
    ca EMA200 (primele bare vor fi mai precise decât ar fi fost în timp real).
    Pentru backtesting strict, mută add_indicators în loop pe historical_data.
    """
    data   = add_indicators(data)
    trades = []

    for i in range(250, len(data) - max_hold_days):
        historical_data = data.iloc[:i]
        score_data      = calculate_total_score(historical_data)
        total_score     = score_data["total_score"]

        if total_score >= min_score:
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
                "date":       data.index[i],
                "entry":      round(entry_price, 2),
                "score":      total_score,
                "result":     trade_result["result"],
                "return_pct": trade_result["return_pct"],
                "days_held":  trade_result["days_held"],
            })

    return pd.DataFrame(trades)
