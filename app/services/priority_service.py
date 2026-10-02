from dataclasses import dataclass
from datetime import datetime, timezone


REPORT_COUNT_POINTS = (
    (8, 40),
    (4, 25),
    (2, 15),
    (1, 5),
)
CATEGORY_SEVERITY_POINTS = {
    "Electrical": 35,
    "Plumbing": 30,
    "Infrastructure": 25,
    "Cleanliness": 15,
    "Furniture": 10,
    "Other": 5,
}
AGE_POINTS = (
    (1, 0),
    (24, 10),
    (72, 20),
)
HIGH_PRIORITY_SCORE = 70
MEDIUM_PRIORITY_SCORE = 40


@dataclass(frozen=True)
class PriorityResult:
    priority: str
    score: int
    report_count_points: int
    severity_points: int
    age_points: int


def _parse_timestamp(value):
    if isinstance(value, datetime):
        timestamp = value
    else:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp


def _report_count_points(report_count):
    for minimum, points in REPORT_COUNT_POINTS:
        if report_count >= minimum:
            return points
    return 0


def _age_points(created_at, now):
    hours = max(0, (now - created_at).total_seconds() / 3600)
    for max_hours, points in AGE_POINTS:
        if hours < max_hours:
            return points
    return 30


def calculate_priority(report_count, category, created_at, now=None):
    now = _parse_timestamp(now or datetime.now(timezone.utc))
    created_at = _parse_timestamp(created_at)
    report_count_points = _report_count_points(report_count)
    severity_points = CATEGORY_SEVERITY_POINTS.get(category, 5)
    age_points = _age_points(created_at, now)
    score = report_count_points + severity_points + age_points

    if score >= HIGH_PRIORITY_SCORE:
        priority = "HIGH"
    elif score >= MEDIUM_PRIORITY_SCORE:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return PriorityResult(
        priority,
        score,
        report_count_points,
        severity_points,
        age_points,
    )
