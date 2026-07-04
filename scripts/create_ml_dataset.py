import pandas as pd
import os

FEATURE_FILE = "/mnt/c/tpch/experiment/features/preprocessed_dataset.csv"
RESULTS_FILE = "/mnt/c/tpch/experiment/runs/raw_output/results.csv"

OUTPUT_FILE = "/mnt/c/tpch/experiment/features/ml_dataset.csv"


def normalize(q):
    q = q.replace("base_", "")
    q = q.replace(".sql", "")
    q = q.replace("variant_", "")
    return q.strip().lower()


def main():

    features = pd.read_csv(FEATURE_FILE)
    results = pd.read_csv(RESULTS_FILE)

    print("Features shape:", features.shape)
    print("Results shape:", results.shape)

    features["query"] = features["query"].apply(normalize)
    results["query"] = results["query"].apply(normalize)

    results = results.dropna(subset=["avg"])

    print("After removing failed queries:", results.shape)

    merged = pd.merge(
        features,
        results[["query", "avg"]],
        on="query",
        how="inner"
    )

    print("Final dataset shape:", merged.shape)

    missing_in_features = set(results["query"]) - set(features["query"])
    missing_in_results = set(features["query"]) - set(results["query"])

    print("\nMissing in features:", len(missing_in_features))
    print("Missing in results:", len(missing_in_results))

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    merged.to_csv(OUTPUT_FILE, index=False)

    print("\n✔ Saved ML dataset →", OUTPUT_FILE)


if __name__ == "__main__":
    main()