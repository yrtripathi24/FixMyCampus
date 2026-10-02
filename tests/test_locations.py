from app.repositories.incidents import get_incident
from app.repositories.locations import list_locations
from app.repositories.reports import get_report


def test_development_locations_are_seeded(app):
    locations = list_locations()

    assert locations
    assert locations[0].campus == "Main Campus"
    assert locations[0].building
    assert locations[0].floor
    assert locations[0].area


def test_report_persists_structured_location_and_detail(app):
    location = list_locations()[0]
    response = app.test_client().post(
        "/report",
        data={
            "category": "Electrical",
            "location_id": str(location.id),
            "location_detail": "Beside the vending machine",
            "description": "The light is not working",
        },
    )

    assert response.status_code == 200
    assert b"Report received" in response.data
    report = get_report(1)
    incident = get_incident(1)
    assert report.location_id == location.id
    assert report.location_detail == "Beside the vending machine"
    assert incident.location_id == location.id
    assert incident.location_detail == "Beside the vending machine"


def test_invalid_structured_location_is_rejected(app):
    response = app.test_client().post(
        "/report",
        data={
            "category": "Electrical",
            "location_id": "999",
            "location_detail": "Somewhere",
            "description": "The light is not working",
        },
    )

    assert response.status_code == 200
    assert b"Choose a valid campus location." in response.data
