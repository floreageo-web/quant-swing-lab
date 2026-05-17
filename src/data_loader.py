import time
import pandas as pd
import yfinance as yf

from src.config import (
    UNIVERSE_FILE,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    BENCHMARK_TICKER,
)

MIN_BARS_REQUIRED = 250


def load_universe(file_path=UNIVERSE_FILE):
    try:
        with open(file_path, "r") as file:
            tickers = [
                line.strip()
                for line in file
                if line.strip()
            ]
        return tickers
    except FileNotFoundError:
        print(f"[DataLoader] Universe file not found: {file_path}")
        return []


def download_price_data(
    ticker,
    period=DEFAULT_PERIOD,
    interval=DEFAULT_INTERVAL,
):
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


def download_benchmark(period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL):
    """
    Descarcă datele pentru SPY ca benchmark.
    """
    print(f"[DataLoader] Downloading benchmark {BENCHMARK_TICKER}...")
    try:
        data = download_price_data(BENCHMARK_TICKER, period, interval)
        if data.empty:
            print(f"[DataLoader] Benchmark {BENCHMARK_TICKER} returned empty data.")
            return None

        # Adaugă EMA200 pentru market regime filter
        data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()
        return data

    except Exception as error:
        print(f"[DataLoader] Error downloading benchmark: {error}")
        return None


def download_universe_data():
    tickers = load_universe()

    if not tickers:
        print("[DataLoader] No tickers to download.")
        return {}

    all_data = {}
    skipped  = []

    for ticker in tickers:
        print(f"[DataLoader] Downloading {ticker}...")
        try:
            data = download_price_data(ticker)

            if data.empty:
                skipped.append((ticker, "empty data"))
                continue

            if len(data) < MIN_BARS_REQUIRED:
                skipped.append((ticker, f"only {len(data)} bars"))
                continue

            all_data[ticker] = data

        except Exception as error:
            print(f"[DataLoader] Error for {ticker}: {error}")
            skipped.append((ticker, str(error)))

        time.sleep(2)

    if skipped:
        print(f"\n[DataLoader] Skipped {len(skipped)} tickers:")
        for ticker, reason in skipped:
            print(f"  {ticker}: {reason}")

    print(f"\n[DataLoader] Loaded {len(all_data)} tickers successfully.")
    return all_data
