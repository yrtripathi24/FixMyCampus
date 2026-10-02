from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    id: int
    campus: str
    building: str
    floor: str
    area: str


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
    location_id: int | None = None
    location_detail: str = ""


@dataclass(frozen=True)
class Report:
    id: int
    incident_id: int | None
    description: str
    category: str
    location: str
    created_at: str
    location_id: int | None = None
    location_detail: str = ""
