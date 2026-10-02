from app.repositories.incidents import create_incident
from app.repositories.reports import create_report


def test_incident_dashboard_lists_report_counts(app):
    incident = create_incident("Broken light", "Electrical", "Block C")
    create_report("Light is broken", "Electrical", "Block C", incident.id)
    response = app.test_client().get("/incidents")

    assert response.status_code == 200
    assert b"Broken light" in response.data
    assert b"Reports:</strong> 1" in response.data


def test_incident_dashboard_filters_by_category_and_status(app):
    create_incident("Broken light", "Electrical", "Block C")
    create_incident("Leaking tap", "Plumbing", "Hostel A", status="RESOLVED")

    response = app.test_client().get("/incidents?category=Plumbing&status=RESOLVED")

    assert b"Leaking tap" in response.data
    assert b"Broken light" not in response.data


def test_incident_detail_shows_all_reports(app):
    incident = create_incident("Damaged desk", "Furniture", "Library")
    create_report("Desk has a broken leg", "Furniture", "Library", incident.id)
    create_report("The desk is unsafe to use", "Furniture", "Library", incident.id)

    response = app.test_client().get(f"/incidents/{incident.id}")

    assert response.status_code == 200
    assert b"Desk has a broken leg" in response.data
    assert b"The desk is unsafe to use" in response.data
    assert b"Reports:</strong> 2" in response.data


def test_missing_incident_returns_not_found(app):
    response = app.test_client().get("/incidents/999")

    assert response.status_code == 404
