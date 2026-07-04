import psycopg2
import subprocess
import os
import pandas as pd
from datetime import datetime

DB_CONFIG = {
    "database": "tpch",
    "user": "postgres",
    "password": "thesis",
    "port": 5432,
}

OUTPUT_FILE = "/mnt/c/tpch/experiment/features/db_stats_features.csv"

def log(msg):
    print(f"[{datetime.now()}] {msg}")

def get_wsl_host():
    try:
        result = subprocess.check_output(
            "ip route | grep default",
            shell=True
        ).decode()
        return result.split()[2]
    except:
        return "localhost"

def get_connection():

    hosts = ["localhost", "127.0.0.1", get_wsl_host()]

    for host in hosts:
        try:
            conn = psycopg2.connect(host=host, **DB_CONFIG)
            log(f"✔ Connected via {host}")
            return conn, host

        except Exception as e:
            log(f"✖ Failed on {host}: {e}")
            continue

    raise Exception("No DB connection")

def get_tables(cursor):
    cursor.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public';
    """)
    return [row[0] for row in cursor.fetchall()]

def get_table_size(cursor, table):
    cursor.execute(f"""
        SELECT pg_total_relation_size('{table}');
    """)
    return cursor.fetchone()[0]

def get_column_cardinality(cursor, table):
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s;
    """, (table,))
    
    columns = [row[0] for row in cursor.fetchall()]

    if not columns:
        return 0

    total_distinct = 0

    for col in columns:
        try:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT {col})
                FROM {table};
            """)
            total_distinct += cursor.fetchone()[0] or 0
        except:
            continue

    return total_distinct / len(columns)  # average cardinality

def get_index_presence(cursor, table):
    cursor.execute("""
        SELECT COUNT(*)
        FROM pg_indexes
        WHERE tablename = %s;
    """, (table,))
    return cursor.fetchone()[0]

def main():

    conn, host = get_connection()
    cursor = conn.cursor()

    tables = get_tables(cursor)

    log(f"Found {len(tables)} tables")

    data = []

    for table in tables:

        try:
            size = get_table_size(cursor, table)
            cardinality = get_column_cardinality(cursor, table)
            indexes = get_index_presence(cursor, table)

            data.append({
                "table": table,
                "table_size_bytes": size,
                "column_cardinality": cardinality,
                "index_presence": indexes
            })

            log(f"Processed {table}")

        except Exception as e:
            log(f"Failed {table}: {e}")

    df = pd.DataFrame(data)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    log(f"Saved DB stats → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()