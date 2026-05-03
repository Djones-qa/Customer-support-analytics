"""
exploratory_analysis.py - Automated EDA for support ticket data.
"""

import pandas as pd
import numpy as np


def ticket_volume_summary(df, date_col="created_at"):
    """Daily, weekly, monthly ticket volume."""
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    return {
        "daily_avg": round(df.groupby(dt.dt.date).size().mean(), 1),
        "weekly_avg": round(df.groupby(dt.dt.isocalendar().week).size().mean(), 1),
        "monthly_avg": round(df.groupby(dt.dt.to_period("M")).size().mean(), 1),
        "peak_day": df.groupby(dt.dt.date).size().idxmax(),
        "peak_volume": int(df.groupby(dt.dt.date).size().max()),
    }


def category_breakdown(df, cat_col="category"):
    """Ticket count and percentage by category."""
    if cat_col not in df.columns:
        return pd.DataFrame()
    counts = df[cat_col].value_counts()
    pct = (counts / len(df) * 100).round(1)
    result = pd.DataFrame({"count": counts, "pct": pct})
    if "resolution_hours" in df.columns:
        result["avg_resolution_hrs"] = df.groupby(cat_col)["resolution_hours"].mean().round(1)
    if "sla_met" in df.columns:
        result["sla_rate"] = (df.groupby(cat_col)["sla_met"].mean() * 100).round(1)
    return result


def priority_distribution(df, pri_col="priority"):
    """Ticket distribution by priority level."""
    if pri_col not in df.columns:
        return pd.DataFrame()
    order = ["Critical", "High", "Medium", "Low"]
    counts = df[pri_col].value_counts().reindex(order).fillna(0).astype(int)
    pct = (counts / len(df) * 100).round(1)
    return pd.DataFrame({"count": counts, "pct": pct})


def channel_analysis(df, chan_col="channel"):
    """Performance metrics by support channel."""
    if chan_col not in df.columns:
        return pd.DataFrame()
    agg = {"ticket_id": "count"} if "ticket_id" in df.columns else {chan_col: "count"}
    if "resolution_hours" in df.columns:
        agg["resolution_hours"] = "mean"
    if "csat_score" in df.columns:
        agg["csat_score"] = "mean"
    if "sla_met" in df.columns:
        agg["sla_met"] = "mean"
    return df.groupby(chan_col).agg(agg).round(2)


def resolution_time_stats(df):
    """Resolution time distribution statistics."""
    if "resolution_hours" not in df.columns:
        return {}
    r = df["resolution_hours"].dropna()
    return {
        "mean": round(r.mean(), 2),
        "median": round(r.median(), 2),
        "p90": round(r.quantile(0.9), 2),
        "p95": round(r.quantile(0.95), 2),
        "std": round(r.std(), 2),
        "min": round(r.min(), 2),
        "max": round(r.max(), 2),
    }


def escalation_analysis(df):
    """Escalation rate and patterns."""
    if "is_escalated" not in df.columns:
        return {}
    esc = df["is_escalated"].astype(int)
    result = {"escalation_rate": round(esc.mean(), 4), "total_escalated": int(esc.sum())}
    if "category" in df.columns:
        result["by_category"] = df.groupby("category")["is_escalated"].mean().round(4).to_dict()
    if "priority" in df.columns:
        result["by_priority"] = df.groupby("priority")["is_escalated"].mean().round(4).to_dict()
    return result


def run_full_eda(df):
    print("\n=== Ticket Volume ===")
    for k, v in ticket_volume_summary(df).items():
        print(f"  {k}: {v}")
    print("\n=== Category Breakdown ===")
    print(category_breakdown(df).to_string())
    print("\n=== Priority Distribution ===")
    print(priority_distribution(df).to_string())
    print("\n=== Channel Analysis ===")
    ca = channel_analysis(df)
    if not ca.empty:
        print(ca.to_string())
    print("\n=== Resolution Time ===")
    for k, v in resolution_time_stats(df).items():
        print(f"  {k}: {v}h")
    print("\n=== Escalation Analysis ===")
    ea = escalation_analysis(df)
    for k, v in ea.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")
    print("\nEDA complete.")
