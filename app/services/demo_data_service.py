from app.repositories.incidents import create_incident, list_incidents
from app.repositories.locations import list_locations
from app.repositories.reports import create_report
from app.services.report_service import refresh_incident_priority


DEMO_INCIDENTS = (
    {
        "title": "Broken streetlight - Block C entrance",
        "category": "Electrical",
        "building": "Engineering Block C",
        "area": "Main Entrance",
        "reports": (
            "Streetlight outside Block C isn't working.",
            "Light near the C block entrance is broken.",
            "It's completely dark near the Block C entrance.",
        ),
    },
    {
        "title": "Leaking tap - Hostel A common area",
        "category": "Plumbing",
        "building": "Hostel A",
        "area": "Common Area",
        "reports": ("The tap is leaking continuously.",),
    },
    {
        "title": "Broken classroom projector - Block C hostel gate",
        "category": "Infrastructure",
        "building": "Engineering Block C",
        "area": "Hostel Gate",
        "reports": ("The classroom projector will not turn on.",),
    },
    {
        "title": "Overflowing waste bin - Cafeteria",
        "category": "Cleanliness",
        "building": "Cafeteria",
        "area": "Dining Area",
        "reports": ("The waste bin near the dining area is overflowing.",),
    },
    {
        "title": "Damaged desk - Library reading room",
        "category": "Furniture",
        "building": "Library",
        "area": "Reading Room",
        "reports": ("A desk has a broken leg and is unsafe.",),
    },
)


def seed_demo_data():
    locations = {
        (location.building, location.area): location
        for location in list_locations()
    }
    existing_titles = {incident.title for incident in list_incidents()}
    created = 0

    for demo in DEMO_INCIDENTS:
        if demo["title"] in existing_titles:
            continue
        location = locations[(demo["building"], demo["area"])]
        display_location = f"{location.building} - {location.area}"
        incident = create_incident(
            demo["title"],
            demo["category"],
            display_location,
            location_id=location.id,
        )
        for description in demo["reports"]:
            create_report(
                description,
                demo["category"],
                display_location,
                incident.id,
                location.id,
            )
        refresh_incident_priority(incident.id)
        existing_titles.add(demo["title"])
        created += 1

    return created
