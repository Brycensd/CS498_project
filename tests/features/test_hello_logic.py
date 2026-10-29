from datetime import date

from core.models import Climb, Section
from features.hello.logic import section_rows


def test_rows_are_ordered_by_number_with_climb_counts():
    sections = [Section("b", "g", 2, "Section 2"), Section("a", "g", 1, "Section 1")]
    climbs = [Climb("c1", "a", "One", 1, "Red", "Sam", date(2026, 1, 1))]

    assert section_rows(sections, climbs) == [("Section 1", "1 climb"), ("Section 2", "0 climbs")]
