from app.repositories.incidents import create_incident, get_incident, list_incidents
from app.repositories.reports import create_report, get_incident_reports, get_report


def existing_streetlight(app):
    incident = create_incident(
        "Streetlight outside Block C is broken", "Electrical", "Block C Entrance"
    )
    create_report(
        "Streetlight outside Block C is broken",
        "Electrical",
        "Block C Entrance",
        incident.id,
    )
    return incident


def report_data():
    return {
        "category": "Electrical",
        "location": "Block C Entrance",
        "description": "Streetlight outside Block C is broken",
    }


def test_strong_candidate_is_shown_before_creating_an_incident(app):
    existing = existing_streetlight(app)

    response = app.test_client().post("/report", data=report_data())

    assert response.status_code == 200
    assert b"Possible existing issue" in response.data
    assert b"Similarity score:</strong> 100%" in response.data
    assert len(list_incidents()) == 1
    assert get_report(2).incident_id is None
    assert get_incident(existing.id) is not None


def test_confirming_candidate_attaches_report_to_existing_incident(app):
    existing = existing_streetlight(app)
    client = app.test_client()
    client.post("/report", data=report_data())

    response = client.post(
        "/report/decision",
        data={"action": "same", "report_id": 2, "incident_id": existing.id},
    )

    assert response.status_code == 200
    assert b"Report received" in response.data
    assert len(list_incidents()) == 1
    assert len(get_incident_reports(existing.id)) == 2


def test_rejecting_candidate_creates_new_incident(app):
    existing = existing_streetlight(app)
    client = app.test_client()
    client.post("/report", data=report_data())

    response = client.post(
        "/report/decision",
        data={"action": "new", "report_id": 2, "incident_id": existing.id},
    )

    assert response.status_code == 200
    assert b"Report received" in response.data
    assert len(list_incidents()) == 2
    assert get_report(2).incident_id != existing.id


def test_report_without_strong_candidate_creates_incident_directly(app):
    create_incident("Broken desk", "Furniture", "Library")

    response = app.test_client().post(
        "/report",
        data={
            "category": "Plumbing",
            "location": "Hostel A",
            "description": "The water tap is leaking",
        },
    )

    assert response.status_code == 200
    assert b"Report received" in response.data
    assert len(list_incidents()) == 2
