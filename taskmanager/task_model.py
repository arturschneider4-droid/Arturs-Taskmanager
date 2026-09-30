from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class ControlMode(str, Enum):
    SELF = "self"
    DELEGATED = "delegated"
    WAITING = "waiting"


@dataclass(frozen=True)
class TaskDraft:
    title: str
    description: str = ""
    project_id: int | None = None
    priority: str = "important_not_urgent"
    status: str = "Offen"
    subtasks: tuple[tuple[str, bool], ...] = ()
    recurrence: str = "none"
    planning_date: date | None = None
    planning_time: time | None = None
    deadline: date | None = None
    estimated_minutes: int | None = None
    is_top_three: bool = False
    reminder_enabled: bool = False
    reminder_at: datetime | None = None
    reminder_lead_minutes: int | None = None
    control_mode: ControlMode = ControlMode.SELF
    responsible_party: str | None = None
    delegated_at: datetime | None = None
    last_contact_at: datetime | None = None
    expected_response_at: datetime | None = None
    follow_up_date: date | None = None
    people_tags: tuple[str, ...] = ()

    def __post_init__(self):
        title = self.title.strip()
        if not title:
            raise ValueError("Titel darf nicht leer sein")
        object.__setattr__(self, "title", title)
        mode = ControlMode(self.control_mode)
        object.__setattr__(self, "control_mode", mode)
        party = self.responsible_party.strip() if self.responsible_party else None
        object.__setattr__(self, "responsible_party", party)
        if self.reminder_at is not None and not self.reminder_enabled:
            raise ValueError("Erinnerung muss aktiviert sein")
        if mode in {ControlMode.DELEGATED, ControlMode.WAITING} and not party:
            raise ValueError("Person oder Organisation ist erforderlich")
        if self.estimated_minutes is not None and self.estimated_minutes <= 0:
            raise ValueError("Geschätzte Dauer muss positiv sein")


@dataclass(frozen=True)
class TaskRecord:
    id: int
    draft: TaskDraft
    created_at: datetime
    updated_at: datetime
    project_name: str | None = None

