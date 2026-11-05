"""Filtering, sorting and display text for sections and climbs. No flet imports."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from core.models import Climb, Section


class SortOrder(StrEnum):
    GRADE_ASC = "grade_asc"
    GRADE_DESC = "grade_desc"


SORT_LABELS: dict[SortOrder, str] = {
    SortOrder.GRADE_ASC: "Easiest",
    SortOrder.GRADE_DESC: "Hardest",
}


@dataclass(frozen=True)
class ClimbFilter:
    """Empty fields mean "no restriction"."""

    min_grade: int | None = None
    max_grade: int | None = None
    hold_colors: frozenset[str] = frozenset()

    def matches(self, climb: Climb) -> bool:
        if self.min_grade is not None and climb.grade < self.min_grade:
            return False
        if self.max_grade is not None and climb.grade > self.max_grade:
            return False
        return not self.hold_colors or climb.hold_color in self.hold_colors


def filter_climbs(climbs: Iterable[Climb], climb_filter: ClimbFilter) -> list[Climb]:
    return [c for c in climbs if climb_filter.matches(c)]


def sort_climbs(climbs: Iterable[Climb], order: SortOrder) -> list[Climb]:
    # Ties are broken by title (then id) so the list order never jumps around.
    if order is SortOrder.GRADE_ASC:
        return sorted(climbs, key=lambda c: (c.grade, c.title, c.id))
    return sorted(climbs, key=lambda c: (-c.grade, c.title, c.id))  # GRADE_DESC


def available_hold_colors(climbs: Iterable[Climb]) -> list[str]:
    return sorted({c.hold_color for c in climbs})


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


def climb_subtitle(climb: Climb) -> str:
    """Subtitle in the climb list, e.g. "Green tag · V2"."""
    return f"{climb.tag} tag · {climb.grade_label}"


def climb_details(climb: Climb, section: Section | None) -> list[tuple[str, str]]:
    """(label, value) rows for the climb detail screen; the label is shown first."""
    return [
        ("Grade", climb.grade_label),
        ("Tag", f"{climb.tag} ({climb.tag.range_label})"),
        ("Hold color", climb.hold_color),
        ("Section", section.name if section else "Unknown"),
    ]
