# =========================
# DATA SETTINGS
# =========================
DEFAULT_PERIOD = "10y"
DEFAULT_INTERVAL = "1d"
UNIVERSE_FILE = "universe/stocks.txt"

# =========================
# SCORING
# =========================
MIN_SCORE = 70

MAX_GRAPH_SCORE = 65
MAX_STATISTIC_SCORE = 35
MAX_TOTAL_SCORE = 100

MARKET_PENALTY = -10

# =========================
# FILTERS
# =========================
RSI_MIN = 35
RSI_MAX = 65

ATR_PCT_MIN = 1.5
ATR_PCT_MAX = 5.0

MAX_PULLBACK_DAYS = 5
MIN_BREAKOUT_VOLUME_RATIO = 1.5

EMA_RETEST_THRESHOLD = 0.02

# =========================
# RISK MANAGEMENT
# =========================
STOP_LOSS_PERCENT = 0.04
TAKE_PROFIT_PERCENT = 0.08
MAX_HOLD_DAYS = 10

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
EMA_SLOW = 100
EMA_TREND = 200

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

FIBONACCI_LOOKBACK = 60

# =========================
# BENCHMARK
# =========================
BENCHMARK_TICKER = "SPY"

RELATIVE_STRENGTH_DAYS_SHORT = 20
RELATIVE_STRENGTH_DAYS_LONG = 60

# =========================
# REPORTS
# =========================
REPORTS_DIR = "reports"
