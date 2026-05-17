import pandas as pd

from src.data_loader import download_universe_data, download_benchmark
from src.indicators import add_indicators
from src.scoring import calculate_total_score
from src.config import MIN_SCORE


def safe_int(value):
    try:
        if pd.isna(value):
            return 0
        return int(value)
    except Exception:
        return 0


def run_scanner(min_score=MIN_SCORE):
    """
    Rulează scannerul principal cu strategia de retest.
    """
    spy_data = download_benchmark()
    if spy_data is not None and not spy_data.empty:
        try:
            spy_data = add_indicators(spy_data)
        except Exception as error:
            print(f"[Scanner] Benchmark indicator error: {error}")
            spy_data = None

    all_data = download_universe_data()
    results  = []

    for ticker, data in all_data.items():
        try:
            data       = add_indicators(data)
            score_data = calculate_total_score(
                data=data,
                spy_data=spy_data,
            )

            if score_data["eliminated"]:
                print(
                    f"[Scanner] Skipping {ticker}: "
                    f"{score_data.get('elimination_reason', 'eliminated')}"
                )
                continue

            if score_data["total_score"] < min_score:
                continue

            latest = data.iloc[-1]

            result = {
                "ticker":             ticker,
                "close":              round(latest["Close"], 2),
                "volume":             safe_int(latest["Volume"]),
                "rsi":                round(latest["RSI"], 1),
                "atr_pct":            round(latest["ATR_PCT"], 2),
                "z_score":            round(score_data["z_score"], 2) if score_data["z_score"] is not None else None,
                "total_score":        score_data["total_score"],
                "graph_score":        score_data["graph_score"],
                "statistic_score":    score_data["statistic_score"],
                "market_penalty":     score_data["market_penalty"],
                "ema_retest_level":   score_data["ema_retest_level"],
                "ema_retest_score":   score_data["ema_retest_score"],
                "rsi_score":          score_data["rsi_score"],
                "volume_dryup_score": score_data["volume_dryup_score"],
                "fibonacci_score":    score_data["fibonacci_score"],
                "candle_score":       score_data["candle_score"],
                "trend_score":        score_data["trend_score"],
                "higher_lows_score":  score_data["higher_lows_score"],
                "zscore_score":       score_data["zscore_score"],
                "rs_score":           score_data["rs_score"],
            }

            results.append(result)

        except Exception as error:
            print(f"[Scanner] Error for {ticker}: {error}")

    results_df = pd.DataFrame(results)

    if not results_df.empty:
        results_df = (
            results_df
            .sort_values(by="total_score", ascending=False)
            .reset_index(drop=True)
        )

    return results_df
