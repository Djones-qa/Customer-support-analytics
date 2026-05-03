"""Unit tests for ticket feature engineering."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.feature_engineering import (
    add_resolution_metrics, add_sla_compliance,
    add_temporal_features, add_complexity_features
)


@pytest.fixture
def sample_ticket_df():
    return pd.DataFrame({
        "ticket_id": ["T1","T2","T3","T4","T5"],
        "created_at": pd.to_datetime(["2024-01-15 09:00","2024-01-15 14:00",
            "2024-01-16 22:00","2024-01-17 10:00","2024-01-18 08:30"]),
        "resolved_at": pd.to_datetime(["2024-01-15 11:00","2024-01-16 10:00",
            "2024-01-17 06:00","2024-01-18 18:00", None]),
        "first_response_at": pd.to_datetime(["2024-01-15 09:30","2024-01-15 15:00",
            "2024-01-16 23:00","2024-01-17 10:20","2024-01-18 09:00"]),
        "priority": ["Critical","High","Medium","Low","High"],
        "description": ["Short","A medium length ticket description here",
            "","Very long ticket with lots of detail and context provided by customer",
            "Another ticket"],
        "num_interactions": [2, 5, 1, 8, 3],
        "reopen_count": [0, 1, 0, 2, 0],
        "is_escalated": [False, True, False, True, False],
    })


class TestResolutionMetrics:
    def test_adds_resolution_hours(self, sample_ticket_df):
        result = add_resolution_metrics(sample_ticket_df)
        assert "resolution_hours" in result.columns
        assert result["resolution_hours"].iloc[0] == 2.0

    def test_adds_resolution_days(self, sample_ticket_df):
        result = add_resolution_metrics(sample_ticket_df)
        assert "resolution_days" in result.columns

    def test_adds_is_resolved(self, sample_ticket_df):
        result = add_resolution_metrics(sample_ticket_df)
        assert "is_resolved" in result.columns
        assert result["is_resolved"].iloc[4] == 0

    def test_adds_first_response_hours(self, sample_ticket_df):
        result = add_resolution_metrics(sample_ticket_df)
        assert "first_response_hours" in result.columns
        assert result["first_response_hours"].iloc[0] == 0.5


class TestSLACompliance:
    def test_adds_sla_met(self, sample_ticket_df):
        df = add_resolution_metrics(sample_ticket_df)
        result = add_sla_compliance(df)
        assert "sla_met" in result.columns

    def test_critical_within_4h(self, sample_ticket_df):
        df = add_resolution_metrics(sample_ticket_df)
        result = add_sla_compliance(df)
        assert result["sla_met"].iloc[0] == 1

    def test_adds_breach_hours(self, sample_ticket_df):
        df = add_resolution_metrics(sample_ticket_df)
        result = add_sla_compliance(df)
        assert "sla_breach_hours" in result.columns
        breach = result["sla_breach_hours"].dropna()
        assert (breach >= 0).all()

    def test_first_response_sla(self, sample_ticket_df):
        df = add_resolution_metrics(sample_ticket_df)
        result = add_sla_compliance(df)
        assert "first_response_sla_met" in result.columns


class TestTemporalFeatures:
    def test_adds_hour(self, sample_ticket_df):
        result = add_temporal_features(sample_ticket_df)
        assert "created_hour" in result.columns
        assert result["created_hour"].iloc[0] == 9

    def test_adds_business_hours_flag(self, sample_ticket_df):
        result = add_temporal_features(sample_ticket_df)
        assert "is_business_hours" in result.columns
        assert result["is_business_hours"].iloc[0] == 1
        assert result["is_business_hours"].iloc[2] == 0

    def test_adds_weekend_flag(self, sample_ticket_df):
        result = add_temporal_features(sample_ticket_df)
        assert "is_weekend" in result.columns


class TestComplexityFeatures:
    def test_adds_description_length(self, sample_ticket_df):
        result = add_complexity_features(sample_ticket_df)
        assert "description_length" in result.columns
        assert "description_word_count" in result.columns

    def test_adds_was_reopened(self, sample_ticket_df):
        result = add_complexity_features(sample_ticket_df)
        assert "was_reopened" in result.columns
        assert result["was_reopened"].iloc[0] == 0
        assert result["was_reopened"].iloc[1] == 1
