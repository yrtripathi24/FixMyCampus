from app.repositories.incidents import (
    count_incident_reports,
    create_incident,
    get_incident,
    update_incident_priority,
)
from app.repositories.reports import attach_report_to_incident, create_report
from app.services.priority_service import calculate_priority


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
    priority = calculate_priority(1, report.category, report.created_at).priority
    return create_incident(
        title,
        report.category,
        report.location,
        priority=priority,
        location_id=report.location_id,
        location_detail=report.location_detail,
    )


def refresh_incident_priority(incident_id):
    incident = get_incident(incident_id)
    if incident is None:
        return None
    priority = calculate_priority(
        count_incident_reports(incident.id),
        incident.category,
        incident.created_at,
    ).priority
    return update_incident_priority(incident.id, priority)
