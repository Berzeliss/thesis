import pandas as pd
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATASET_PATH = "/mnt/c/tpch/experiment/features/ml_dataset.csv"
LOG_PATH = "/mnt/c/tpch/experiment/logs/random_forest_log.txt"

def write_log(message):
    """
    Prints message to terminal and writes it to log file.
    """
    print(message)

    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def train_random_forest():

    os.makedirs("../experiment/logs", exist_ok=True)


    write_log("\n====================================")
    write_log("Random Forest Training Run")
    write_log(
        "Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    write_log("====================================\n")

    write_log("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    write_log(
        f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    df = df.drop(columns=["query"])

    X = df.drop(columns=["avg_execution_time"])
    y = df["avg_execution_time"]


    write_log(
        f"Number of features: {X.shape[1]}"
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    write_log("\nDataset split:")
    write_log(
        f"Training samples: {len(X_train)}"
    )
    write_log(
        f"Testing samples: {len(X_test)}"
    )

    write_log("\nCreating Random Forest model...")

    model = RandomForestRegressor(
        random_state=42
    )

    write_log("Training model...")

    model.fit(
        X_train,
        y_train
    )

    write_log("Model training completed.")

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions,
    )
    rmse = mse ** 0.5

    write_log("\n===== BASELINE MODEL RESULTS =====")
    write_log(
        f"MAE:  {mae:.4f}"
    )
    write_log(
        f"RMSE: {rmse:.4f}"
    )

    write_log("\nRun completed successfully.")
    write_log("====================================\n")

if __name__ == "__main__":
    train_random_forest()