from src.structure import analyze_structure


def calculate_trend_score(data):
    """
    Scor trend 0-20.
    Verifică alinierea EMA și direcția prețului pe 20 de zile.
    """

    required_columns = {"Close", "EMA20", "EMA50", "EMA200"}

    if not required_columns.issubset(data.columns):
        return 0

    if len(data) < 20:
        return 0

    score = 0
    latest = data.iloc[-1]

    if latest["Close"] > latest["EMA20"]:
        score += 5

    if latest["EMA20"] > latest["EMA50"]:
        score += 5

    if latest["EMA50"] > latest["EMA200"]:
        score += 5

    if data["Close"].iloc[-1] > data["Close"].iloc[-20]:
        score += 5

    return min(score, 20)


def calculate_momentum_score(data):
    """
    Scor momentum 0-20.
    Folosește RSI și ROC.
    """

    required_columns = {"RSI", "ROC"}

    if not required_columns.issubset(data.columns):
        return 0

    if len(data) < 20:
        return 0

    score = 0
    latest = data.iloc[-1]

    if 50 <= latest["RSI"] <= 75:
        score += 8

    if latest["ROC"] > 0:
        score += 6

    recent_roc = data["ROC"].tail(5).mean()
    previous_roc = data["ROC"].tail(20).mean()

    if recent_roc > previous_roc:
        score += 6

    return min(score, 20)


def calculate_compression_score(data):
    """
    Scor compresie 0-20.
    Folosește ATR contraction, Bollinger squeeze și tight range.
    """

    required_columns = {"ATR", "BB_WIDTH", "High", "Low"}

    if not required_columns.issubset(data.columns):
        return 0

    if len(data) < 60:
        return 0

    score = 0

    recent_atr = data["ATR"].tail(5).mean()
    previous_atr = data["ATR"].iloc[-30:-5].mean()

    if recent_atr < previous_atr:
        score += 7

    current_width = data["BB_WIDTH"].iloc[-1]
    historical_width = data["BB_WIDTH"].tail(60).quantile(0.25)

    if current_width < historical_width:
        score += 7

    recent_low = data["Low"].tail(10).min()

    if recent_low > 0:
        recent_range = (
            data["High"].tail(10).max()
            - recent_low
        ) / recent_low

        if recent_range < 0.06:
            score += 6

    return min(score, 20)


def calculate_volume_score(data):
    """
    Scor volum 0-20.
    Verifică volum relativ și volum exploziv.
    """

    required_columns = {"REL_VOLUME", "Volume"}

    if not required_columns.issubset(data.columns):
        return 0

    if len(data) < 20:
        return 0

    score = 0
    latest = data.iloc[-1]

    if latest["REL_VOLUME"] > 1.5:
        score += 10

    average_volume_20 = data["Volume"].tail(20).mean()

    if average_volume_20 > 0:
        if latest["Volume"] > average_volume_20 * 2:
            score += 10

    return min(score, 20)


def calculate_total_score(data):
    """
    Scor total 0-100.

    Componente:
    - Trend: 0-20
    - Momentum: 0-20
    - Compression: 0-20
    - Volume: 0-20
    - Structure: 0-20
    """

    trend_score = calculate_trend_score(data)
    momentum_score = calculate_momentum_score(data)
    compression_score = calculate_compression_score(data)
    volume_score = calculate_volume_score(data)

    structure = analyze_structure(data)
    structure_score = structure["structure_score"]

    total_score = (
        trend_score
        + momentum_score
        + compression_score
        + volume_score
        + structure_score
    )

    return {
        "total_score": total_score,
        "trend_score": trend_score,
        "momentum_score": momentum_score,
        "compression_score": compression_score,
        "volume_score": volume_score,
        "structure_score": structure_score,
        "structure": structure,
    }
