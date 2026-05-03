# Customer Support Analytics

**Ticket analysis, resolution trends, SLA compliance, and agent performance analytics.**

[![CI](https://github.com/Djones-qa/Customer-support-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Djones-qa/Customer-support-analytics/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Project Overview

End-to-end customer support analytics pipeline that processes ticket data, tracks SLA compliance, measures agent performance, analyzes customer satisfaction drivers, and classifies ticket priority using ML. Designed for portfolio demonstration of operational analytics, classification modeling, and business intelligence skills.

### Key Objectives

- **Ticket Volume Analysis** - Daily, weekly, monthly volume trends and peak detection
- **Resolution Time Tracking** - Distribution, percentiles, and category-level benchmarks
- **SLA Compliance** - Priority-based SLA targets with breach detection and trending
- **Agent Performance** - Productivity, resolution speed, CSAT, and escalation rates
- **Customer Satisfaction** - CSAT trends, drivers, and correlation with resolution time
- **Priority Classification** - ML classifiers (LR, RF, GB, XGBoost) for auto-prioritization
- **Channel Comparison** - Email, Chat, Phone, Web Form, Social Media performance
- **Escalation Pattern Detection** - Rate analysis by category, priority, and agent
- **8 Professional Visualizations** - Charts, heatmaps, and interactive Plotly dashboards

---

## Repository Structure

    Customer-support-analytics/
    .github/workflows/ci.yml
    config/config.yaml
    data/
        raw/                        Original ticket exports
        processed/                  Cleaned, feature-engineered data
        external/                   Holiday calendars, product catalogs
        README.md
    eda/
        exploratory_analysis.py     Volume, category, priority, resolution stats
        agent_performance.py        Agent productivity and quality metrics
        satisfaction_analysis.py    CSAT trends, drivers, correlations
    models/
        train.py                    4-model priority classifier comparison
        predict.py                  Single and batch ticket classification
        evaluate.py                 Metrics, confusion matrix, error analysis
        saved_models/
    notebooks/
        01_data_exploration.ipynb
        02_preprocessing_features.ipynb
        03_model_training.ipynb
        04_visualization.ipynb
    sql/
        create_tables.sql           tickets, agent_metrics, sla_tracking
        ticket_queries.sql          Volume, category, priority, aging
        sla_queries.sql             Compliance by priority, trend, breaches
        agent_queries.sql           Leaderboard, trend, CSAT, escalations
    src/
        __init__.py
        data_loader.py
        preprocessing.py            DateTime parsing, normalization, dedup
        feature_engineering.py      Resolution, SLA, temporal, agent features
        utils.py                    Formatting, diagnostics, SLA summary
    tests/
        test_preprocessing.py       14 data cleaning tests
        test_features.py            14 feature engineering tests
        test_models.py              10 evaluation and utility tests
    visualizations/
        plots.py                    8 matplotlib/seaborn charts
        dashboard.py                Interactive Plotly dashboards
        output/
    .gitignore
    requirements.txt
    README.md

---

## Analytics Pipeline

    Raw Tickets -> Validate -> Clean -> Normalize -> Feature Engineer -> Analyze -> Classify -> Visualize

### Preprocessing (src/preprocessing.py)
- DateTime parsing with error handling
- Category, priority, and status normalization
- Duplicate ticket removal (keep latest)

### Feature Engineering (src/feature_engineering.py)
- Resolution time (hours, days) and first response time
- SLA compliance flags with breach hour calculation
- Temporal: hour, day of week, business hours, weekend flags
- Agent-level aggregations (volume, avg resolution, SLA rate)
- Customer features (ticket count, repeat flag, escalation rate)
- Complexity: description length, word count, reopen flag

### ML Classifiers (models/train.py)

| Model | Approach |
|---|---|
| Logistic Regression | Linear baseline |
| Random Forest | 200-tree ensemble |
| Gradient Boosting | 200 sequential estimators |
| XGBoost | Gradient boosting with regularization |

All models use StratifiedKFold (5-fold) cross-validation.

---

## Visualizations

### Static Plots (8 charts)
1. Weekly ticket volume trend
2. Category breakdown (pie + bar)
3. Resolution time distribution
4. SLA compliance by priority
5. Channel comparison
6. Top agent performance
7. Ticket volume heatmap (hour x day)
8. Monthly CSAT trend

### Interactive Dashboards (Plotly HTML)
- Support overview (category, priority, resolution, CSAT)
- SLA compliance (by priority + monthly trend)

---

## Quick Start

    git clone https://github.com/Djones-qa/Customer-support-analytics.git
    cd Customer-support-analytics
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pytest tests/ -v --cov=src

Place your CSV in data/raw/ then run notebooks 01 through 04.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Analysis | pandas, NumPy, SciPy |
| ML | scikit-learn, XGBoost, LightGBM |
| Database | SQLite, SQLAlchemy |
| Visualization | matplotlib, seaborn, Plotly |
| Testing | pytest, pytest-cov |
| CI/CD | GitHub Actions |

---

## Key Metrics (Template)

After running the pipeline, document findings here:

- **Avg Resolution Time**: Typical range 8-24 hours depending on priority
- **SLA Compliance**: Target 95%+ for Critical/High, 90%+ for Medium/Low
- **CSAT Score**: Industry benchmark 4.0+ out of 5.0
- **First Response**: Target under 1 hour for all priorities
- **Escalation Rate**: Healthy teams stay under 10%

---

## Author

**Darrius Jones**
QA Automation Specialist | Backend Engineering | Support Operations Analytics
