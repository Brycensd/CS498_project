from datetime import date

from core.models import Climb, Section, TagColor
from features.search_sort.logic import (
    SORT_LABELS,
    SortOrder,
    climb_details,
    matches,
    result_subtitle,
    search_climbs,
)

SECTIONS = {
    "s1": Section("s1", "g1", 1, "Section 1"),
    "s2": Section("s2", "g1", 2, "Section 2"),
}


def climb(cid: str, section_id: str, name: str, grade: int, setter: str = "Sam") -> Climb:
    return Climb(cid, section_id, name, grade, TagColor.BLUE, "Red", setter, date(2026, 9, 7))


CLIMBS = [
    climb("a", "s2", "Crimp", 4),
    climb("b", "s1", "Dyno", 6, setter="Alex"),
    climb("c", "s2", "Arete", 1),
    climb("d", "s1", "Balance", 4),
]


def ids(climbs: list[Climb]) -> list[str]:
    return [c.id for c in climbs]


def test_matches_name_setter_tag_and_hold_color_ignoring_case():
    target = CLIMBS[1]
    for query in ("dyn", "ALEX", "blue", "red", "  dyno  ", ""):
        assert matches(target, query)
    assert not matches(target, "crimp")


def test_matches_ignores_grade_and_section():
    assert not matches(climb("x", "s1", "Slab", 3), "3")


def test_search_filters_by_query():
    assert ids(search_climbs(CLIMBS, "alex", SortOrder.GRADE_ASC, SECTIONS)) == ["b"]
    assert search_climbs(CLIMBS, "zzz", SortOrder.GRADE_ASC, SECTIONS) == []


def test_sort_by_grade_breaks_ties_by_name():
    assert ids(search_climbs(CLIMBS, "", SortOrder.GRADE_ASC, SECTIONS)) == ["c", "d", "a", "b"]
    assert ids(search_climbs(CLIMBS, "", SortOrder.GRADE_DESC, SECTIONS)) == ["b", "d", "a", "c"]


def test_sort_by_section_then_grade():
    assert ids(search_climbs(CLIMBS, "", SortOrder.SECTION, SECTIONS)) == ["d", "b", "c", "a"]


def test_sort_by_section_uses_number_not_id():
    sections = {"s10": Section("s10", "g1", 10, "Section 10"), **SECTIONS}
    climbs = [climb("x", "s10", "Ten", 1), climb("y", "s2", "Two", 1)]
    assert ids(search_climbs(climbs, "", SortOrder.SECTION, sections)) == ["y", "x"]


def test_every_sort_order_has_a_label():
    assert set(SORT_LABELS) == set(SortOrder)


def test_result_subtitle():
    assert result_subtitle(CLIMBS[0], SECTIONS["s2"]) == "V4 · Section 2 · Blue tag"


def test_climb_details_rows():
    assert climb_details(CLIMBS[0], SECTIONS["s2"]) == [
        ("Grade", "V4"),
        ("Tag", "Blue (V3–V5)"),
        ("Hold color", "Red"),
        ("Section", "Section 2"),
        ("Setter", "Sam"),
        ("Set on", "Sep 7, 2026"),
    ]
