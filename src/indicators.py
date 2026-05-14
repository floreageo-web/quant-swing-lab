from ta.momentum import RSIIndicator
from ta.momentum import ROCIndicator
from ta.volatility import AverageTrueRange
from ta.volatility import BollingerBands


def add_indicators(data):
    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Coloane lipsă din data: {missing}")

    data = data.copy()

    # EMA
    data["EMA20"] = (
        data["Close"]
        .ewm(span=20, adjust=False)
        .mean()
    )
    data["EMA50"] = (
        data["Close"]
        .ewm(span=50, adjust=False)
        .mean()
    )
    data["EMA200"] = (
        data["Close"]
        .ewm(span=200, adjust=False)
        .mean()
    )

    # RSI
    rsi = RSIIndicator(
        close=data["Close"],
        window=14
    )
    data["RSI"] = rsi.rsi()

    # ROC
    roc = ROCIndicator(
        close=data["Close"],
        window=12
    )
    data["ROC"] = roc.roc()

    # ATR
    atr = AverageTrueRange(
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        window=14
    )
    data["ATR"] = atr.average_true_range()

    # Bollinger Width
    bb = BollingerBands(
        close=data["Close"],
        window=20,
        window_dev=2
    )
    data["BB_WIDTH"] = bb.bollinger_wband()

    # Relative Volume — fillna(0) pentru primele 20 bare unde rolling e NaN
    data["REL_VOLUME"] = (
        data["Volume"] /
        data["Volume"].rolling(20).mean()
    ).fillna(0)

    return data
