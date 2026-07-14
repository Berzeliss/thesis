import pandas as pd
import os

DATASET_PATH = "C:/tpch/experiment/features/ml_dataset.csv"

def verify_dataset():
    print("Loading dataset...\n")

    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)

    print("===== DATASET OVERVIEW =====")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}\n")

    print("===== COLUMN NAMES =====")
    for column in df.columns:
        print(column)

    print("\n===== DATA TYPES =====")
    print(df.dtypes)

    print("\n===== MISSING VALUES =====")
    missing_values = df.isnull().sum()

    if missing_values.sum() == 0:
        print("No missing values found.")
    else:
        print(missing_values[missing_values > 0])

    print("\n===== DUPLICATE ROWS =====")
    duplicates = df.duplicated().sum()
    print(f"Duplicate rows: {duplicates}")

    print("\n===== FIRST 5 ROWS =====")
    print(df.head())

    print("\n===== BASIC STATISTICS =====")
    print(df.describe())


if __name__ == "__main__":
    verify_dataset()