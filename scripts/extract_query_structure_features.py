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


def extract_tables(sql):
    """
    Extract tables from FROM clauses.
    Handles TPC-H style:
    FROM CUSTOMER, ORDERS, LINEITEM
    """

    tables = []

    from_sections = re.findall(
        r"\bFROM\b(.*?)(?=\bWHERE\b|\bGROUP BY\b|\bORDER BY\b|\bHAVING\b|$)",
        sql,
        flags=re.DOTALL
    )

    for section in from_sections:

        section = re.sub(r"\bJOIN\b", ",", section)

        candidates = section.split(",")

        for table in candidates:

            table = re.sub(
                r"\s+(AS\s+)?[A-Z_][A-Z0-9_]*\s*$",
                "",
                table.strip()
            )

            table = table.strip()

            if table:
                tables.append(table)

    return tables

def extract_joins(sql):
    """
    Count TPC-H style joins.

    Examples:
    C_CUSTKEY = O_CUSTKEY
    L_ORDERKEY = O_ORDERKEY

    These are joins because both sides are column names.
    """

    conditions = re.findall(
        r"\b([A-Z]+_[A-Z0-9]+)\s*=\s*([A-Z]+_[A-Z0-9]+)\b",
        sql
    )

    joins = 0

    for left, right in conditions:
        if left != right:
            joins += 1

    return joins

def extract_aggregates(sql):
    """
    Counts aggregate functions only.
    Example:
    SUM(price * quantity)

    counts as 1.
    """

    count = 0

    for func in AGG_FUNCTIONS:
        count += len(
            re.findall(
                rf"\b{func}\s*\(",
                sql
            )
        )

    return count


def extract_features(sql):

    tables = extract_tables(sql)

    num_tables = len(tables)

    num_joins = extract_joins(sql)

    num_aggs = extract_aggregates(sql)

    where_count = len(re.findall(r"\bWHERE\b", sql))

    and_count = len(re.findall(r"\bAND\b", sql))

    or_count = len(re.findall(r"\bOR\b", sql))

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

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("✔ Query structure features saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()