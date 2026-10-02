from datetime import datetime, timezone

from app.database import get_db
from app.models import Report


def _to_report(row):
    return Report(**dict(row)) if row else None


def create_report(
    description,
    category,
    location,
    incident_id=None,
    location_id=None,
    location_detail="",
    photo_filename=None,
):
    created_at = datetime.now(timezone.utc).isoformat()
    cursor = get_db().execute(
        """
        INSERT INTO reports
            (incident_id, description, category, location, location_id,
             location_detail, photo_filename, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident_id,
            description,
            category,
            location,
            location_id,
            location_detail,
            photo_filename,
            created_at,
        ),
    )
    get_db().commit()
    return get_report(cursor.lastrowid)


def get_report(report_id):
    row = get_db().execute(
        "SELECT * FROM reports WHERE id = ?", (report_id,)
    ).fetchone()
    return _to_report(row)


def attach_report_to_incident(report_id, incident_id):
    cursor = get_db().execute(
        "UPDATE reports SET incident_id = ? WHERE id = ?",
        (incident_id, report_id),
    )
    get_db().commit()
    return cursor.rowcount == 1


def get_incident_reports(incident_id):
    rows = get_db().execute(
        "SELECT * FROM reports WHERE incident_id = ? ORDER BY created_at",
        (incident_id,),
    ).fetchall()
    return [_to_report(row) for row in rows]
