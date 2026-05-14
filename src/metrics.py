def calculate_backtest_metrics(trades):
    """
    Calculează metrici pentru rezultatele backtestului.

    Expectancy = (win_rate x avg_win) - (loss_rate x avg_loss)
    Profit Factor = total_profit / total_loss
    """
    if trades.empty:
        return {
            "total_trades":   0,
            "win_rate":       0,
            "average_return": 0,
            "expectancy":     0,
            "profit_factor":  0,
            "avg_win":        0,
            "avg_loss":       0,
            "avg_days_held":  0,
            "wins":           0,
            "losses":         0,
            "timeouts":       0,
        }

    total_trades = len(trades)

    # Separare pe tip rezultat — nu pe semn return_pct
    wins     = trades[trades["result"] == "win"]
    losses   = trades[trades["result"] == "loss"]
    timeouts = trades[trades["result"] == "timeout"]

    win_rate  = len(wins) / total_trades
    loss_rate = len(losses) / total_trades

    avg_win  = wins["return_pct"].mean() if not wins.empty else 0
    avg_loss = abs(losses["return_pct"].mean()) if not losses.empty else 0

    average_return = trades["return_pct"].mean()

    # Expectancy corectă: (win_rate × avg_win) - (loss_rate × avg_loss)
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)

    total_profit = wins["return_pct"].sum()
    total_loss   = abs(losses["return_pct"].sum())

    if total_loss == 0:
        profit_factor = float("inf")
    else:
        profit_factor = total_profit / total_loss

    avg_days_held = trades["days_held"].mean() if "days_held" in trades.columns else 0

    return {
        "total_trades":   total_trades,
        "wins":           len(wins),
        "losses":         len(losses),
        "timeouts":       len(timeouts),
        "win_rate":       round(win_rate, 4),
        "average_return": round(average_return, 4),
        "avg_win":        round(avg_win, 4),
        "avg_loss":       round(avg_loss, 4),
        "expectancy":     round(expectancy, 4),
        "profit_factor":  round(profit_factor, 4) if profit_factor != float("inf") else profit_factor,
        "avg_days_held":  round(avg_days_held, 1),
    }
