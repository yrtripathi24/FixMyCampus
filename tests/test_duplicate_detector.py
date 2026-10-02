from datetime import datetime, timedelta, timezone

from app.models import Incident, Report
from app.services.duplicate_detector import (
    CATEGORY_POINTS,
    LOCATION_POINTS,
    TEXT_POINTS,
    TIME_POINTS,
    calculate_category_score,
    calculate_location_score,
    calculate_similarity,
    calculate_text_score,
    calculate_time_score,
    find_duplicate_candidates,
    normalize_location,
    tokenize,
)


BASE_TIME = datetime(2026, 10, 2, 10, tzinfo=timezone.utc)


def make_incident(incident_id=1, **overrides):
    values = {
        "id": incident_id,
        "title": "Streetlight outside Block C is broken",
        "category": "Electrical",
        "location": "Block C Entrance",
        "status": "OPEN",
        "priority": "MEDIUM",
        "created_at": BASE_TIME.isoformat(),
        "updated_at": BASE_TIME.isoformat(),
    }
    values.update(overrides)
    return Incident(**values)


def make_report(**overrides):
    values = {
        "id": 1,
        "incident_id": None,
        "description": "Streetlight outside Block C is broken",
        "category": "Electrical",
        "location": "Block C Entrance",
        "created_at": (BASE_TIME + timedelta(minutes=30)).isoformat(),
    }
    values.update(overrides)
    return Report(**values)


def test_location_normalization_handles_case_and_whitespace():
    assert normalize_location("  Block   C Entrance ") == "block c entrance"


def test_tokenize_ignores_punctuation_and_common_words():
    assert tokenize("The light, near Block C!") == {"light", "block", "c"}


def test_identical_reports_receive_all_component_points():
    report = make_report()
    incident = make_incident()

    assert calculate_category_score(report, incident) == CATEGORY_POINTS
    assert calculate_location_score(report, incident) == LOCATION_POINTS
    assert calculate_text_score(report, incident) == TEXT_POINTS
    assert calculate_time_score(report, incident) == TIME_POINTS
    assert calculate_similarity(report, incident) == 100


def test_category_and_location_mismatches_receive_no_points():
    report = make_report(category="Plumbing", location="Hostel A")
    incident = make_incident()

    assert calculate_category_score(report, incident) == 0
    assert calculate_location_score(report, incident) == 0


def test_matching_structured_location_ids_receive_full_location_score():
    report = make_report(location_id=7, location="Different legacy text")
    incident = make_incident(location_id=7, location="Another legacy text")

    assert calculate_location_score(report, incident) == LOCATION_POINTS


def test_text_similarity_handles_capitalization_and_punctuation():
    report = make_report(description="STREETLIGHT outside Block C is broken!")
    incident = make_incident()

    assert calculate_text_score(report, incident) == TEXT_POINTS


def test_unrelated_text_has_no_text_score():
    report = make_report(description="The cafeteria refrigerator is leaking")
    incident = make_incident()

    assert calculate_text_score(report, incident) == 0


def test_time_score_boundaries():
    incident = make_incident()
    assert calculate_time_score(make_report(created_at=(BASE_TIME + timedelta(minutes=59)).isoformat()), incident) == 15
    assert calculate_time_score(make_report(created_at=(BASE_TIME + timedelta(hours=1)).isoformat()), incident) == 12
    assert calculate_time_score(make_report(created_at=(BASE_TIME + timedelta(hours=6)).isoformat()), incident) == 8
    assert calculate_time_score(make_report(created_at=(BASE_TIME + timedelta(hours=24)).isoformat()), incident) == 4
    assert calculate_time_score(make_report(created_at=(BASE_TIME + timedelta(hours=72)).isoformat()), incident) == 0


def test_candidates_exclude_closed_incidents_and_rank_by_score_then_id():
    report = make_report()
    best = make_incident(incident_id=2)
    tied = make_incident(incident_id=1)
    closed = make_incident(incident_id=3, status="RESOLVED")

    candidates = find_duplicate_candidates(report, [best, closed, tied])

    assert [candidate.incident.id for candidate in candidates] == [1, 2]
    assert candidates[0].score == candidates[1].score
