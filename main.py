import os
from datetime import datetime

from src.scanner import run_scanner
from src.portfolio import select_portfolio
from src.config import MIN_SCORE


def main():
    print("")
    print("QUANT SWING LAB")
    print("================")
    print("Running scanner...")
    print("")

    results = run_scanner(min_score=MIN_SCORE)

    print("")
    print("SCAN FINISHED")
    print("================")

    if results.empty:
        print("No stocks found.")
        return

    print(f"Total signals found: {len(results)}")

    # Selectează portofoliul final
    portfolio = select_portfolio(results)

    print("")
    print("TOP PORTFOLIO")
    print("=============")
    print(portfolio.to_string(index=False))

    # Creează reports/
    os.makedirs("reports", exist_ok=True)

    timestamp      = datetime.now().strftime("%Y%m%d_%H%M")
    signals_file   = f"reports/signals_{timestamp}.csv"
    portfolio_file = f"reports/portfolio_{timestamp}.csv"

    # Salvează toate semnalele
    results.to_csv(signals_file, index=False)

    # Salvează doar portofoliul final
    portfolio.to_csv(portfolio_file, index=False)

    print("")
    print(f"Signals   → {signals_file}  ({len(results)} stocks)")
    print(f"Portfolio → {portfolio_file}  ({len(portfolio)} stocks)")


if __name__ == "__main__":
    main()
