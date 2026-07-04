import os
import pandas as pd
import re

DB_STATS_FILE = "/mnt/c/tpch/experiment/features/db_stats_features.csv"
Q_STRUCT_FILE = "/mnt/c/tpch/experiment/features/query_structure_features.csv"
PLAN_FILE = "/mnt/c/tpch/experiment/features/plan_features.csv"

OUTPUT_FILE = "/mnt/c/tpch/experiment/features/merged_feature_dataset.csv"

def normalize(name: str):
    name = name.replace(".sql", "")
    name = name.replace(".json", "")
    name = name.replace("base_", "")
    name = name.replace("variant_", "")
    return name.strip().lower()

def extract_tables(sql):
    sql = sql.lower()
    from_tables = re.findall(r"from\s+([a-zA-Z0-9_]+)", sql)
    join_tables = re.findall(r"join\s+([a-zA-Z0-9_]+)", sql)
    return list(set(from_tables + join_tables))

def load_db_stats():
    df = pd.read_csv(DB_STATS_FILE)

    stats = {}
    for _, r in df.iterrows():
        stats[r["table"].lower()] = {
            "size": r["table_size_bytes"],
            "cardinality": r["column_cardinality"],
            "indexes": r["index_presence"]
        }

    return stats

def aggregate_stats(tables, stats):

    sizes, cards, idx = [], [], []

    for t in tables:
        if t in stats:
            sizes.append(stats[t]["size"])
            cards.append(stats[t]["cardinality"])
            idx.append(stats[t]["indexes"])

    if not tables or not sizes:
        return 0, 0, 0

    return (
        sum(sizes),
        sum(cards) / len(cards),
        sum(idx)
    )

def main():

    q_struct = pd.read_csv(Q_STRUCT_FILE)
    plans = pd.read_csv(PLAN_FILE)

    # normalize keys
    q_struct["query"] = q_struct["query"].apply(normalize)
    plans["query"] = plans["query"].apply(normalize)

    db_stats = load_db_stats()

    merged = []

    missing_plan = 0
    missing_sql = 0

    for _, row in q_struct.iterrows():

        qid = row["query"]

        plan_row = plans[plans["query"] == qid]

        if plan_row.empty:
            missing_plan += 1
            continue

        plan_row = plan_row.iloc[0]

        # find SQL file (safe fallback search)
        sql_path = None

        for root, _, files in os.walk("/mnt/c/tpch/queries"):
            for f in files:
                if normalize(f) == qid:
                    sql_path = os.path.join(root, f)
                    break

        if not sql_path:
            missing_sql += 1
            continue

        sql = open(sql_path, "r").read()
        tables = extract_tables(sql)

        table_size, card, idx = aggregate_stats(tables, db_stats)

        merged.append({
            # query structure
            "query": qid,
            "tables": row["tables"],
            "joins": row["joins"],
            "aggregates": row["aggregates"],
            "predicates": row["predicates"],
            "query_length": row["query_length"],

            # plan features
            "estimated_rows": plan_row["estimated_rows"],
            "estimated_cost": plan_row["estimated_cost"],
            "scan_types": plan_row["scan_types"],
            "join_types": plan_row["join_types"],
            "total_operations": plan_row["total_operations"],

            # db stats
            "table_size": table_size,
            "column_cardinality": card,
            "index_presence": idx
        })

    df = pd.DataFrame(merged)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n✔ Saved:", OUTPUT_FILE)
    print("✔ Rows:", len(df))
    print("⚠ Missing plan matches:", missing_plan)
    print("⚠ Missing SQL matches:", missing_sql)


if __name__ == "__main__":
    main()