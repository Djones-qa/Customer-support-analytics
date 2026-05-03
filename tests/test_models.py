"""Unit tests for model evaluation utilities."""
import pytest
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models.evaluate import compute_metrics
from src.utils import format_hours, format_pct, sla_summary
import pandas as pd


@pytest.fixture
def sample_predictions():
    np.random.seed(42)
    y_true = np.random.randint(0, 4, 100)
    y_pred = y_true.copy()
    y_pred[:15] = np.random.randint(0, 4, 15)
    return y_true, y_pred


class TestComputeMetrics:
    def test_returns_all_keys(self, sample_predictions):
        y_true, y_pred = sample_predictions
        metrics = compute_metrics(y_true, y_pred)
        expected = {"accuracy","f1_weighted","f1_macro",
                    "precision_weighted","recall_weighted","n_samples"}
        assert set(metrics.keys()) == expected

    def test_accuracy_range(self, sample_predictions):
        y_true, y_pred = sample_predictions
        metrics = compute_metrics(y_true, y_pred)
        assert 0 <= metrics["accuracy"] <= 1

    def test_perfect_prediction(self):
        labels = np.array([0, 1, 2, 3] * 10)
        metrics = compute_metrics(labels, labels)
        assert metrics["accuracy"] == 1.0
        assert metrics["f1_weighted"] == 1.0

    def test_sample_count(self, sample_predictions):
        y_true, y_pred = sample_predictions
        assert compute_metrics(y_true, y_pred)["n_samples"] == 100


class TestFormatting:
    def test_format_hours_minutes(self):
        assert "m" in format_hours(0.5)

    def test_format_hours_hours(self):
        assert "h" in format_hours(5.0)

    def test_format_hours_days(self):
        assert "d" in format_hours(48.0)

    def test_format_hours_na(self):
        assert format_hours(None) == "N/A"

    def test_format_pct(self):
        assert format_pct(0.952) == "95.2%"

    def test_format_pct_na(self):
        assert format_pct(None) == "N/A"


class TestSLASummary:
    def test_returns_rate(self):
        df = pd.DataFrame({
            "sla_met": [1, 1, 0, 1, 1],
            "priority": ["High","Low","High","Medium","Low"],
            "first_response_sla_met": [1, 1, 1, 0, 1],
        })
        result = sla_summary(df)
        assert "overall_sla_rate" in result
        assert 0 <= result["overall_sla_rate"] <= 1
        assert "sla_by_priority" in result
        assert "first_response_sla_rate" in result
