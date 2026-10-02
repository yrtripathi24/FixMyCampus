from app.repositories.incidents import create_incident, get_incident
from app.repositories.reports import create_report
from app.services.report_service import refresh_incident_priority


def test_attaching_reports_refreshes_incident_priority(app):
    incident = create_incident("Water leak", "Plumbing", "Hostel A")
    for _ in range(8):
        create_report("Water leak is getting worse", "Plumbing", "Hostel A", incident.id)

    refreshed = refresh_incident_priority(incident.id)

    assert refreshed.priority == "HIGH"
    assert get_incident(incident.id).priority == "HIGH"
