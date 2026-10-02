from app.repositories.incidents import get_incident
from app.repositories.reports import get_incident_reports


def test_valid_report_creates_incident_and_report(app):
    response = app.test_client().post(
        "/report",
        data={
            "category": "Electrical",
            "location": "Block C Entrance",
            "description": "Streetlight outside Block C is not working.",
        },
    )

    assert response.status_code == 200
    assert b"Report received" in response.data
    incident = get_incident(1)
    reports = get_incident_reports(incident.id)
    assert incident.title == "Streetlight outside Block C is not working"
    assert len(reports) == 1
    assert reports[0].incident_id == incident.id


def test_missing_description_shows_validation_message(app):
    response = app.test_client().post(
        "/report",
        data={"category": "Electrical", "location": "Block C", "description": ""},
    )

    assert response.status_code == 200
    assert b"Description is required." in response.data


def test_missing_location_shows_validation_message(app):
    response = app.test_client().post(
        "/report",
        data={"category": "Electrical", "location": "", "description": "Broken light"},
    )

    assert response.status_code == 200
    assert b"Location is required." in response.data


def test_invalid_category_shows_validation_message(app):
    response = app.test_client().post(
        "/report",
        data={"category": "Roads", "location": "Block C", "description": "Broken light"},
    )

    assert response.status_code == 200
    assert b"Choose a valid category." in response.data
