import numpy as np


def calculate_returns(data):
    """
    Returnează seria de returns zilnice (pct_change).
    Prima valoare e NaN — dropna() înainte de std() unde e necesar.
    """
    return data["Close"].pct_change()


def calculate_z_score(data, window=20):
    """
    Z-score al Close față de media rolling pe `window` bare.
    Returnează None dacă nu sunt suficiente date.
    Pozitiv = supracumpărat, negativ = supravândut.
    """
    if len(data) < window:
        return None

    close = data["Close"]
    rolling_mean = close.rolling(window).mean()
    rolling_std  = close.rolling(window).std()

    latest_close = close.iloc[-1]
    latest_mean  = rolling_mean.iloc[-1]
    latest_std   = rolling_std.iloc[-1]

    if latest_std == 0:
        return 0

    return (latest_close - latest_mean) / latest_std


def detect_mean_reversion_context(z_score):
    """
    Detectează context de mean reversion pe baza z_score pre-calculat.
    Returnează direcția explicită în loc de simplu bool.

    - "overbought"  : z > +2  → potențial short / evită long
    - "oversold"    : z < -2  → potențial revenire bullish
    - None          : z în interval normal, fără semnal de mean reversion
    """
    if z_score is None:
        return None

    if z_score > 2:
        return "overbought"
    if z_score < -2:
        return "oversold"

    return None


def detect_low_volatility_regime(data):
    """
    Detectează regim de volatilitate scăzută.

    Fix: ferestrele nu se suprapun.
    - recent_volatility    : returns din ultimele 10 bare
    - historical_volatility: returns din bara 11-30 (exclusiv ultimele 10)
    """
    returns = calculate_returns(data).dropna()

    if len(returns) < 30:
        return False

    recent_volatility     = returns.tail(10).std()
    historical_volatility = returns.iloc[-30:-10].std()  # fără ultimele 10

    if historical_volatility == 0:
        return False

    return recent_volatility < historical_volatility


def analyze_market_regime(data):
    """
    Returnează dict complet cu z_score, context mean reversion și regim volatilitate.
    z_score e calculat o singură dată și transmis mai departe.
    """
    z_score              = calculate_z_score(data)
    mean_reversion       = detect_mean_reversion_context(z_score)
    low_vol_regime       = detect_low_volatility_regime(data)

    return {
        "z_score":                z_score,
        "mean_reversion_context": mean_reversion,       # "overbought" | "oversold" | None
        "is_mean_reversion":      mean_reversion is not None,
        "low_volatility_regime":  low_vol_regime,
    }
