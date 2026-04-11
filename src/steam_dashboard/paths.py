from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MONITORING_DIR = DATA_DIR / "monitoring"
ACADEMIC_DIR = DATA_DIR / "academic"
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_PDF_DIR = OUTPUT_DIR / "pdf"

DEFAULT_PROCESSED_CSV = PROCESSED_DIR / "games_processed.csv"
DEFAULT_PROCESSED_PARQUET = PROCESSED_DIR / "games_processed.parquet"
DEFAULT_MONITOR_CANDIDATES = PROCESSED_DIR / "monitor_candidates.csv"
DEFAULT_CCU_HISTORY = MONITORING_DIR / "ccu_snapshots.csv"
DEFAULT_ACADEMIC_DAILY_SALES = ACADEMIC_DIR / "daily_sales_month.csv"
DEFAULT_ACADEMIC_CUSTOMER_PROFILE = ACADEMIC_DIR / "customer_genre_profile_week.csv"
DEFAULT_ACADEMIC_STORE_ACCESS = ACADEMIC_DIR / "store_access_shift_week.csv"


def ensure_directories() -> None:
    for path in (DATA_DIR, RAW_DIR, PROCESSED_DIR, MONITORING_DIR, ACADEMIC_DIR, OUTPUT_DIR, OUTPUT_PDF_DIR):
        path.mkdir(parents=True, exist_ok=True)
