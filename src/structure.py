import numpy as np
from src.config import (
    EMA_RETEST_THRESHOLD,
    FIBONACCI_LOOKBACK,
    PULLBACK_MAX_DAYS,
    MIN_BREAKOUT_VOLUME_RATIO,
)


# =========================
# EMA RETEST
# =========================

def detect_ema_retest(data, ema_col):
    """
    Detectează retest pe EMA specificată.
    Condiții:
    - Prețul (low sau close) e la maxim EMA_RETEST_THRESHOLD distanță de EMA
    - Close e deasupra EMA
    - Close e în treimea superioară a lumânării (respingere)
    """
    if ema_col not in data.columns or len(data) < 2:
        return False

    latest = data.iloc[-1]
    ema_val = latest[ema_col]
    close   = latest["Close"]
    low     = latest["Low"]
    high    = latest["High"]

    if ema_val == 0:
        return False

    # Distanța low față de EMA
    distance = abs(low - ema_val) / ema_val

    # Close deasupra EMA
    close_above = close > ema_val

    # Respingere — close în treimea superioară
    if high == low:
        return False
    close_strength = (close - low) / (high - low)
    strong_close = close_strength >= 0.70

    return distance <= EMA_RETEST_THRESHOLD and close_above and strong_close


def get_ema_retest_score(data):
    """
    Returnează scorul EMA retest — doar cel mai bun nivel, nu cumulativ.
    EMA20 → 15p, EMA50 → 12p, EMA100 → 8p
    """
    if detect_ema_retest(data, "EMA20"):
        return 15, "EMA20"
    if detect_ema_retest(data, "EMA50"):
        return 12, "EMA50"
    if detect_ema_retest(data, "EMA100"):
        return 8, "EMA100"
    return 0, None


# =========================
# RSI ZONE
# =========================

def get_rsi_score(data):
    """
    RSI 40-55 → 10p, RSI 35-40 → 5p, RSI 55-60 → 5p
    Eliminare: RSI < 35 sau RSI > 65
    """
    if "RSI" not in data.columns:
        return 0, False

    rsi = data["RSI"].iloc[-1]

    if rsi < 35 or rsi > 65:
        return 0, True  # eliminat

    if 40 <= rsi <= 55:
        return 10, False
    if 35 <= rsi < 40:
        return 5, False
    if 55 < rsi <= 60:
        return 5, False

    return 0, False


# =========================
# ATR FILTER
# =========================

def check_atr_filter(data):
    """
    Returnează True dacă ATR% e în interval valid (1.5% - 5%).
    Nu oferă puncte — doar filtru eliminatoriu.
    """
    if "ATR_PCT" not in data.columns:
        return False

    atr_pct = data["ATR_PCT"].iloc[-1]
    return 1.5 <= atr_pct <= 5.0


# =========================
# VOLUME DRY-UP
# =========================

def get_volume_dryup_score(data):
    """
    Detectează breakout cu volum + pullback pe volum mic (seller exhaustion).

    Breakout Day:
    - Close > max High ultimele 20 zile
    - Volume > 1.5x media volumului pe 20 zile

    Pullback:
    - Maxim 5 zile bursiere după breakout
    - Pullback Ratio = V-PB / V-BO

    Scoring:
    - < 35%  → 20p
    - 35-50% → 15p
    - 50-70% → 8p
    - 70-90% → 3p
    - > 90%  → 0p
    """
    if len(data) < 25:
        return 0, False

    # Caută breakout în ultimele PULLBACK_MAX_DAYS + 1 zile
    breakout_idx = None
    breakout_volume = None

    for i in range(PULLBACK_MAX_DAYS + 1, 0, -1):
        idx = len(data) - i
        if idx < 21:
            continue

        candle        = data.iloc[idx]
        prev_high_20  = data["High"].iloc[idx - 20:idx].max()
        avg_vol_20    = data["Volume"].iloc[idx - 20:idx].mean()

        is_breakout = (
            candle["Close"] > prev_high_20 and
            candle["Volume"] > avg_vol_20 * MIN_BREAKOUT_VOLUME_RATIO
        )

        if is_breakout:
            breakout_idx    = idx
            breakout_volume = candle["Volume"]
            break

    if breakout_idx is None:
        return 0, False

    # Verifică dacă pullback-ul e în limita PULLBACK_MAX_DAYS
    pullback_bars = len(data) - 1 - breakout_idx

    if pullback_bars > PULLBACK_MAX_DAYS:
        return 0, True  # eliminat — pullback prea lung

    if pullback_bars == 0:
        # Suntem chiar pe ziua breakout-ului
        return 20, False

    # Calculează Pullback Ratio
    pullback_data   = data.iloc[breakout_idx + 1:]
    avg_pb_volume   = pullback_data["Volume"].mean()
    pullback_ratio  = avg_pb_volume / breakout_volume if breakout_volume > 0 else 1

    if pullback_ratio < 0.35:
        return 20, False
    if pullback_ratio < 0.50:
        return 15, False
    if pullback_ratio < 0.70:
        return 8, False
    if pullback_ratio < 0.90:
        return 3, False

    return 0, False


