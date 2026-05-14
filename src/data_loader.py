import yfinance as yf


def load_universe(file_path="universe/stocks.txt"):
    """
    Citește lista de ticker-e din universe/stocks.txt
    """

    with open(file_path, "r") as file:

        tickers = []

        for line in file:

            ticker = line.strip()

            if ticker:
                tickers.append(ticker)

    return tickers


def download_price_data(
    ticker,
    period="1y",
    interval="1d"
):
    """
    Descarcă date bursiere pentru un ticker.
    """

    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    return data


def download_universe_data():

    tickers = load_universe()

    all_data = {}

    for ticker in tickers:

        print(f"Downloading {ticker}...")

        try:

            data = download_price_data(ticker)

            if not data.empty:
                all_data[ticker] = data

        except Exception as error:

            print(f"Error for {ticker}: {error}")

    return all_data
