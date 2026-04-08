from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MONITORING_DIR = DATA_DIR / "monitoring"

DEFAULT_PROCESSED_CSV = PROCESSED_DIR / "games_processed.csv"
DEFAULT_PROCESSED_PARQUET = PROCESSED_DIR / "games_processed.parquet"
DEFAULT_MONITOR_CANDIDATES = PROCESSED_DIR / "monitor_candidates.csv"
DEFAULT_CCU_HISTORY = MONITORING_DIR / "ccu_snapshots.csv"


def ensure_directories() -> None:
    for path in (DATA_DIR, RAW_DIR, PROCESSED_DIR, MONITORING_DIR):
        path.mkdir(parents=True, exist_ok=True)
