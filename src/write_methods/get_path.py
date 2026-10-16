
from pathlib import Path


def get_dp_path():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]   # see note below
    DB_DIR = PROJECT_ROOT / "database"
    DB_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DB_DIR / "market_intelligence.db"

    return DB_PATH

def get_output_dir():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]   # see note below
    OUTPUT_DIR = PROJECT_ROOT / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    return OUTPUT_DIR