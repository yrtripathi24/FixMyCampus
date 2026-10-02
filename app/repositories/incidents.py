from datetime import datetime, timezone

from app.database import get_db
from app.models import Incident


def _now():
    return datetime.now(timezone.utc).isoformat()


def _to_incident(row):
    return Incident(**dict(row)) if row else None


def create_incident(
    title,
    category,
    location,
    status="OPEN",
    priority="MEDIUM",
    location_id=None,
    location_detail="",
):
    timestamp = _now()
    cursor = get_db().execute(
        """
        INSERT INTO incidents
            (title, category, location, location_id, location_detail,
             status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            category,
            location,
            location_id,
            location_detail,
            status,
            priority,
            timestamp,
            timestamp,
        ),
    )
    get_db().commit()
    return get_incident(cursor.lastrowid)


def get_incident(incident_id):
    row = get_db().execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    return _to_incident(row)


def list_incidents(category=None, status=None):
    query = "SELECT * FROM incidents"
    filters = []
    values = []

    if category:
        filters.append("category = ?")
        values.append(category)
    if status:
        filters.append("status = ?")
        values.append(status)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY created_at DESC"

    rows = get_db().execute(query, values).fetchall()
    return [_to_incident(row) for row in rows]


def count_incident_reports(incident_id):
    row = get_db().execute(
        "SELECT COUNT(*) AS report_count FROM reports WHERE incident_id = ?",
        (incident_id,),
    ).fetchone()
    return row["report_count"]
