"""
feature_engineering.py - Resolution time, SLA, agent, and temporal features.
"""

import pandas as pd
import numpy as np


def add_resolution_metrics(df, created_col="created_at", resolved_col="resolved_at"):
    """Calculate resolution time and first response time."""
    df = df.copy()
    if created_col in df.columns and resolved_col in df.columns:
        created = pd.to_datetime(df[created_col])
        resolved = pd.to_datetime(df[resolved_col])
        delta = resolved - created
        df["resolution_hours"] = (delta.dt.total_seconds() / 3600).round(2)
        df["resolution_days"] = (df["resolution_hours"] / 24).round(2)
        df["is_resolved"] = df[resolved_col].notna().astype(int)
    if "first_response_at" in df.columns and created_col in df.columns:
        first = pd.to_datetime(df["first_response_at"])
        created = pd.to_datetime(df[created_col])
        df["first_response_hours"] = ((first - created).dt.total_seconds() / 3600).round(2)
    return df


def add_sla_compliance(df, sla_config=None):
    """Check SLA compliance based on priority and resolution time."""
    df = df.copy()
    if sla_config is None:
        sla_config = {"Critical": 4, "High": 8, "Medium": 24, "Low": 72}
    if "priority" in df.columns and "resolution_hours" in df.columns:
        df["sla_target_hours"] = df["priority"].map(sla_config)
        df["sla_met"] = (df["resolution_hours"] <= df["sla_target_hours"]).astype(int)
        df["sla_breach_hours"] = np.maximum(df["resolution_hours"] - df["sla_target_hours"], 0).round(2)
    if "first_response_hours" in df.columns:
        df["first_response_sla_met"] = (df["first_response_hours"] <= 1).astype(int)
    return df


def add_temporal_features(df, date_col="created_at"):
    """Extract time components from ticket creation date."""
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    df["created_year"] = dt.dt.year
    df["created_month"] = dt.dt.month
    df["created_day_of_week"] = dt.dt.dayofweek
    df["created_hour"] = dt.dt.hour
    df["created_quarter"] = dt.dt.quarter
    df["is_weekend"] = dt.dt.dayofweek.ge(5).astype(int)
    df["is_business_hours"] = (
        (dt.dt.hour >= 9) & (dt.dt.hour < 17)
        & (dt.dt.dayofweek < 5)
    ).astype(int)
    df["day_name"] = dt.dt.day_name()
    return df


def add_agent_metrics(df, agent_col="agent_id"):
    """Calculate per-agent performance metrics."""
    df = df.copy()
    if agent_col not in df.columns:
        return df
    agent_stats = df.groupby(agent_col).agg(
        agent_total_tickets=("ticket_id", "count") if "ticket_id" in df.columns else (agent_col, "count"),
        agent_avg_resolution=("resolution_hours", "mean") if "resolution_hours" in df.columns else (agent_col, "count"),
        agent_sla_rate=("sla_met", "mean") if "sla_met" in df.columns else (agent_col, "count"),
    ).round(2)
    df = df.merge(agent_stats, on=agent_col, how="left")
    return df


def add_customer_features(df):
    """Add customer-level aggregation features."""
    df = df.copy()
    if "customer_id" not in df.columns:
        return df
    cust_stats = df.groupby("customer_id").agg(
        customer_ticket_count=("ticket_id", "count") if "ticket_id" in df.columns else ("customer_id", "count"),
        customer_escalation_rate=("is_escalated", "mean") if "is_escalated" in df.columns else ("customer_id", "count"),
    ).round(3)
    df = df.merge(cust_stats, on="customer_id", how="left")
    df["is_repeat_customer"] = (df.get("customer_ticket_count", 0) > 1).astype(int)
    return df


def add_complexity_features(df):
    """Estimate ticket complexity from available fields."""
    df = df.copy()
    if "description" in df.columns:
        df["description_length"] = df["description"].fillna("").str.len()
        df["description_word_count"] = df["description"].fillna("").str.split().str.len()
    if "num_interactions" in df.columns:
        df["is_complex"] = (df["num_interactions"] > df["num_interactions"].median()).astype(int)
    if "reopen_count" in df.columns:
        df["was_reopened"] = (df["reopen_count"] > 0).astype(int)
    if "is_escalated" in df.columns:
        df["is_escalated"] = df["is_escalated"].astype(int)
    return df


def run_feature_pipeline(df):
    """Execute full feature engineering pipeline."""
    print("Starting feature engineering...")
    initial = len(df.columns)
    df = add_resolution_metrics(df)
    df = add_sla_compliance(df)
    df = add_temporal_features(df)
    df = add_agent_metrics(df)
    df = add_customer_features(df)
    df = add_complexity_features(df)
    new_cols = len(df.columns) - initial
    print(f"  Added {new_cols} features ({initial} -> {len(df.columns)} total)")
    print("Feature engineering complete.")
    return df
