"""Filtering, sorting and display text for sections and climbs. No flet imports."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from core.models import Climb, Section


class SortOrder(StrEnum):
    GRADE_ASC = "grade_asc"
    GRADE_DESC = "grade_desc"
    NAME = "name"
    NEWEST = "newest"


SORT_LABELS: dict[SortOrder, str] = {
    SortOrder.GRADE_ASC: "Easiest",
    SortOrder.GRADE_DESC: "Hardest",
    SortOrder.NAME: "Name",
    SortOrder.NEWEST: "Newest",
}


@dataclass(frozen=True)
class ClimbFilter:
    """Empty fields mean "no restriction"."""

    min_grade: int | None = None
    max_grade: int | None = None
    colors: frozenset[str] = frozenset()

    def matches(self, climb: Climb) -> bool:
        if self.min_grade is not None and climb.grade < self.min_grade:
            return False
        if self.max_grade is not None and climb.grade > self.max_grade:
            return False
        return not self.colors or climb.color in self.colors


def filter_climbs(climbs: Iterable[Climb], climb_filter: ClimbFilter) -> list[Climb]:
    return [c for c in climbs if climb_filter.matches(c)]


def sort_climbs(climbs: Iterable[Climb], order: SortOrder) -> list[Climb]:
    # Ties are broken by name (then id) so the list order never jumps around.
    if order is SortOrder.GRADE_ASC:
        return sorted(climbs, key=lambda c: (c.grade, c.name, c.id))
    if order is SortOrder.GRADE_DESC:
        return sorted(climbs, key=lambda c: (-c.grade, c.name, c.id))
    if order is SortOrder.NEWEST:
        return sorted(climbs, key=lambda c: (-c.set_on.toordinal(), c.name, c.id))
    return sorted(climbs, key=lambda c: (c.name.casefold(), c.id))


def available_colors(climbs: Iterable[Climb]) -> list[str]:
    return sorted({c.color for c in climbs})


def grade_span(climbs: Iterable[Climb]) -> str:
    grades = [c.grade for c in climbs]
    if not grades:
        return "No climbs"
    low, high = min(grades), max(grades)
    return f"V{low}" if low == high else f"V{low}–V{high}"


def section_summary(climbs: list[Climb]) -> str:
    """Subtitle for a section, e.g. "3 climbs · V0–V4"."""
    if not climbs:
        return "No climbs"
    noun = "climb" if len(climbs) == 1 else "climbs"
    return f"{len(climbs)} {noun} · {grade_span(climbs)}"


def climb_details(climb: Climb, section: Section | None) -> list[tuple[str, str]]:
    """(label, value) rows for the climb detail screen."""
    set_on = climb.set_on
    return [
        ("Grade", climb.grade_label),
        ("Hold color", climb.color),
        ("Section", section.name if section else "Unknown"),
        ("Setter", climb.setter),
        ("Set on", f"{set_on:%b} {set_on.day}, {set_on.year}"),
    ]
