from app.repositories.incidents import create_incident
from app.repositories.reports import attach_report_to_incident, create_report


CATEGORIES = (
    "Electrical",
    "Plumbing",
    "Cleanliness",
    "Furniture",
    "Infrastructure",
    "Other",
)
MAX_LOCATION_LENGTH = 120
MAX_LOCATION_DETAIL_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000


def validate_report(
    category, location, description, location_id=None, location_detail=""
):
    category = category.strip()
    location = location.strip()
    description = description.strip()
    location_detail = location_detail.strip()
    errors = {}

    if category not in CATEGORIES:
        errors["category"] = "Choose a valid category."
    if not location:
        errors["location"] = "Location is required."
    elif len(location) > MAX_LOCATION_LENGTH:
        errors["location"] = "Location must be 120 characters or fewer."
    if len(location_detail) > MAX_LOCATION_DETAIL_LENGTH:
        errors["location_detail"] = "Location details must be 200 characters or fewer."
    if not description:
        errors["description"] = "Description is required."
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors["description"] = "Description must be 1000 characters or fewer."

    return {
        "category": category,
        "location": location,
        "description": description,
        "location_id": location_id,
        "location_detail": location_detail,
    }, errors


def submit_report(
    category, location, description, location_id=None, location_detail=""
):
    report = create_report(
        description, category, location, location_id=location_id, location_detail=location_detail
    )
    incident = create_incident_for_report(report)
    attach_report_to_incident(report.id, incident.id)
    return incident, report


def create_incident_for_report(report):
    title = report.description.split(".", 1)[0][:120]
    return create_incident(
        title,
        report.category,
        report.location,
        location_id=report.location_id,
        location_detail=report.location_detail,
    )
