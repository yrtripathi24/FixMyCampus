from dataclasses import dataclass


@dataclass(frozen=True)
class Incident:
    id: int
    title: str
    category: str
    location: str
    status: str
    priority: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Report:
    id: int
    incident_id: int | None
    description: str
    category: str
    location: str
    created_at: str
