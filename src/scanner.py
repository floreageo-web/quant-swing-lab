import pandas as pd

from src.data_loader import download_universe_data
from src.indicators import add_indicators
from src.scoring import calculate_total_score


def run_scanner(min_score=60):
    """
    Scanează toate acțiunile din universe/stocks.txt.
    Returnează doar acțiunile cu scor total >= min_score.

    Scor maxim teoretic: 100 (5 componente × 20).
    Prag recomandat: 60-70 pentru rezultate practice.
    """
    all_data = download_universe_data()
    results = []

    for ticker, data in all_data.items():
        try:
            data = add_indicators(data)
            score_data = calculate_total_score(data)
            latest = data.iloc[-1]

            result = {
                "ticker":             ticker,
                "close":              round(latest["Close"], 2),
                "volume":             int(latest["Volume"]),
                "rsi":                round(latest["RSI"], 1) if "RSI" in data.columns else None,
                "ema20":              round(latest["EMA20"], 2) if "EMA20" in data.columns else None,
                "total_score":        score_data["total_score"],
                "trend_score":        score_data["trend_score"],
                "momentum_score":     score_data["momentum_score"],
                "compression_score":  score_data["compression_score"],
                "volume_score":       score_data["volume_score"],
                "structure_score":    score_data["structure_score"],
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
