
from src.config import MAX_POSITIONS


def select_portfolio(candidates, max_positions=MAX_POSITIONS):
    """
    Alege cele mai bune acțiuni din rezultatele scannerului.
    Sortează descrescător după total_score și păstrează primele max_positions.
    """
    if candidates.empty:
        return candidates

    portfolio = (
        candidates
        .sort_values(by="total_score", ascending=False)
        .head(max_positions)
        .reset_index(drop=True)
    )

    # Rank vizibil pentru Telegram / rapoarte (1-based)
    portfolio.insert(0, "rank", portfolio.index + 1)

    return portfolio
