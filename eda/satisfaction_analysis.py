"""
satisfaction_analysis.py - CSAT trends and drivers.
"""

import pandas as pd


def csat_summary(df, score_col="csat_score"):
    """Overall CSAT statistics."""
    if score_col not in df.columns:
        return {}
    scores = df[score_col].dropna()
    return {
        "mean": round(scores.mean(), 2),
        "median": round(scores.median(), 2),
        "std": round(scores.std(), 2),
        "satisfied_pct": round((scores >= 4).mean() * 100, 1),
        "dissatisfied_pct": round((scores <= 2).mean() * 100, 1),
        "responses": len(scores),
        "response_rate": round(len(scores) / len(df) * 100, 1),
    }


def csat_by_dimension(df, dimension, score_col="csat_score"):
    """Average CSAT grouped by a dimension (category, channel, agent, etc.)."""
    if dimension not in df.columns or score_col not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(dimension)[score_col]
        .agg(["mean", "median", "count"])
        .round(2)
        .sort_values("mean", ascending=False)
    )


def csat_trend(df, score_col="csat_score", date_col="created_at", freq="M"):
    """Monthly CSAT trend."""
    if score_col not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["period"] = pd.to_datetime(df[date_col]).dt.to_period(freq)
    return df.groupby("period")[score_col].agg(["mean", "count"]).round(2)


def csat_vs_resolution_time(df, score_col="csat_score"):
    """Correlation between resolution time and satisfaction."""
    if score_col not in df.columns or "resolution_hours" not in df.columns:
        return {}
    corr = df[[score_col, "resolution_hours"]].corr().iloc[0, 1]
    bins = [0, 4, 8, 24, 72, float("inf")]
    labels = ["<4h", "4-8h", "8-24h", "24-72h", ">72h"]
    df = df.copy()
    df["res_bucket"] = pd.cut(df["resolution_hours"], bins=bins, labels=labels)
    avg_by_bucket = df.groupby("res_bucket")[score_col].mean().round(2)
    return {"correlation": round(corr, 4), "avg_by_resolution_bucket": avg_by_bucket.to_dict()}
