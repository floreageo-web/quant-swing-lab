# Quant Swing Lab

Scanner Python pentru swing trading pe acțiuni NASDAQ/NYSE.

## Ce face

- Citește lista de acțiuni din `universe/stocks.txt`
- Descarcă date din Yahoo Finance
- Calculează indicatori tehnici: EMA, RSI, ROC, ATR, Bollinger Width
- Detectează structuri de preț: breakout, bull flag, higher lows, tight range
- Calculează scor 0–100 pe 5 componente
- Analizează z-score și context de mean reversion
- Selectează un portofoliu final
- Salvează rapoarte CSV în `reports/`

## Structura proiectului

```text
quant-swing-lab/
├── main.py                  # Scanner principal
├── main_backtest.py         # Backtest pe date istorice
├── requirements.txt         # Biblioteci necesare
├── PROJECT_SPEC.md          # Specificația sistemului
├── README.md                # Documentație proiect
├── universe/
│   └── stocks.txt           # Lista de ticker-e
├── reports/                 # Rapoarte generate automat
├── data/
│   ├── raw/
│   └── processed/
└── src/
    ├── __init__.py
    ├── config.py            # Setări globale
    ├── data_loader.py       # Download date Yahoo Finance
    ├── indicators.py        # EMA, RSI, ROC, ATR, Bollinger, Relative Volume
    ├── structure.py         # Detectare structuri de preț
    ├── scoring.py           # Scor total 0-100
    ├── market_regime.py     # Z-score, mean reversion, regim volatilitate
    ├── scanner.py           # Logică scanner principal
    ├── portfolio.py         # Selecție portofoliu final
    ├── backtest.py          # Simulare trade-uri istorice
    └── metrics.py           # Metrici backtest
