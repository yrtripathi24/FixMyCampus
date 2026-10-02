from datetime import datetime, timedelta, timezone

from app.services.priority_service import calculate_priority


NOW = datetime(2026, 10, 2, 12, tzinfo=timezone.utc)


def test_water_leak_with_many_reports_is_high_priority():
    result = calculate_priority(8, "Plumbing", NOW - timedelta(hours=9), now=NOW)

    assert result.priority == "HIGH"
    assert result.score == 80
    assert result.report_count_points == 40
    assert result.severity_points == 30
    assert result.age_points == 10


def test_single_damaged_chair_is_low_priority():
    result = calculate_priority(1, "Furniture", NOW - timedelta(hours=2), now=NOW)

    assert result.priority == "LOW"
    assert result.score == 25


def test_priority_boundaries_are_deterministic():
    medium = calculate_priority(2, "Electrical", NOW, now=NOW)
    high = calculate_priority(4, "Electrical", NOW - timedelta(hours=24), now=NOW)

    assert medium.priority == "MEDIUM"
    assert high.priority == "HIGH"
