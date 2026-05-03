"""
agent_performance.py - Agent productivity and quality metrics.
"""

import pandas as pd
import numpy as np


def agent_productivity(df, agent_col="agent_id"):
    """Tickets handled, resolution time, SLA rate per agent."""
    if agent_col not in df.columns:
        return pd.DataFrame()
    agg = {}
    if "ticket_id" in df.columns:
        agg["tickets_handled"] = ("ticket_id", "count")
    if "resolution_hours" in df.columns:
        agg["avg_resolution_hrs"] = ("resolution_hours", "mean")
        agg["median_resolution_hrs"] = ("resolution_hours", "median")
    if "sla_met" in df.columns:
        agg["sla_rate"] = ("sla_met", "mean")
    if "csat_score" in df.columns:
        agg["avg_csat"] = ("csat_score", "mean")
    if "is_escalated" in df.columns:
        agg["escalation_rate"] = ("is_escalated", "mean")
    if not agg:
        return pd.DataFrame()
    result = df.groupby(agent_col).agg(**agg).round(2)
    return result.sort_values("tickets_handled", ascending=False) if "tickets_handled" in result.columns else result


def agent_trend(df, agent_col="agent_id", date_col="created_at", freq="M"):
    """Monthly ticket volume trend per agent."""
    if agent_col not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["period"] = pd.to_datetime(df[date_col]).dt.to_period(freq)
    return df.groupby([agent_col, "period"]).size().unstack(fill_value=0)


def agent_category_matrix(df, agent_col="agent_id", cat_col="category"):
    """Which categories each agent handles most."""
    if agent_col not in df.columns or cat_col not in df.columns:
        return pd.DataFrame()
    return pd.crosstab(df[agent_col], df[cat_col])


def top_performers(df, agent_col="agent_id", metric="sla_rate", n=10):
    """Top N agents by a given metric."""
    perf = agent_productivity(df, agent_col)
    if metric not in perf.columns:
        return pd.DataFrame()
    return perf.nlargest(n, metric)
