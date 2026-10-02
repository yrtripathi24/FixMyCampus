import re
from dataclasses import dataclass
from datetime import datetime, timezone


CATEGORY_POINTS = 30
LOCATION_POINTS = 30
TEXT_POINTS = 25
TIME_POINTS = 15

TIME_WINDOWS = (
    (1, 15),
    (6, 12),
    (24, 8),
    (72, 4),
)

STOP_WORDS = {"a", "an", "and", "is", "near", "of", "the", "to"}


@dataclass(frozen=True)
class DuplicateCandidate:
    incident: object
    score: int


def normalize_location(location):
    return " ".join(location.strip().casefold().split())


def tokenize(text):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.casefold())
        if token not in STOP_WORDS
    }


def calculate_category_score(report, incident):
    return CATEGORY_POINTS if report.category.casefold() == incident.category.casefold() else 0


def calculate_location_score(report, incident):
    return LOCATION_POINTS if normalize_location(report.location) == normalize_location(incident.location) else 0


def calculate_text_score(report, incident):
    report_tokens = tokenize(report.description)
    incident_tokens = tokenize(incident.title)
    if not report_tokens or not incident_tokens:
        return 0
    similarity = len(report_tokens & incident_tokens) / len(report_tokens | incident_tokens)
    return round(similarity * TEXT_POINTS)


def _parse_timestamp(value):
    if isinstance(value, datetime):
        timestamp = value
    else:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp


def calculate_time_score(report, incident):
    hours = abs(
        (_parse_timestamp(report.created_at) - _parse_timestamp(incident.created_at)).total_seconds()
    ) / 3600
    for max_hours, points in TIME_WINDOWS:
        if hours < max_hours:
            return points
    return 0


def calculate_similarity(report, incident):
    return (
        calculate_category_score(report, incident)
        + calculate_location_score(report, incident)
        + calculate_text_score(report, incident)
        + calculate_time_score(report, incident)
    )


def find_duplicate_candidates(report, incidents):
    candidates = [
        DuplicateCandidate(incident, calculate_similarity(report, incident))
        for incident in incidents
        if incident.status == "OPEN"
    ]
    return sorted(candidates, key=lambda candidate: (-candidate.score, candidate.incident.id))
