"""
plots.py - 8 professional customer support visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

OUTPUT_DIR = "visualizations/output"


def _save(fig, name, output_dir=None):
    out = output_dir or OUTPUT_DIR
    Path(out).mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{out}/{name}", dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved: {out}/{name}")
    plt.close(fig)


def plot_ticket_volume_trend(df, date_col="created_at", output_dir=None):
    df = df.copy()
    df["week"] = pd.to_datetime(df[date_col]).dt.to_period("W").dt.to_timestamp()
    weekly = df.groupby("week").size()
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.fill_between(weekly.index, weekly.values, alpha=0.3, color="#2196F3")
    ax.plot(weekly.index, weekly.values, color="#2196F3", linewidth=2)
    ax.set_title("Weekly Ticket Volume", fontweight="bold", fontsize=14)
    ax.set_ylabel("Tickets")
    ax.grid(alpha=0.3)
    _save(fig, "01_ticket_volume.png", output_dir)


def plot_category_breakdown(df, cat_col="category", output_dir=None):
    if cat_col not in df.columns:
        return
    counts = df[cat_col].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    axes[0].pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
    axes[0].set_title("By Category", fontweight="bold")
    axes[1].barh(counts.index[::-1], counts.values[::-1], color="#4CAF50", edgecolor="white")
    axes[1].set_title("Ticket Counts", fontweight="bold")
    plt.tight_layout()
    _save(fig, "02_category_breakdown.png", output_dir)


def plot_resolution_time_distribution(df, output_dir=None):
    if "resolution_hours" not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    data = df["resolution_hours"].dropna()
    data = data[data <= data.quantile(0.95)]
    ax.hist(data, bins=50, color="#FF9800", edgecolor="white", alpha=0.8)
    ax.axvline(data.median(), color="red", linestyle="--", linewidth=2,
               label=f"Median: {data.median():.1f}h")
    ax.set_title("Resolution Time Distribution", fontweight="bold", fontsize=14)
    ax.set_xlabel("Hours")
    ax.set_ylabel("Tickets")
    ax.legend()
    _save(fig, "03_resolution_distribution.png", output_dir)


def plot_sla_compliance(df, output_dir=None):
    if "sla_met" not in df.columns or "priority" not in df.columns:
        return
    order = ["Critical", "High", "Medium", "Low"]
    sla = df.groupby("priority")["sla_met"].mean().reindex(order) * 100
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#F44336" if v < 80 else "#FF9800" if v < 95 else "#4CAF50" for v in sla.values]
    ax.bar(sla.index, sla.values, color=colors, edgecolor="white")
    ax.axhline(95, color="green", linestyle="--", alpha=0.7, label="95% Target")
    ax.axhline(80, color="red", linestyle="--", alpha=0.5, label="80% Warning")
    for i, v in enumerate(sla.values):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontweight="bold")
    ax.set_title("SLA Compliance by Priority", fontweight="bold", fontsize=14)
    ax.set_ylabel("Compliance (%)")
    ax.set_ylim(0, 110)
    ax.legend()
    _save(fig, "04_sla_compliance.png", output_dir)


def plot_channel_comparison(df, output_dir=None):
    if "channel" not in df.columns:
        return
    metrics = {}
    if "resolution_hours" in df.columns:
        metrics["Avg Resolution (h)"] = df.groupby("channel")["resolution_hours"].mean()
    if "csat_score" in df.columns:
        metrics["Avg CSAT"] = df.groupby("channel")["csat_score"].mean()
    if not metrics:
        return
    fig, axes = plt.subplots(1, len(metrics), figsize=(7 * len(metrics), 6))
    if len(metrics) == 1:
        axes = [axes]
    for ax, (title, data) in zip(axes, metrics.items()):
        data.sort_values().plot(kind="barh", ax=ax, color="#9C27B0", edgecolor="white")
        ax.set_title(title, fontweight="bold")
    plt.tight_layout()
    _save(fig, "05_channel_comparison.png", output_dir)


def plot_agent_performance(df, agent_col="agent_id", output_dir=None):
    if agent_col not in df.columns or "resolution_hours" not in df.columns:
        return
    top = df.groupby(agent_col).agg(
        tickets=("ticket_id", "count") if "ticket_id" in df.columns else (agent_col, "count"),
        avg_hrs=("resolution_hours", "mean"),
    ).nlargest(15, "tickets")
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(top.index[::-1].astype(str), top["avg_hrs"][::-1], color="#1976D2", edgecolor="white")
    ax.set_title("Top 15 Agents - Avg Resolution Time", fontweight="bold", fontsize=14)
    ax.set_xlabel("Avg Resolution Hours")
    _save(fig, "06_agent_performance.png", output_dir)


def plot_hourly_heatmap(df, date_col="created_at", output_dir=None):
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    df["hour"] = dt.dt.hour
    df["dow"] = dt.dt.dayofweek
    pivot = df.groupby(["dow", "hour"]).size().unstack(fill_value=0)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    pivot.index = [days[i] if i < len(days) else str(i) for i in pivot.index]
    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax, linewidths=0.5,
                cbar_kws={"label": "Tickets"})
    ax.set_title("Ticket Volume by Hour and Day", fontweight="bold", fontsize=14)
    ax.set_xlabel("Hour of Day")
    _save(fig, "07_hourly_heatmap.png", output_dir)


def plot_csat_trend(df, score_col="csat_score", date_col="created_at", output_dir=None):
    if score_col not in df.columns:
        return
    df = df.copy()
    df["month"] = pd.to_datetime(df[date_col]).dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("month")[score_col].mean()
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly.index, monthly.values, color="#4CAF50", linewidth=2, marker="o", markersize=5)
    ax.axhline(monthly.values.mean(), color="gray", linestyle="--", alpha=0.5,
               label=f"Avg: {monthly.values.mean():.2f}")
    ax.set_title("Monthly CSAT Trend", fontweight="bold", fontsize=14)
    ax.set_ylabel("Avg CSAT Score")
    ax.set_ylim(1, 5.2)
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, "08_csat_trend.png", output_dir)


def generate_all_plots(df, output_dir=None):
    out = output_dir or OUTPUT_DIR
    print(f"Generating all plots to {out}/...")
    plot_ticket_volume_trend(df, output_dir=out)
    plot_category_breakdown(df, output_dir=out)
    plot_resolution_time_distribution(df, output_dir=out)
    plot_sla_compliance(df, output_dir=out)
    plot_channel_comparison(df, output_dir=out)
    plot_agent_performance(df, output_dir=out)
    plot_hourly_heatmap(df, output_dir=out)
    plot_csat_trend(df, output_dir=out)
    print("All 8 plots generated.")
