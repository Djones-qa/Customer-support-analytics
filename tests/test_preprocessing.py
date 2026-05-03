"""Unit tests for ticket preprocessing."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.preprocessing import (
    parse_datetime_columns, normalize_priority, normalize_status,
    normalize_categories, remove_duplicate_tickets
)


class TestDatetimeParsing:
    def test_parses_valid_dates(self):
        df = pd.DataFrame({"created_at": ["2024-01-15 10:30:00", "2024-02-20 14:00:00"]})
        result = parse_datetime_columns(df, ["created_at"])
        assert pd.api.types.is_datetime64_any_dtype(result["created_at"])

    def test_handles_bad_dates(self):
        df = pd.DataFrame({"created_at": ["2024-01-15", "not-a-date"]})
        result = parse_datetime_columns(df, ["created_at"])
        assert result["created_at"].isna().sum() == 1

    def test_skips_missing_columns(self):
        df = pd.DataFrame({"other_col": [1, 2]})
        result = parse_datetime_columns(df, ["created_at"])
        assert "created_at" not in result.columns


class TestNormalizePriority:
    def test_maps_critical(self):
        df = pd.DataFrame({"priority": ["urgent", "CRITICAL", "p1"]})
        result = normalize_priority(df)
        assert (result["priority"] == "Critical").all()

    def test_maps_high(self):
        df = pd.DataFrame({"priority": ["high", "P2"]})
        result = normalize_priority(df)
        assert (result["priority"] == "High").all()

    def test_defaults_to_medium(self):
        df = pd.DataFrame({"priority": ["unknown", "weird"]})
        result = normalize_priority(df)
        assert (result["priority"] == "Medium").all()


class TestNormalizeStatus:
    def test_maps_resolved(self):
        df = pd.DataFrame({"status": ["solved", "fixed", "resolved"]})
        result = normalize_status(df)
        assert (result["status"] == "Resolved").all()

    def test_maps_open(self):
        df = pd.DataFrame({"status": ["new", "open"]})
        result = normalize_status(df)
        assert (result["status"] == "Open").all()


class TestNormalizeCategories:
    def test_title_cases(self):
        df = pd.DataFrame({"category": ["billing", "TECHNICAL SUPPORT"]})
        result = normalize_categories(df)
        assert result["category"].iloc[0] == "Billing"
        assert result["category"].iloc[1] == "Technical Support"

    def test_maps_invalid_to_other(self):
        df = pd.DataFrame({"category": ["Billing", "xyz123"]})
        result = normalize_categories(df, valid_categories=["Billing"])
        assert result["category"].iloc[1] == "Other"


class TestDuplicateRemoval:
    def test_removes_dupes(self):
        df = pd.DataFrame({"ticket_id": ["T1", "T1", "T2"], "val": [1, 2, 3]})
        result = remove_duplicate_tickets(df)
        assert len(result) == 2

    def test_keeps_last(self):
        df = pd.DataFrame({"ticket_id": ["T1", "T1"], "val": [1, 2]})
        result = remove_duplicate_tickets(df)
        assert result["val"].iloc[0] == 2