# =========================
# FIBONACCI RETEST
# =========================

def get_fibonacci_score(data):
    """
    Detectează retest pe niveluri Fibonacci 38.2% sau 50%.
    Swing calculat pe ultimele FIBONACCI_LOOKBACK bare.
    """
    if len(data) < FIBONACCI_LOOKBACK:
        return 0

    recent = data.tail(FIBONACCI_LOOKBACK)
    swing_low  = recent["Low"].min()
    swing_high = recent["High"].max()

    if swing_high == swing_low:
        return 0

    current_close = data["Close"].iloc[-1]
    fib_range     = swing_high - swing_low

    fib_382 = swing_high - fib_range * 0.382
    fib_500 = swing_high - fib_range * 0.500

    tolerance = fib_range * 0.02  # 2% toleranță

    if abs(current_close - fib_382) <= tolerance:
        return 5
    if abs(current_close - fib_500) <= tolerance:
        return 3

    return 0


# =========================
# CANDLE CONFIRMATION
# =========================

def detect_hammer(data):
    """
    Hammer: coadă jos > 2x corpul, corp mic în treimea superioară.
    """
    latest = data.iloc[-1]
    open_  = latest["Open"]
    close  = latest["Close"]
    high   = latest["High"]
    low    = latest["Low"]

    body      = abs(close - open_)
    lower_wick = min(open_, close) - low
    upper_wick = high - max(open_, close)
    total_range = high - low

    if total_range == 0:
        return False

    return (
        lower_wick >= 2 * body and
        upper_wick <= body * 0.5 and
        close > open_ and
        (close - low) / total_range >= 0.60
    )


def detect_pin_bar(data):
    """
    Pin bar: coadă jos lungă (>60% din range), close aproape de high.
    """
    latest = data.iloc[-1]
    close  = latest["Close"]
    high   = latest["High"]
    low    = latest["Low"]
    open_  = latest["Open"]

    total_range = high - low
    if total_range == 0:
        return False

    lower_wick  = min(open_, close) - low
    close_strength = (close - low) / total_range

    return (
        lower_wick / total_range >= 0.60 and
        close_strength >= 0.70
    )


def detect_bullish_engulfing(data):
    """
    Bullish engulfing: lumânare roșie urmată de verde care o acoperă complet.
    """
    if len(data) < 2:
        return False

    prev    = data.iloc[-2]
    current = data.iloc[-1]

    prev_bearish    = prev["Close"] < prev["Open"]
    current_bullish = current["Close"] > current["Open"]
    engulfs         = (
        current["Open"] <= prev["Close"] and
        current["Close"] >= prev["Open"]
    )

    return prev_bearish and current_bullish and engulfs


def get_candle_score(data):
    """
    15p dacă există oricare candle de confirmare. Nu se cumulează.
    """
    if detect_hammer(data) or detect_pin_bar(data) or detect_bullish_engulfing(data):
        return 15
    return 0


# =========================
# HIGHER LOWS
# =========================

def detect_higher_lows(data, lookback=3):
    if len(data) < lookback:
        return False

    recent_lows = data["Low"].tail(lookback)
    return all(
        recent_lows.iloc[i] > recent_lows.iloc[i - 1]
        for i in range(1, len(recent_lows))
    )


# =========================
# GRAPH SCORE
# =========================

def calculate_graph_score(data):
    """
    Calculează Graph Score (max 65p) și filtrele eliminatorii.
    Returnează scorul și un dict cu detalii.
    """
    details = {}
    eliminated = False
    elimination_reason = None

    # A. EMA Retest — 15p
    ema_score, ema_level = get_ema_retest_score(data)
    details["ema_retest_score"] = ema_score
    details["ema_retest_level"] = ema_level

    # B. RSI Zone — 10p
    rsi_score, rsi_eliminated = get_rsi_score(data)
    details["rsi_score"] = rsi_score
    if rsi_eliminated:
        eliminated = True
        elimination_reason = "RSI out of range"

    # C. ATR Filter — eliminatoriu
    atr_valid = check_atr_filter(data)
    details["atr_valid"] = atr_valid
    if not atr_valid:
        eliminated = True
        elimination_reason = elimination_reason or "ATR% out of range"

    # D. Volume Dry-Up — 20p
    vol_score, vol_eliminated = get_volume_dryup_score(data)
    details["volume_dryup_score"] = vol_score
    if vol_eliminated:
        eliminated = True
        elimination_reason = elimination_reason or "Pullback > 5 days"

    # E. Fibonacci — 5p
    fib_score = get_fibonacci_score(data)
    details["fibonacci_score"] = fib_score

    # F. Candle Confirmation — 15p
    candle_score = get_candle_score(data)
    details["candle_score"] = candle_score

    graph_score = ema_score + rsi_score + vol_score + fib_score + candle_score

    return {
        "graph_score":        min(graph_score, 65),
        "eliminated":         eliminated,
        "elimination_reason": elimination_reason,
        **details,
    }
