"""
data_loader.py - Load ticket data, validate schema, save outputs.
"""

import os
import pandas as pd
import yaml


def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_raw_data(file_name, config=None, file_type="csv"):
    if config is None:
        config = load_config()
    file_path = os.path.join(config["data"]["raw_dir"], file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    date_cols = [config["data"]["date_column"]]
    if file_type == "csv":
        df = pd.read_csv(file_path, parse_dates=date_cols)
    elif file_type == "json":
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported: {file_type}")
    print(f"Loaded {len(df):,} rows x {len(df.columns)} columns from {file_path}")
    return df


def validate_schema(df, config=None):
    if config is None:
        config = load_config()
    required = [config["data"]["ticket_id_column"], config["data"]["date_column"]]
    missing = [c for c in required if c not in df.columns]
    result = {"valid": len(missing) == 0, "missing": missing, "columns": sorted(df.columns.tolist())}
    if missing:
        print(f"WARNING: Missing columns: {missing}")
    else:
        print("Schema validation passed.")
    return result


def save_processed(df, file_name, config=None):
    if config is None:
        config = load_config()
    out_dir = config["data"]["processed_dir"]
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, file_name)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df):,} rows to {out_path}")
