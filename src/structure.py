def detect_higher_lows(data, lookback=3):
    """
    Detectează higher lows consecutive.
    lookback=3 e mai robust pe daily față de 5.
    """
    if len(data) < lookback:
        return False

    recent_lows = data["Low"].tail(lookback)

    return all(
        recent_lows.iloc[i] > recent_lows.iloc[i - 1]
        for i in range(1, len(recent_lows))
    )


def detect_tight_range(data, lookback=10, threshold=0.06):
    """
    Detectează consolidare strânsă: range% < threshold în ultimele `lookback` bare.
    """
    if len(data) < lookback:
        return False

    recent_high = data["High"].tail(lookback).max()
    recent_low = data["Low"].tail(lookback).min()

    if recent_low == 0:
        return False

    range_percent = (recent_high - recent_low) / recent_low

    return range_percent < threshold


def detect_breakout_20(data):
    """
    Close curent > maximul High din ultimele 20 de sesiuni (exclusiv ziua curentă).
    Dacă breakout_50 e True, acest semnal e ignorat în scoring (evităm dublu-punctaj).
    """
    if len(data) < 21:
        return False

    previous_high = data["High"].iloc[-21:-1].max()
    current_close = data["Close"].iloc[-1]

    return current_close > previous_high


def detect_breakout_50(data):
    """
    Close curent > maximul High din ultimele 50 de sesiuni (exclusiv ziua curentă).
    """
    if len(data) < 51:
        return False

    previous_high = data["High"].iloc[-51:-1].max()
    current_close = data["Close"].iloc[-1]

    return current_close > previous_high


def detect_reclaim_ema20(data):
    """
    Close trece deasupra EMA20 față de ziua precedentă (crossover bullish).
    """
    if "EMA20" not in data.columns or len(data) < 2:
        return False

    yesterday = data.iloc[-2]
    today = data.iloc[-1]

    return yesterday["Close"] < yesterday["EMA20"] and today["Close"] > today["EMA20"]


def detect_reclaim_ema50(data):
    """
    Close trece deasupra EMA50 față de ziua precedentă (crossover bullish).
    """
    if "EMA50" not in data.columns or len(data) < 2:
        return False

    yesterday = data.iloc[-2]
    today = data.iloc[-1]

    return yesterday["Close"] < yesterday["EMA50"] and today["Close"] > today["EMA50"]


def detect_close_strength(data, threshold=0.7):
    """
    Close în treimea superioară a range-ului zilei (putere la închidere).
    """
    latest = data.iloc[-1]

    high = latest["High"]
    low = latest["Low"]
    close = latest["Close"]

    if high == low:
        return False

    strength = (close - low) / (high - low)

    return strength >= threshold


def detect_volatility_contraction(data):
    """
    ATR mediu pe ultimele 5 bare < ATR mediu pe bara 6-30 (contracție volatilitate).
    Ferestrele nu se suprapun.
    """
    if "ATR" not in data.columns or len(data) < 30:
        return False

    recent_atr = data["ATR"].tail(5).mean()
    previous_atr = data["ATR"].iloc[-30:-5].mean()

    return recent_atr < previous_atr


def detect_bollinger_squeeze(data):
    """
    BB_WIDTH curent < percentila 25 a ultimelor 60 de bare (squeeze Bollinger).
    """
    if "BB_WIDTH" not in data.columns or len(data) < 60:
        return False

    current_width = data["BB_WIDTH"].iloc[-1]
    historical_width = data["BB_WIDTH"].tail(60).quantile(0.25)

    return current_width < historical_width


def detect_bull_flag(data):
    """
    Bull flag: impuls > 12% în ultimele 15-3 bare, urmat de pullback 1-8% față de High.

    Fix-uri față de versiunea anterioară:
    - impulse_high calculat din High (nu Close) pentru referință corectă
    - fereastră mai largă pentru impulse high (iloc[-15:-3] în loc de [-10:-5])
    - pullback trebuie să fie strict pozitiv (0 < pullback < 0.08)
      → elimină semnale false când prețul continuă să crească
    """
    if len(data) < 25:
        return False

    impulse_start = data["Close"].iloc[-25]
    impulse_high = data["High"].iloc[-15:-3].max()   # High, nu Close; fereastră mai largă
    current_close = data["Close"].iloc[-1]

    if impulse_start == 0:
        return False

    impulse_gain = (impulse_high - impulse_start) / impulse_start
    pullback = (impulse_high - current_close) / impulse_high

    # pullback trebuie pozitiv → prețul a coborât față de vârf, dar nu prea mult
    return impulse_gain > 0.12 and 0 < pullback < 0.08


def calculate_structure_score(data):
    """
    Scor structură 0-20.

    Logică scoring breakout:
    - breakout_50 primește scorul maxim (5 pct)
    - breakout_20 primește scor doar dacă breakout_50 e False (evită dublu-punctaj)
    """
    score = 0

    higher_lows         = detect_higher_lows(data)
    tight_range         = detect_tight_range(data)
    breakout_20         = detect_breakout_20(data)
    breakout_50         = detect_breakout_50(data)
    reclaim_ema20       = detect_reclaim_ema20(data)
    reclaim_ema50       = detect_reclaim_ema50(data)
    close_strong        = detect_close_strength(data)
    volatility_contract = detect_volatility_contraction(data)
    bollinger_squeeze   = detect_bollinger_squeeze(data)
    bull_flag           = detect_bull_flag(data)

    if higher_lows:
        score += 2

    if tight_range:
        score += 3

    # Breakout: scor exclusiv — cel mai puternic câștigă
    if breakout_50:
        score += 5
    elif breakout_20:
        score += 3

    if reclaim_ema20:
        score += 2

    if reclaim_ema50:
        score += 2

    if close_strong:
        score += 2

    if volatility_contract:
        score += 2

    if bollinger_squeeze:
        score += 2

    if bull_flag:
        score += 4

    return min(score, 20)


def analyze_structure(data):
    """
    Returnează dict complet cu toate semnalele și scorul final.
    """
    return {
        "higher_lows":           detect_higher_lows(data),
        "tight_range":           detect_tight_range(data),
        "breakout_20":           detect_breakout_20(data),
        "breakout_50":           detect_breakout_50(data),
        "reclaim_ema20":         detect_reclaim_ema20(data),
        "reclaim_ema50":         detect_reclaim_ema50(data),
        "close_strong":          detect_close_strength(data),
        "volatility_contraction": detect_volatility_contraction(data),
        "bollinger_squeeze":     detect_bollinger_squeeze(data),
        "bull_flag":             detect_bull_flag(data),
        "structure_score":       calculate_structure_score(data),
    }
