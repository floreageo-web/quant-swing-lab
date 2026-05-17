from ta.momentum import RSIIndicator
from ta.momentum import ROCIndicator
from ta.volatility import AverageTrueRange
from ta.volatility import BollingerBands

from src.config import (
    EMA_FAST,
    EMA_MEDIUM,
    EMA_SLOW,
    EMA_TREND,
    RSI_WINDOW,
    ROC_WINDOW,
    ATR_WINDOW,
    BOLLINGER_WINDOW,
    BOLLINGER_STD,
)


def add_indicators(data):
    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Coloane lipsă din data: {missing}")

    data = data.copy()

    # EMA
    data["EMA20"]  = data["Close"].ewm(span=EMA_FAST,   adjust=False).mean()
    data["EMA50"]  = data["Close"].ewm(span=EMA_MEDIUM, adjust=False).mean()
    data["EMA100"] = data["Close"].ewm(span=EMA_SLOW,   adjust=False).mean()
    data["EMA200"] = data["Close"].ewm(span=EMA_TREND,  adjust=False).mean()

    # RSI
    rsi = RSIIndicator(close=data["Close"], window=RSI_WINDOW)
    data["RSI"] = rsi.rsi()

    # ROC
    roc = ROCIndicator(close=data["Close"], window=ROC_WINDOW)
    data["ROC"] = roc.roc()

    # ATR
    atr = AverageTrueRange(
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        window=ATR_WINDOW,
    )
    data["ATR"]     = atr.average_true_range()
    data["ATR_PCT"] = (data["ATR"] / data["Close"]) * 100

    # Bollinger Width
    bb = BollingerBands(
        close=data["Close"],
        window=BOLLINGER_WINDOW,
        window_dev=BOLLINGER_STD,
    )
    data["BB_WIDTH"] = bb.bollinger_wband()

    # Relative Volume
    data["REL_VOLUME"] = (
        data["Volume"] / data["Volume"].rolling(20).mean()
    ).fillna(0)

    # MA20 + STD20 pentru Z-Score
    data["MA20"]    = data["Close"].rolling(20).mean()
    data["STD20"]   = data["Close"].rolling(20).std()

    # Z-Score calculat direct aici
    data["Z_SCORE"] = (data["Close"] - data["MA20"]) / data["STD20"]

    return data
