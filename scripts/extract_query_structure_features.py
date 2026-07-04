import os
import re
import pandas as pd

BASE_PATH = "/mnt/c/tpch/queries/base"
VARIANT_PATH = "/mnt/c/tpch/queries/variants"

OUTPUT_FILE = "/mnt/c/tpch/experiment/features/query_structure_features.csv"

AGG_FUNCTIONS = ["COUNT", "SUM", "AVG", "MIN", "MAX"]


def read_sql(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().upper()


def extract_features(sql):

    from_count = len(re.findall(r"\bFROM\b", sql))
    join_count_tables = len(re.findall(r"\bJOIN\b", sql))
    num_tables = from_count + join_count_tables

    num_joins = join_count_tables

    num_aggs = sum(sql.count(func) for func in AGG_FUNCTIONS)

    where_count = sql.count("WHERE")
    and_count = sql.count(" AND ")
    or_count = sql.count(" OR ")
    num_predicates = where_count + and_count + or_count

    query_length = len(sql)

    return {
        "tables": num_tables,
        "joins": num_joins,
        "aggregates": num_aggs,
        "predicates": num_predicates,
        "query_length": query_length
    }


def normalize_name(filename):
    """
    base_q1.sql -> q1
    variant_q1_v2.sql -> q1_v2
    """
    name = filename.replace(".sql", "")
    name = name.replace("base_", "")
    name = name.replace("variant_", "")
    return name


def process_folder(folder):
    data = []

    for file in sorted(os.listdir(folder)):
        if not file.endswith(".sql"):
            continue

        path = os.path.join(folder, file)
        sql = read_sql(path)

        features = extract_features(sql)
        features["query"] = normalize_name(file)

        data.append(features)

    return data


def main():

    base_data = process_folder(BASE_PATH)
    variant_data = process_folder(VARIANT_PATH)

    all_data = base_data + variant_data

    df = pd.DataFrame(all_data)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("✔ Query structure features saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()