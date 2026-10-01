from datetime import datetime, timezone

from app.database import get_db
from app.models import Incident


def _now():
    return datetime.now(timezone.utc).isoformat()


def _to_incident(row):
    return Incident(**dict(row)) if row else None


def create_incident(title, category, location, status="OPEN", priority="MEDIUM"):
    timestamp = _now()
    cursor = get_db().execute(
        """
        INSERT INTO incidents
            (title, category, location, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (title, category, location, status, priority, timestamp, timestamp),
    )
    get_db().commit()
    return get_incident(cursor.lastrowid)


def get_incident(incident_id):
    row = get_db().execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    return _to_incident(row)


def list_incidents():
    rows = get_db().execute(
        "SELECT * FROM incidents ORDER BY created_at DESC"
    ).fetchall()
    return [_to_incident(row) for row in rows]
