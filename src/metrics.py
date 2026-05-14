def calculate_backtest_metrics(trades):
    """
    Calculează metrici simple pentru rezultatele backtestului.
    """

    if trades.empty:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "average_return": 0,
            "expectancy": 0,
            "profit_factor": 0,
        }

    total_trades = len(trades)

    wins = trades[trades["return_pct"] > 0]
    losses = trades[trades["return_pct"] < 0]

    win_rate = len(wins) / total_trades

    average_return = trades["return_pct"].mean()

    total_profit = wins["return_pct"].sum()
    total_loss = abs(losses["return_pct"].sum())

    if total_loss == 0:
        profit_factor = float("inf")
    else:
        profit_factor = total_profit / total_loss

    expectancy = average_return

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 4),
        "average_return": round(average_return, 4),
        "expectancy": round(expectancy, 4),
        "profit_factor": round(profit_factor, 4)
        if profit_factor != float("inf")
        else profit_factor,
    }
