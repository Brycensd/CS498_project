import pytest

from core.models import Climb, Section, TagColor
from features.sections.logic import (
    SORT_LABELS,
    ClimbFilter,
    SortOrder,
    available_hold_colors,
    climb_details,
    climb_subtitle,
    filter_climbs,
    grade_span,
    section_summary,
    sort_climbs,
)


def climb(cid: str, grade: int, hold_color: str = "Red") -> Climb:
    return Climb(cid, "s1", grade, TagColor.BLUE, hold_color)


CLIMBS = [
    climb("a", 4, "Red"),
    climb("b", 1, "Blue"),
    climb("c", 6, "Red"),
    climb("d", 4, "Green"),
]


def ids(climbs: list[Climb]) -> list[str]:
    return [c.id for c in climbs]


class TestFilter:
    def test_empty_filter_keeps_everything(self):
        assert filter_climbs(CLIMBS, ClimbFilter()) == CLIMBS

    def test_grade_range_is_inclusive(self):
        result = filter_climbs(CLIMBS, ClimbFilter(min_grade=4, max_grade=4))
        assert ids(result) == ["a", "d"]

    def test_open_ended_grade_bounds(self):
        assert ids(filter_climbs(CLIMBS, ClimbFilter(min_grade=5))) == ["c"]
        assert ids(filter_climbs(CLIMBS, ClimbFilter(max_grade=1))) == ["b"]

    def test_hold_colors(self):
        result = filter_climbs(CLIMBS, ClimbFilter(hold_colors=frozenset({"Red", "Green"})))
        assert ids(result) == ["a", "c", "d"]

    def test_filters_combine(self):
        result = filter_climbs(CLIMBS, ClimbFilter(min_grade=5, hold_colors=frozenset({"Red"})))
        assert ids(result) == ["c"]


class TestSort:
    def test_grade_ascending_breaks_ties_by_title(self):
        assert ids(sort_climbs(CLIMBS, SortOrder.GRADE_ASC)) == ["b", "d", "a", "c"]

    def test_grade_descending(self):
        assert ids(sort_climbs(CLIMBS, SortOrder.GRADE_DESC)) == ["c", "d", "a", "b"]

    def test_does_not_mutate_input(self):
        original = list(CLIMBS)
        sort_climbs(CLIMBS, SortOrder.GRADE_DESC)
        assert CLIMBS == original

    @pytest.mark.parametrize("order", list(SortOrder))
    def test_every_order_has_a_label(self, order):
        assert SORT_LABELS[order]


def test_available_hold_colors_are_unique_and_sorted():
    assert available_hold_colors(CLIMBS) == ["Blue", "Green", "Red"]


@pytest.mark.parametrize(
    ("climbs", "expected"),
    [([], "No climbs"), ([climb("x", 3)], "V3"), (CLIMBS, "V1–V6")],
)
def test_grade_span(climbs, expected):
    assert grade_span(climbs) == expected


def test_section_summary():
    assert section_summary(CLIMBS) == "4 climbs · V1–V6"
    assert section_summary([climb("x", 2)]) == "1 climb · V2"
    assert section_summary([]) == "No climbs"


def test_climb_subtitle_shows_tag_and_grade():
    assert climb_subtitle(climb("x", 5, "Pink")) == "Blue tag · V5"


def test_climb_details():
    section = Section("s1", "g1", 1, "Section 1")
    rows = climb_details(CLIMBS[0], section)
    assert [label for label, _ in rows][:3] == ["Grade", "Tag", "Hold color"]
    assert dict(rows) == {
        "Grade": "V4",
        "Tag": "Blue (V3–V5)",
        "Hold color": "Red",
        "Section": "Section 1",
    }
    assert dict(climb_details(CLIMBS[0], None))["Section"] == "Unknown"
