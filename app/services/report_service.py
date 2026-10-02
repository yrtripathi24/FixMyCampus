from app.repositories.incidents import create_incident
from app.repositories.reports import create_report


CATEGORIES = (
    "Electrical",
    "Plumbing",
    "Cleanliness",
    "Furniture",
    "Infrastructure",
    "Other",
)
MAX_LOCATION_LENGTH = 120
MAX_DESCRIPTION_LENGTH = 1000


def validate_report(category, location, description):
    category = category.strip()
    location = location.strip()
    description = description.strip()
    errors = {}

    if category not in CATEGORIES:
        errors["category"] = "Choose a valid category."
    if not location:
        errors["location"] = "Location is required."
    elif len(location) > MAX_LOCATION_LENGTH:
        errors["location"] = "Location must be 120 characters or fewer."
    if not description:
        errors["description"] = "Description is required."
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors["description"] = "Description must be 1000 characters or fewer."

    return {"category": category, "location": location, "description": description}, errors


def submit_report(category, location, description):
    title = description.split(".", 1)[0][:120]
    incident = create_incident(title, category, location)
    report = create_report(description, category, location, incident.id)
    return incident, report
