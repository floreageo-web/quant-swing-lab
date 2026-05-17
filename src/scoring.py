from src.structure import calculate_graph_score, detect_higher_lows
from src.config import MARKET_PENALTY


# =========================
# Z-SCORE
# =========================

def get_zscore_score(data):
    """
    Folosește Z_SCORE calculat direct în indicators.py.
    -0.5 to 0.5   → 10p
    0.5 to 1.0    → 8p
    -1.0 to -0.5  → 8p
    1.0 to 1.5    → 5p
    -1.5 to -1.0  → 5p
    1.5 to 2.0    → 2p
    -2.0 to -1.5  → 2p
    > 2 or < -2   → 0p
    """
    if "Z_SCORE" not in data.columns or len(data) < 20:
        return 0, None

    z  = data["Z_SCORE"].iloc[-1]
    az = abs(z)

    if az <= 0.5:
        return 10, z
    if az <= 1.0:
        return 8, z
    if az <= 1.5:
        return 5, z
    if az <= 2.0:
        return 2, z

    return 0, z


# =========================
# TREND EMA BULLISH
# =========================

def get_trend_score(data):
    """
    EMA20 > EMA50 > EMA200 → 10p
    """
    required = {"EMA20", "EMA50", "EMA200"}
    if not required.issubset(data.columns):
        return 0

    latest = data.iloc[-1]

    if latest["EMA20"] > latest["EMA50"] > latest["EMA200"]:
        return 10

    return 0


# =========================
# RELATIVE STRENGTH vs SPY
# =========================

def get_relative_strength_score(data, spy_data):
    """
    Bate SPY pe 20 zile → 5p
    Bate SPY pe 60 zile → 5p
    Total max: 10p
    """
    if spy_data is None or spy_data.empty:
        return 0

    score = 0

    try:
        if len(data) >= 20 and len(spy_data) >= 20:
            stock_return_20 = data["Close"].iloc[-1] / data["Close"].iloc[-20] - 1
            spy_return_20   = spy_data["Close"].iloc[-1] / spy_data["Close"].iloc[-20] - 1
            if stock_return_20 > spy_return_20:
                score += 5

        if len(data) >= 60 and len(spy_data) >= 60:
            stock_return_60 = data["Close"].iloc[-1] / data["Close"].iloc[-60] - 1
            spy_return_60   = spy_data["Close"].iloc[-1] / spy_data["Close"].iloc[-60] - 1
            if stock_return_60 > spy_return_60:
                score += 5

    except Exception:
        return 0

    return score


# =========================
# MARKET REGIME PENALTY
# =========================

def get_market_penalty(spy_data):
    """
    SPY Close < SPY EMA200 → -10p
    Altfel → 0p
    """
    if spy_data is None or spy_data.empty:
        return 0

    if "EMA200" not in spy_data.columns:
        return 0

    latest = spy_data.iloc[-1]

    if latest["Close"] < latest["EMA200"]:
        return MARKET_PENALTY

    return 0


# =========================
# STATISTIC SCORE
# =========================

def calculate_statistic_score(data, spy_data=None):
    """
    Calculează Statistic Score (max 35p).
    """
    trend_score          = get_trend_score(data)
    higher_lows          = detect_higher_lows(data)
    hl_score             = 5 if higher_lows else 0
    zscore_score, z_value = get_zscore_score(data)
    rs_score             = get_relative_strength_score(data, spy_data)

    statistic_score = trend_score + hl_score + zscore_score + rs_score

    return {
        "statistic_score":   min(statistic_score, 35),
        "trend_score":       trend_score,
        "higher_lows_score": hl_score,
        "zscore_score":      zscore_score,
        "z_score":           round(z_value, 2) if z_value is not None else None,
        "rs_score":          rs_score,
    }


# =========================
# TOTAL SCORE
# =========================

def calculate_total_score(data, spy_data=None):
    """
    Total Score = graph_score + statistic_score + market_penalty
    Max: 65 + 35 = 100
    Cu penalizare: poate scădea la -10
    """
    graph   = calculate_graph_score(data)
    stat    = calculate_statistic_score(data, spy_data)
    penalty = get_market_penalty(spy_data)

    graph_score     = graph["graph_score"]
    statistic_score = stat["statistic_score"]
    total_score     = graph_score + statistic_score + penalty

    return {
        "total_score":        total_score,
        "graph_score":        graph_score,
        "statistic_score":    statistic_score,
        "market_penalty":     penalty,
        "eliminated":         graph["eliminated"],
        "elimination_reason": graph["elimination_reason"],
        # Graph details
        "ema_retest_score":   graph["ema_retest_score"],
        "ema_retest_level":   graph["ema_retest_level"],
        "rsi_score":          graph["rsi_score"],
        "volume_dryup_score": graph["volume_dryup_score"],
        "fibonacci_score":    graph["fibonacci_score"],
        "candle_score":       graph["candle_score"],
        "atr_valid":          graph["atr_valid"],
        # Statistic details
        "trend_score":        stat["trend_score"],
        "higher_lows_score":  stat["higher_lows_score"],
        "zscore_score":       stat["zscore_score"],
        "z_score":            stat["z_score"],
        "rs_score":           stat["rs_score"],
    }
