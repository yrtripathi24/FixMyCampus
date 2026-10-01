from app.repositories.incidents import create_incident, get_incident
from app.repositories.reports import (
    attach_report_to_incident,
    create_report,
    get_incident_reports,
)


def test_create_and_retrieve_incident(app):
    incident = create_incident("Broken streetlight", "Electrical", "Block C")

    stored = get_incident(incident.id)

    assert stored == incident
    assert stored.status == "OPEN"
    assert stored.priority == "MEDIUM"


def test_create_attach_and_retrieve_reports(app):
    incident = create_incident("Leaking tap", "Plumbing", "Hostel A")
    first = create_report("Tap is leaking", "Plumbing", "Hostel A")
    second = create_report("Water pooling below the tap", "Plumbing", "Hostel A")

    assert first.incident_id is None
    assert attach_report_to_incident(first.id, incident.id)
    assert attach_report_to_incident(second.id, incident.id)
    reports = get_incident_reports(incident.id)

    assert [report.id for report in reports] == [first.id, second.id]
    assert all(report.incident_id == incident.id for report in reports)
