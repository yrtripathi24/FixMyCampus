import pytest

from app.repositories.incidents import create_incident, get_incident
from app.repositories.reports import create_report
from app.services.admin_service import (
    InvalidStatusTransition,
    transition_incident_status,
)


def test_status_transitions_record_timestamps(app):
    incident = create_incident("Broken light", "Electrical", "Block C")

    in_progress = transition_incident_status(incident, "IN_PROGRESS")
    resolved = transition_incident_status(in_progress, "RESOLVED")

    assert resolved.status == "RESOLVED"
    assert resolved.in_progress_at is not None
    assert resolved.resolved_at is not None


def test_status_transitions_only_move_forward(app):
    incident = create_incident("Broken light", "Electrical", "Block C")

    with pytest.raises(InvalidStatusTransition):
        transition_incident_status(incident, "RESOLVED")


def test_admin_dashboard_groups_incidents(app):
    high = create_incident("Water leak", "Plumbing", "Hostel A", priority="HIGH")
    create_report("Leak report one", "Plumbing", "Hostel A", high.id)
    create_report("Leak report two", "Plumbing", "Hostel A", high.id)
    resolved = create_incident("Fixed chair", "Furniture", "Library", status="RESOLVED")

    response = app.test_client().get("/admin/incidents")

    assert response.status_code == 200
    assert b"Water leak" in response.data
    assert b"High priority" in response.data
    assert b"Resolved incidents" in response.data
    assert str(resolved.id).encode() in response.data


def test_admin_route_updates_status(app):
    incident = create_incident("Broken light", "Electrical", "Block C")

    response = app.test_client().post(
        f"/admin/incidents/{incident.id}/status",
        data={"status": "IN_PROGRESS"},
    )

    assert response.status_code == 302
    assert get_incident(incident.id).status == "IN_PROGRESS"
