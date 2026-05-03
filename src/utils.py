"""
utils.py - Shared utilities: config, formatting, diagnostics.
"""

import os
import yaml
import pandas as pd
from pathlib import Path


def get_project_root():
    return Path(__file__).parent.parent


def load_config(config_path=None):
    if config_path is None:
        config_path = get_project_root() / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def format_hours(value):
    if pd.isna(value):
        return "N/A"
    if value < 1:
        return f"{value * 60:.0f}m"
    if value < 24:
        return f"{value:.1f}h"
    return f"{value / 24:.1f}d"


def format_pct(value, decimals=1):
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def dataset_summary(df):
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_pct": round(missing_cells / total_cells * 100, 2) if total_cells else 0,
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 2),
        "duplicates": df.duplicated().sum(),
    }


def print_summary(df, label="Dataset"):
    info = dataset_summary(df)
    sep = "=" * 50
    print(f"\n{sep}")
    print(f"  {label} Summary")
    print(f"{sep}")
    print(f"  Rows:        {info['rows']:,}")
    print(f"  Columns:     {info['columns']}")
    print(f"  Missing:     {info['missing_pct']}%")
    print(f"  Duplicates:  {info['duplicates']:,}")
    print(f"  Memory:      {info['memory_mb']} MB")
    if "created_at" in df.columns:
        dates = pd.to_datetime(df["created_at"])
        print(f"  Date Range:  {dates.min().date()} to {dates.max().date()}")
    if "ticket_id" in df.columns:
        print(f"  Tickets:     {df['ticket_id'].nunique():,}")
    print(f"{sep}\n")


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


def sla_summary(df):
    """Quick SLA compliance summary."""
    result = {}
    if "sla_met" in df.columns:
        result["overall_sla_rate"] = round(df["sla_met"].mean(), 4)
    if "priority" in df.columns and "sla_met" in df.columns:
        result["sla_by_priority"] = df.groupby("priority")["sla_met"].mean().round(4).to_dict()
    if "first_response_sla_met" in df.columns:
        result["first_response_sla_rate"] = round(df["first_response_sla_met"].mean(), 4)
    return result
