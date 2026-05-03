"""
dashboard.py - Interactive Plotly support dashboards exported as HTML.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def create_support_dashboard(df):
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=("Tickets by Category", "Priority Distribution",
                        "Resolution Time", "CSAT Distribution"),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "histogram"}, {"type": "histogram"}]])
    if "category" in df.columns:
        cats = df["category"].value_counts()
        fig.add_trace(go.Pie(labels=cats.index, values=cats.values), row=1, col=1)
    if "priority" in df.columns:
        order = ["Critical","High","Medium","Low"]
        pri = df["priority"].value_counts().reindex(order).fillna(0)
        colors = ["#F44336","#FF9800","#2196F3","#4CAF50"]
        fig.add_trace(go.Bar(x=pri.index, y=pri.values,
            marker_color=colors, name="Priority"), row=1, col=2)
    if "resolution_hours" in df.columns:
        data = df["resolution_hours"].dropna()
        data = data[data <= data.quantile(0.95)]
        fig.add_trace(go.Histogram(x=data, nbinsx=40,
            marker_color="#FF9800", name="Resolution"), row=2, col=1)
    if "csat_score" in df.columns:
        fig.add_trace(go.Histogram(x=df["csat_score"].dropna(),
            nbinsx=5, marker_color="#4CAF50", name="CSAT"), row=2, col=2)
    fig.update_layout(title="Support Overview Dashboard",
        height=700, showlegend=False, template="plotly_white")
    return fig


def create_sla_dashboard(df):
    if "sla_met" not in df.columns:
        return None
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("SLA by Priority", "SLA Trend"))
    if "priority" in df.columns:
        order = ["Critical","High","Medium","Low"]
        sla = (df.groupby("priority")["sla_met"].mean() * 100).reindex(order)
        colors = ["#F44336" if v < 80 else "#FF9800" if v < 95 else "#4CAF50"
                  for v in sla.values]
        fig.add_trace(go.Bar(x=sla.index, y=sla.values,
            marker_color=colors, name="SLA %"), row=1, col=1)
    if "created_at" in df.columns:
        df2 = df.copy()
        df2["month"] = pd.to_datetime(df2["created_at"]).dt.to_period("M").dt.to_timestamp()
        trend = df2.groupby("month")["sla_met"].mean() * 100
        fig.add_trace(go.Scatter(x=trend.index, y=trend.values,
            mode="lines+markers", line=dict(color="#1976D2", width=2),
            name="SLA Trend"), row=1, col=2)
    fig.update_layout(title="SLA Compliance Dashboard",
        height=450, showlegend=False, template="plotly_white")
    return fig


def export_dashboards(df, output_dir="visualizations/output"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    print("Generating interactive dashboards...")
    fig1 = create_support_dashboard(df)
    fig1.write_html(str(out / "dashboard_support.html"))
    print(f"  Saved: {out}/dashboard_support.html")
    fig2 = create_sla_dashboard(df)
    if fig2:
        fig2.write_html(str(out / "dashboard_sla.html"))
        print(f"  Saved: {out}/dashboard_sla.html")
    print("Dashboards complete.")
