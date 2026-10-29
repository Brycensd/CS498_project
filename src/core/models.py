"""Shared domain models.

All models are frozen dataclasses so they can be passed between features safely.
Ids are strings so server-generated UUIDs can replace the seeded ids later.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


def new_id() -> str:
    return uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class Gym:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class Section:
    id: str
    gym_id: str
    number: int
    name: str
    # Asset path relative to src/assets (e.g. "walls/section_1.png") or a URL;
    # ft.Image accepts both, so photos can move to a server without a model change.
    wall_image: str | None = None


@dataclass(frozen=True, slots=True)
class Climb:
    id: str
    section_id: str
    name: str
    # Assumption: bouldering only, so grades are V-scale numbers (V0 = 0). Stored as int
    # so sorting and range filters never re-parse strings. Revisit if rope grades are added.
    grade: int
    color: str  # hold color, e.g. "Red"
    setter: str
    set_on: date
    image: str | None = None

    @property
    def grade_label(self) -> str:
        return f"V{self.grade}"


class AscentStyle(StrEnum):
    FLASH = "flash"
    SEND = "send"
    REPEAT = "repeat"


@dataclass(frozen=True, slots=True)
class Ascent:
    id: str
    user_id: str
    climb_id: str
    style: AscentStyle
    climbed_at: datetime


@dataclass(frozen=True, slots=True)
class Comment:
    id: str
    climb_id: str
    user_id: str
    text: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class User:
    id: str
    display_name: str
