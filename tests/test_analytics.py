from app.repositories.incidents import create_incident
from app.repositories.reports import create_report
from app.services.admin_service import transition_incident_status


def test_analytics_dashboard_reports_summary_and_breakdowns(app):
    electrical = create_incident(
        "Broken light", "Electrical", "Engineering Block C - Main Entrance"
    )
    create_report("Light report", "Electrical", "Engineering Block C", electrical.id)
    plumbing = create_incident("Water leak", "Plumbing", "Hostel A - Common Area")
    create_report("Leak report", "Plumbing", "Hostel A", plumbing.id)
    in_progress = transition_incident_status(plumbing, "IN_PROGRESS")
    transition_incident_status(in_progress, "RESOLVED")

    response = app.test_client().get("/analytics")

    assert response.status_code == 200
    assert b"Open incidents" in response.data
    assert b"Resolved incidents" in response.data
    assert b"Electrical" in response.data
    assert b"Plumbing" in response.data
    assert b"Average resolution time" in response.data


def test_empty_analytics_dashboard_is_supported(app):
    response = app.test_client().get("/analytics")

    assert response.status_code == 200
    assert b"No category data yet." in response.data
    assert b"No building data yet." in response.data
