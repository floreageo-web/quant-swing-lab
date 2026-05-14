import yfinance as yf

from src.config import (
    UNIVERSE_FILE,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
)

MIN_BARS_REQUIRED = 200  # necesar pentru EMA200 și indicatori pe termen lung


def load_universe(file_path=UNIVERSE_FILE):
    """
    Citește lista de ticker-e din universe/stocks.txt.
    Returnează listă goală dacă fișierul nu există.
    """
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
    """
    Descarcă date bursiere pentru un ticker via yfinance.
    Returnează DataFrame gol dacă descărcarea eșuează.
    """
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    return data


def download_universe_data():
    """
    Descarcă date pentru toți ticker-ii din universe.
    Filtrează ticker-ii cu date insuficiente (< MIN_BARS_REQUIRED bare).
    """
    tickers = load_universe()

    if not tickers:
        print("[DataLoader] No tickers to download.")
        return {}

    all_data = {}
    skipped = []

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

    if skipped:
        print(f"\n[DataLoader] Skipped {len(skipped)} tickers:")
        for ticker, reason in skipped:
            print(f"  {ticker}: {reason}")

    print(f"\n[DataLoader] Loaded {len(all_data)} tickers successfully.")
    return all_data
