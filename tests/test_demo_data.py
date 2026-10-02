from app.repositories.incidents import list_incidents
from app.repositories.reports import get_incident_reports
from app.services.demo_data_service import seed_demo_data


def test_demo_data_creates_realistic_incidents_and_duplicates(app):
    assert seed_demo_data() == 5

    incidents = list_incidents()
    streetlight = next(
        incident for incident in incidents if "streetlight" in incident.title
    )
    reports = get_incident_reports(streetlight.id)

    assert len(incidents) == 5
    assert len(reports) == 3
    assert seed_demo_data() == 0
    assert len(list_incidents()) == 5
