from app.database import get_db
from app.models import Location


def _to_location(row):
    return Location(**dict(row)) if row else None


def list_locations():
    rows = get_db().execute(
        """
        SELECT * FROM locations
        ORDER BY campus, building, floor, area
        """
    ).fetchall()
    return [_to_location(row) for row in rows]


def get_location(location_id):
    row = get_db().execute(
        "SELECT * FROM locations WHERE id = ?", (location_id,)
    ).fetchone()
    return _to_location(row)


def create_location(campus, building, floor, area):
    cursor = get_db().execute(
        """
        INSERT INTO locations (campus, building, floor, area)
        VALUES (?, ?, ?, ?)
        """,
        (campus, building, floor, area),
    )
    get_db().commit()
    return get_location(cursor.lastrowid)
