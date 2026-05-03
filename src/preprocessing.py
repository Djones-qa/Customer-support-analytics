"""
preprocessing.py - Ticket data cleaning, datetime parsing, status normalization.
"""

import pandas as pd
import numpy as np


def parse_datetime_columns(df, columns=None):
    """Convert datetime string columns to proper datetime type."""
    df = df.copy()
    if columns is None:
        columns = ["created_at", "resolved_at", "first_response_at"]
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            nulls = df[col].isna().sum()
            if nulls > 0:
                print(f"  {col}: {nulls} unparseable dates set to NaT")
    return df


def normalize_categories(df, col="category", valid_categories=None):
    """Standardize category labels."""
    df = df.copy()
    if col not in df.columns:
        return df
    df[col] = df[col].str.strip().str.title()
    if valid_categories:
        invalid = ~df[col].isin(valid_categories)
        count = invalid.sum()
        if count > 0:
            df.loc[invalid, col] = "Other"
            print(f"  {col}: mapped {count} invalid values to 'Other'")
    return df


def normalize_priority(df, col="priority"):
    """Standardize priority labels."""
    df = df.copy()
    if col not in df.columns:
        return df
    mapping = {
        "critical": "Critical", "urgent": "Critical", "p1": "Critical",
        "high": "High", "p2": "High",
        "medium": "Medium", "normal": "Medium", "p3": "Medium",
        "low": "Low", "p4": "Low",
    }
    df[col] = df[col].str.strip().str.lower().map(mapping).fillna("Medium")
    return df


def normalize_status(df, col="status"):
    """Standardize ticket status labels."""
    df = df.copy()
    if col not in df.columns:
        return df
    mapping = {
        "open": "Open", "new": "Open",
        "in progress": "In Progress", "working": "In Progress", "assigned": "In Progress",
        "pending": "Pending Customer", "waiting": "Pending Customer",
        "escalated": "Escalated",
        "resolved": "Resolved", "solved": "Resolved", "fixed": "Resolved",
        "closed": "Closed",
    }
    df[col] = df[col].str.strip().str.lower().map(mapping).fillna("Open")
    return df


def remove_duplicate_tickets(df, id_col="ticket_id"):
    """Remove duplicate ticket entries."""
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates(subset=[id_col], keep="last")
    removed = before - len(df)
    if removed > 0:
        print(f"  Removed {removed} duplicate tickets")
    return df


def run_preprocessing_pipeline(df):
    """Execute full ticket preprocessing pipeline."""
    print("Starting support ticket preprocessing...")
    print(f"  Input: {len(df):,} tickets")
    df = parse_datetime_columns(df)
    df = normalize_categories(df)
    df = normalize_priority(df)
    df = normalize_status(df)
    df = remove_duplicate_tickets(df)
    print(f"  Output: {len(df):,} tickets")
    print("Preprocessing complete.")
    return df
