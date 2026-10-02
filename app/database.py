import sqlite3

import click
from flask import current_app, g


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campus TEXT NOT NULL,
    building TEXT NOT NULL,
    floor TEXT NOT NULL,
    area TEXT NOT NULL,
    UNIQUE (campus, building, floor, area)
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    location_id INTEGER REFERENCES locations(id),
    location_detail TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED')),
    priority TEXT NOT NULL DEFAULT 'MEDIUM'
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    location_id INTEGER REFERENCES locations(id),
    location_detail TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
"""

DEV_LOCATIONS = (
    ("Main Campus", "Engineering Block C", "Ground", "Main Entrance"),
    ("Main Campus", "Engineering Block C", "Ground", "Hostel Gate"),
    ("Main Campus", "Hostel A", "Ground", "Common Area"),
    ("Main Campus", "Library", "First", "Reading Room"),
    ("Main Campus", "Cafeteria", "Ground", "Dining Area"),
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    _add_missing_columns(db)
    db.executemany(
        """
        INSERT OR IGNORE INTO locations (campus, building, floor, area)
        VALUES (?, ?, ?, ?)
        """,
        DEV_LOCATIONS,
    )
    db.commit()
    click.echo("Initialized the database.")


def _add_missing_columns(db):
    for table, definition in (
        ("incidents", "location_id INTEGER REFERENCES locations(id)"),
        ("incidents", "location_detail TEXT NOT NULL DEFAULT ''"),
        ("reports", "location_id INTEGER REFERENCES locations(id)"),
        ("reports", "location_detail TEXT NOT NULL DEFAULT ''"),
    ):
        columns = {
            row["name"] for row in db.execute(f"PRAGMA table_info({table})")
        }
        column_name = definition.split()[0]
        if column_name not in columns:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")
