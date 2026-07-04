import os
import json
import pandas as pd

PLAN_DIR = "/mnt/c/tpch/experiment/runs/plans"
OUTPUT_FILE = "/mnt/c/tpch/experiment/features/plan_features.csv"

def traverse(node, counters):

    if not node:
        return

    counters["total_operations"] += 1

    node_type = node.get("Node Type", "")

    if "Scan" in node_type:
        counters["scan_types"].add(node_type)

    if "Join" in node_type:
        counters["join_types"].add(node_type)

    if "Plans" in node:
        for child in node["Plans"]:
            traverse(child, counters)


def extract_features(plan_json):

    root = plan_json[0]["Plan"]

    counters = {
        "total_operations": 0,
        "scan_types": set(),
        "join_types": set()
    }

    traverse(root, counters)

    return {
        "estimated_rows": root.get("Plan Rows", 0),
        "estimated_cost": root.get("Total Cost", 0),

        "scan_types": len(counters["scan_types"]),
        "join_types": len(counters["join_types"]),

        "total_operations": counters["total_operations"]
    }


def normalize_name(filename):
    return filename.replace(".json", "")


def main():

    data = []

    for file in sorted(os.listdir(PLAN_DIR)):
        if not file.endswith(".json"):
            continue

        path = os.path.join(PLAN_DIR, file)

        try:
            with open(path, "r") as f:
                plan_json = json.load(f)

            features = extract_features(plan_json)
            features["query"] = normalize_name(file)

            data.append(features)

        except Exception as e:
            print("Failed:", file, e)

    df = pd.DataFrame(data)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()