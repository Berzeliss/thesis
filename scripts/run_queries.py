import psycopg2
import time
import csv
import os
import subprocess
import json
from datetime import datetime

DB_CONFIG = {
    "database": "tpch",
    "user": "postgres",
    "password": "thesis",
    "port": 5432,
}

BASE_PATH = "queries/base"
VARIANT_PATH = "queries/variants"

OUTPUT_FILE = "experiment/runs/raw_output/results.csv"
PLANS_DIR = "experiment/runs/plans"
LOG_FILE = "experiment/logs/runtime_log.txt"

RUNS_PER_QUERY = 3
QUERY_TIMEOUT_MS = 1200000  # 20 minutes


def log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)


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

            cursor = conn.cursor()

            # FIX: proper PostgreSQL timeout syntax
            cursor.execute(f"SET statement_timeout = {QUERY_TIMEOUT_MS}")

            return conn, host
        except Exception as e:
            log(f"✖ Failed on {host}: {e}")
            continue

    raise Exception("No DB connection")


def run_query(cursor, query):
    start = time.time()

    # ensure timeout applies every run
    cursor.execute(f"SET statement_timeout = {QUERY_TIMEOUT_MS}")

    cursor.execute(query)
    cursor.fetchall()

    return time.time() - start


def get_plan(cursor, query):
    try:
        cursor.execute(f"SET statement_timeout = {QUERY_TIMEOUT_MS}")
        cursor.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + query)
        return cursor.fetchall()[0][0]
    except Exception as e:
        return {"error": str(e)}


def load_queries():
    queries = []

    for f in sorted(os.listdir(BASE_PATH)):
        if f.endswith(".sql"):
            with open(os.path.join(BASE_PATH, f), "r") as file:
                queries.append((f"base_{f}", file.read()))

    for f in sorted(os.listdir(VARIANT_PATH)):
        if f.endswith(".sql"):
            with open(os.path.join(VARIANT_PATH, f), "r") as file:
                queries.append((f"variant_{f}", file.read()))

    return queries


def main():
    conn, host = get_connection()
    cursor = conn.cursor()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(PLANS_DIR, exist_ok=True)

    queries = load_queries()
    results = []

    log("\n=== Starting experiments ===\n")

    for name, query in queries:

        log(f"\n START QUERY: {name}")
        query_start = datetime.now()

        times = []

        for i in range(RUNS_PER_QUERY):
            try:
                conn.rollback()

                log(f"  ▶ run {i+1} started")
                t_start = time.time()

                t = run_query(cursor, query)

                log(f"  ✔ run {i+1} finished in {t:.4f}s")
                times.append(t)

            except Exception as e:
                log(f"  ✖ run {i+1} failed: {e}")
                times.append(None)

        valid = [t for t in times if t is not None]
        avg = sum(valid) / len(valid) if valid else None

        results.append([name] + times + [avg])

        try:
            conn.rollback()
            log(f" generating plan for {name}")

            plan = get_plan(cursor, query)

            plan_file = os.path.join(
                PLANS_DIR,
                name.replace(".sql", ".json")
            )

            with open(plan_file, "w") as f:
                json.dump(plan, f, indent=2)

            log(f"  ✔ plan saved: {plan_file}")

        except Exception as e:
            log(f"  ✖ plan failed: {e}")

        log(f"🏁 END QUERY: {name} | started {query_start} | ended {datetime.now()}\n")

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "run1", "run2", "run3", "avg"])
        writer.writerows(results)

    log("\n✔ Saved CSV: " + OUTPUT_FILE)
    log("✔ Saved plans: " + PLANS_DIR)


if __name__ == "__main__":
    main()