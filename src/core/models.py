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


class TagColor(StrEnum):
    """The gym's colored difficulty tags, easiest to hardest.

    A tag marks a climb's difficulty band and is independent of the hold color.
    """

    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    WHITE = "White"
    BLUE = "Blue"
    BLACK = "Black"
    PURPLE = "Purple"
    ORANGE = "Orange"
    PINK = "Pink"

    @property
    def grade_range(self) -> tuple[int, int | None]:
        """Inclusive (lowest, highest) V-grade this tag covers; highest is None if open-ended."""
        return TAG_GRADE_RANGES[self]

    @property
    def range_label(self) -> str:
        low, high = self.grade_range
        if high is None:
            return f"V{low}+"
        return f"V{low}" if low == high else f"V{low}–V{high}"

    def covers(self, grade: int) -> bool:
        low, high = self.grade_range
        return low <= grade and (high is None or grade <= high)


# Red, Yellow, Green and Pink are from the gym. Assumption: White through Orange continue
# the pattern of three grades, each starting one grade higher than the previous tag.
# Correct this table if the gym's chart differs; nothing else hard-codes the ranges.
TAG_GRADE_RANGES: dict[TagColor, tuple[int, int | None]] = {
    TagColor.RED: (0, 0),
    TagColor.YELLOW: (0, 2),
    TagColor.GREEN: (1, 3),
    TagColor.WHITE: (2, 4),
    TagColor.BLUE: (3, 5),
    TagColor.BLACK: (4, 6),
    TagColor.PURPLE: (5, 7),
    TagColor.ORANGE: (6, 8),
    TagColor.PINK: (8, None),  # V8 and harder
}


@dataclass(frozen=True, slots=True)
class Climb:
    id: str
    section_id: str
    name: str
    # Assumption: bouldering only, so grades are V-scale numbers (V0 = 0). Stored as int
    # so sorting and range filters never re-parse strings. Revisit if rope grades are added.
    grade: int
    tag: TagColor  # difficulty tag; its range should contain `grade`
    hold_color: str  # any color, unrelated to the tag, e.g. "Pink"
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
