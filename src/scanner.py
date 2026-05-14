import pandas as pd

from src.data_loader import download_universe_data
from src.indicators import add_indicators
from src.scoring import calculate_total_score
from src.market_regime import analyze_market_regime
from src.config import MIN_SCORE


def run_scanner(min_score=MIN_SCORE):
    """
    Rulează scannerul principal.
    Returnează DataFrame sortat descrescător după total_score,
    filtrând doar acțiunile cu scor >= min_score.
    """
    all_data = download_universe_data()
    results = []

    for ticker, data in all_data.items():
        try:
            # Indicatori
            data = add_indicators(data)

            # Scoring
            score_data = calculate_total_score(data)

            # Market Regime
            regime_data = analyze_market_regime(data)

            latest = data.iloc[-1]

            result = {
                "ticker":            ticker,
                "close":             round(latest["Close"], 2),
                "volume":            int(latest["Volume"]),
                "rsi":               round(latest["RSI"], 1) if "RSI" in data.columns else None,
                "total_score":       score_data["total_score"],
                "trend_score":       score_data["trend_score"],
                "momentum_score":    score_data["momentum_score"],
                "compression_score": score_data["compression_score"],
                "volume_score":      score_data["volume_score"],
                "structure_score":   score_data["structure_score"],
                "z_score":           round(regime_data["z_score"], 2) if regime_data["z_score"] is not None else None,
                "mean_reversion":    regime_data["mean_reversion_context"],
                "low_volatility":    regime_data["low_volatility_regime"],
            }

            if result["total_score"] >= min_score:
                results.append(result)

        except Exception as error:
            print(f"[Scanner] Error for {ticker}: {error}")

    results_df = pd.DataFrame(results)

    if not results_df.empty:
        results_df = results_df.sort_values(
            by="total_score",
            ascending=False
        ).reset_index(drop=True)

    return results_df
