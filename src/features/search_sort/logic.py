"""Searching, sorting and display text for climbs across the gym. No flet imports."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum

from core.models import Climb, Section


class SortOrder(StrEnum):
    GRADE_ASC = "grade_asc"
    GRADE_DESC = "grade_desc"
    SECTION = "section"


SORT_LABELS: dict[SortOrder, str] = {
    SortOrder.GRADE_ASC: "Easiest",
    SortOrder.GRADE_DESC: "Hardest",
    SortOrder.SECTION: "Section",
}


def matches(climb: Climb, query: str) -> bool:
    """Case-insensitive match on title, tag and hold color.

    Grade and section are left out on purpose: "3" would match both V3 and Section 3.
    """
    text = f"{climb.title} {climb.tag} {climb.hold_color}".lower()
    return query.strip().lower() in text


def search_climbs(
    climbs: Iterable[Climb],
    query: str,
    order: SortOrder,
    sections: Mapping[str, Section],
) -> list[Climb]:
    """Climbs matching query in the given order. sections maps section id to Section."""
    hits = [c for c in climbs if matches(c, query)]
    # Ties are broken by title (then id) so the list order never jumps around.
    if order is SortOrder.GRADE_ASC:
        return sorted(hits, key=lambda c: (c.grade, c.title, c.id))
    if order is SortOrder.GRADE_DESC:
        return sorted(hits, key=lambda c: (-c.grade, c.title, c.id))
    return sorted(hits, key=lambda c: (sections[c.section_id].number, c.grade, c.title, c.id))


def result_subtitle(climb: Climb, section: Section) -> str:
    """Subtitle in the results list, e.g. "Blue tag · V5 · Section 3"."""
    return f"{climb.tag} tag · {climb.grade_label} · {section.name}"


def climb_details(climb: Climb, section: Section) -> list[tuple[str, str]]:
    """(label, value) rows for the climb detail screen; the label is shown first."""
    return [
        ("Grade", climb.grade_label),
        ("Tag", f"{climb.tag} ({climb.tag.range_label})"),
        ("Hold color", climb.hold_color),
        ("Section", section.name),
    ]
