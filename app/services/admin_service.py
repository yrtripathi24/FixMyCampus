from app.repositories.incidents import count_incident_reports, list_incidents


def get_admin_dashboard():
    incidents = list_incidents()
    report_counts = {
        incident.id: count_incident_reports(incident.id)
        for incident in incidents
    }
    most_reported = sorted(
        incidents,
        key=lambda incident: (-report_counts[incident.id], incident.id),
    )
    return {
        "open_incidents": [i for i in incidents if i.status == "OPEN"],
        "high_priority_incidents": [i for i in incidents if i.priority == "HIGH"],
        "most_reported_incidents": most_reported[:5],
        "recent_incidents": incidents[:5],
        "resolved_incidents": [i for i in incidents if i.status == "RESOLVED"],
        "report_counts": report_counts,
    }


VALID_TRANSITIONS = {
    "OPEN": {"IN_PROGRESS"},
    "IN_PROGRESS": {"RESOLVED"},
    "RESOLVED": set(),
}


class InvalidStatusTransition(ValueError):
    pass


def transition_incident_status(incident, new_status):
    from datetime import datetime, timezone

    from app.repositories.incidents import update_incident_status

    if new_status == incident.status:
        return incident
    if new_status not in VALID_TRANSITIONS.get(incident.status, set()):
        raise InvalidStatusTransition(
            f"Cannot change incident from {incident.status} to {new_status}."
        )
    return update_incident_status(
        incident.id,
        new_status,
        datetime.now(timezone.utc).isoformat(),
    )
