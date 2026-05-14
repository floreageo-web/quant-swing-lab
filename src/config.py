# =========================
# DATA SETTINGS
# =========================

DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"

UNIVERSE_FILE = "universe/stocks.txt"

# =========================
# SCORING
# =========================

MIN_SCORE = 80

MAX_TOTAL_SCORE = 100

# =========================
# RISK MANAGEMENT
# =========================

STOP_LOSS_PERCENT = 0.06
TAKE_PROFIT_PERCENT = 0.12

MAX_HOLD_DAYS = 15

# =========================
# PORTFOLIO
# =========================

MAX_POSITIONS = 10
IDEAL_POSITIONS = 5

MAX_POSITIONS_PER_SECTOR = 2

# =========================
# INDICATORS
# =========================

EMA_FAST = 20
EMA_MEDIUM = 50
EMA_SLOW = 200

RSI_WINDOW = 14
ROC_WINDOW = 12

ATR_WINDOW = 14

BOLLINGER_WINDOW = 20
BOLLINGER_STD = 2

# =========================
# STRUCTURE
# =========================

TIGHT_RANGE_THRESHOLD = 0.06

BREAKOUT_LOOKBACK_20 = 20
BREAKOUT_LOOKBACK_50 = 50

# =========================
# REPORTS
# =========================

SIGNALS_REPORT_FILE = (
    "reports/latest_signals.csv"
)
