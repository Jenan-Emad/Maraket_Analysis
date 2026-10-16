import sqlite3
from write_methods.get_path import get_dp_path


def warehouse_database_operations(df, table_name="apps_user_feedback"):
 
    #create the new tables
    DB_PATH = get_dp_path()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        # clean the table name to avoid any error occur
        table_name = table_name.replace(".", "_").lower()

        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit()
    finally:
        conn.close()
    print(f"Exported {len(df)} rows to '{table_name}' in {DB_PATH.resolve()}")


def drop_all_old_tables(db_path=get_dp_path()):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
            print(f"Dropped table: {table[0]}")
        conn.commit()
    finally:
        conn.close()
