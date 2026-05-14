import os
import pandas as pd
from datetime import datetime

from src.data_loader import download_universe_data
from src.backtest import run_backtest_on_stock
from src.metrics import calculate_backtest_metrics
from src.config import MIN_SCORE


def main():
    print("")
    print("QUANT SWING LAB - BACKTEST")
    print("==========================")
    print("Running backtest...")
    print("")

    all_data   = download_universe_data()
    all_trades = []

    for ticker, data in all_data.items():
        print(f"[Backtest] {ticker}...")
        trades = run_backtest_on_stock(
            data=data,
            min_score=MIN_SCORE,
        )
        if not trades.empty:
            trades["ticker"] = ticker
            all_trades.append(trades)

    os.makedirs("reports", exist_ok=True)

    if not all_trades:
        print("")
        print("No trades found in backtest.")
        return

    results   = pd.concat(all_trades, ignore_index=True)
    metrics   = calculate_backtest_metrics(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    trades_file  = f"reports/backtest_trades_{timestamp}.csv"
    metrics_file = f"reports/backtest_metrics_{timestamp}.txt"

    results.to_csv(trades_file, index=False)

    with open(metrics_file, "w") as file:
        for key, value in metrics.items():
            file.write(f"{key}: {value}\n")

    print("")
    print("BACKTEST FINISHED")
    print("=================")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print("")
    print(f"Trades  → {trades_file}")
    print(f"Metrics → {metrics_file}")


if __name__ == "__main__":
    main()
