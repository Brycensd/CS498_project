from datetime import date

import pytest

from core.models import Climb, Section
from features.sections.logic import (
    SORT_LABELS,
    ClimbFilter,
    SortOrder,
    available_colors,
    climb_details,
    filter_climbs,
    grade_span,
    section_summary,
    sort_climbs,
)


def climb(cid: str, name: str, grade: int, color: str = "Red", day: int = 1) -> Climb:
    return Climb(cid, "s1", name, grade, color, "Sam", date(2026, 9, day))


CLIMBS = [
    climb("a", "Crimp", 4, "Red", day=3),
    climb("b", "arete", 1, "Blue", day=5),
    climb("c", "Dyno", 6, "Red", day=1),
    climb("d", "Balance", 4, "Green", day=5),
]


def names(climbs: list[Climb]) -> list[str]:
    return [c.name for c in climbs]


class TestFilter:
    def test_empty_filter_keeps_everything(self):
        assert filter_climbs(CLIMBS, ClimbFilter()) == CLIMBS

    def test_grade_range_is_inclusive(self):
        result = filter_climbs(CLIMBS, ClimbFilter(min_grade=4, max_grade=4))
        assert names(result) == ["Crimp", "Balance"]

    def test_open_ended_grade_bounds(self):
        assert names(filter_climbs(CLIMBS, ClimbFilter(min_grade=5))) == ["Dyno"]
        assert names(filter_climbs(CLIMBS, ClimbFilter(max_grade=1))) == ["arete"]

    def test_colors(self):
        result = filter_climbs(CLIMBS, ClimbFilter(colors=frozenset({"Red", "Green"})))
        assert names(result) == ["Crimp", "Dyno", "Balance"]

    def test_filters_combine(self):
        result = filter_climbs(CLIMBS, ClimbFilter(min_grade=5, colors=frozenset({"Red"})))
        assert names(result) == ["Dyno"]


class TestSort:
    def test_grade_ascending_breaks_ties_by_name(self):
        assert names(sort_climbs(CLIMBS, SortOrder.GRADE_ASC)) == [
            "arete",
            "Balance",
            "Crimp",
            "Dyno",
        ]

    def test_grade_descending(self):
        assert names(sort_climbs(CLIMBS, SortOrder.GRADE_DESC)) == [
            "Dyno",
            "Balance",
            "Crimp",
            "arete",
        ]

    def test_name_is_case_insensitive(self):
        assert names(sort_climbs(CLIMBS, SortOrder.NAME)) == ["arete", "Balance", "Crimp", "Dyno"]

    def test_newest_first(self):
        assert names(sort_climbs(CLIMBS, SortOrder.NEWEST)) == [
            "Balance",
            "arete",
            "Crimp",
            "Dyno",
        ]

    def test_does_not_mutate_input(self):
        original = list(CLIMBS)
        sort_climbs(CLIMBS, SortOrder.GRADE_DESC)
        assert CLIMBS == original

    @pytest.mark.parametrize("order", list(SortOrder))
    def test_every_order_has_a_label(self, order):
        assert SORT_LABELS[order]


def test_available_colors_are_unique_and_sorted():
    assert available_colors(CLIMBS) == ["Blue", "Green", "Red"]


@pytest.mark.parametrize(
    ("climbs", "expected"),
    [([], "No climbs"), ([climb("x", "X", 3)], "V3"), (CLIMBS, "V1–V6")],
)
def test_grade_span(climbs, expected):
    assert grade_span(climbs) == expected


def test_section_summary():
    assert section_summary(CLIMBS) == "4 climbs · V1–V6"
    assert section_summary([climb("x", "X", 2)]) == "1 climb · V2"
    assert section_summary([]) == "No climbs"


def test_climb_details():
    section = Section("s1", "g1", 1, "Section 1")
    rows = dict(climb_details(CLIMBS[0], section))
    assert rows == {
        "Grade": "V4",
        "Hold color": "Red",
        "Section": "Section 1",
        "Setter": "Sam",
        "Set on": "Sep 3, 2026",
    }
    assert dict(climb_details(CLIMBS[0], None))["Section"] == "Unknown"
