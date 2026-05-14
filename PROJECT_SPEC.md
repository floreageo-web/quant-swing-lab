# Quant Swing Lab

## Obiectiv

Construim un scanner quant pentru swing trading.

Nu încercăm să ghicim piața.

Căutăm acțiuni cu:
- trend bun
- momentum bun
- compresie
- volum
- structură bună
- risc controlat

## Universe

Lista de acțiuni este în:

universe/stocks.txt

## Timeframe

Folosim daily timeframe.

## Scoring

Scor total: 0-100

Componente:
- Trend: 0-20
- Momentum: 0-20
- Compression: 0-20
- Volume: 0-20
- Structure: 0-20

## Praguri

- 90+ = setup foarte puternic
- 80-90 = setup bun
- sub 80 = ignorăm pentru moment

## Risk Management

Versiunea 1:
- Stop Loss: 6%
- Take Profit: 12%
- Max hold: 15 zile

## Next Steps

- market_regime.py
- portfolio.py
- backtest.py
- Telegram alerts
