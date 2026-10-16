import sqlite3
import pandas as pd
from write_methods.get_path import get_dp_path, get_output_dir


def save_pain_to_excel(db_path=None):
    db_path = db_path or get_dp_path()          # resolved at call time, not import time
    OUTPUT_DIR = get_output_dir()
    out_file = OUTPUT_DIR / "pain_reviews.xlsx"

    conn = sqlite3.connect(db_path)
    try:
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'", conn
        )["name"]

        with pd.ExcelWriter(out_file) as writer:
            for table in tables:
                df = pd.read_sql(f'SELECT appId, content, score FROM "{table}" WHERE score <= 2', conn)

                if not df.empty:
                    df.to_excel(
                        writer,
                        sheet_name=table[:31],
                        index=False
                    )

    finally:
        conn.close()

    print(f"All tables from {db_path} saved to '{out_file}'.")
