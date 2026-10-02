from collections import Counter
from datetime import datetime

from app.repositories.incidents import count_incident_reports, list_incidents
from app.repositories.locations import get_location


def _parse_timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _breakdown(counter):
    maximum = max(counter.values(), default=0)
    return [
        {
            "label": label,
            "count": count,
            "percentage": round(count / maximum * 100) if maximum else 0,
        }
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _building_name(incident):
    if incident.location_id:
        location = get_location(incident.location_id)
        if location is not None:
            return location.building
    return incident.location


def get_analytics():
    incidents = list_incidents()
    report_counts = {
        incident.id: count_incident_reports(incident.id)
        for incident in incidents
    }
    resolved_durations = [
        (
            _parse_timestamp(incident.resolved_at)
            - _parse_timestamp(incident.created_at)
        ).total_seconds()
        / 3600
        for incident in incidents
        if incident.resolved_at
    ]
    total_reports = sum(report_counts.values())

    return {
        "open_count": sum(incident.status == "OPEN" for incident in incidents),
        "resolved_count": sum(incident.status == "RESOLVED" for incident in incidents),
        "average_reports": round(total_reports / len(incidents), 1) if incidents else 0,
        "average_resolution_hours": (
            round(sum(resolved_durations) / len(resolved_durations), 1)
            if resolved_durations
            else None
        ),
        "category_breakdown": _breakdown(Counter(incident.category for incident in incidents)),
        "building_breakdown": _breakdown(Counter(_building_name(incident) for incident in incidents)),
    }
