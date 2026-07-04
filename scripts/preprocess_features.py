import pandas as pd
import os
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

INPUT_FILE = "/mnt/c/tpch/experiment/features/merged_feature_dataset.csv"
OUTPUT_FILE = "/mnt/c/tpch/experiment/features/preprocessed_dataset.csv"


def main():

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded dataset: {df.shape}")

    query_ids = df["query"].copy()

    categorical_features = [
        "scan_types",
        "join_types"
    ]

    numerical_features = [
        "tables",
        "joins",
        "aggregates",
        "predicates",
        "query_length",
        "estimated_rows",
        "estimated_cost",
        "total_operations",
        "table_size",
        "column_cardinality",
        "index_presence"
    ]

    df[categorical_features] = df[categorical_features].fillna("none")
    df[numerical_features] = df[numerical_features].fillna(0)

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", StandardScaler(), numerical_features)
        ]
    )

    X = preprocessor.fit_transform(df)

    feature_names = preprocessor.get_feature_names_out()

    if hasattr(X, "toarray"):
        X = X.toarray()

    X_df = pd.DataFrame(X, columns=feature_names)

    X_df.insert(0, "query", query_ids.values)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    X_df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved preprocessed dataset → {OUTPUT_FILE}")
    print(f"Final shape: {X_df.shape}")
    print("Sample columns:", list(X_df.columns[:5]))


if __name__ == "__main__":
    main()