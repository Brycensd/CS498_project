from datetime import UTC, date, datetime

import pytest

from core.models import Ascent, AscentStyle, Climb, NewsPost, TagColor
from features.home import logic

CLIMBS = {
    "easy": Climb("easy", "s1", 1, TagColor.YELLOW, "Red"),
    "hard": Climb("hard", "s1", 6, TagColor.PURPLE, "Blue"),
    "mid": Climb("mid", "s2", 4, TagColor.BLUE, "Green"),
}


def ascent(climb_id: str, style: AscentStyle = AscentStyle.SEND) -> Ascent:
    return Ascent(f"a-{climb_id}", "u1", climb_id, style, datetime(2026, 10, 1, tzinfo=UTC))


def test_hardest_send_picks_the_highest_grade():
    ascents = [ascent("easy"), ascent("hard"), ascent("mid")]
    assert logic.hardest_send(ascents, CLIMBS) == CLIMBS["hard"]


@pytest.mark.parametrize("style", list(AscentStyle))
def test_every_ascent_style_counts_as_a_send(style):
    assert logic.hardest_send([ascent("mid", style)], CLIMBS) == CLIMBS["mid"]


def test_ascents_of_removed_climbs_are_ignored():
    assert logic.hardest_send([ascent("easy"), ascent("gone")], CLIMBS) == CLIMBS["easy"]
    assert logic.hardest_send([ascent("gone")], CLIMBS) is None


def test_hardest_send_label():
    assert logic.hardest_send_label(CLIMBS["hard"]) == "V6"
    assert logic.hardest_send_label(None) == "No sends yet"


@pytest.mark.parametrize(
    ("name", "expected"),
    [("Daniel Woods", "DW"), ("ada lovelace byron", "AB"), ("Madonna", "M"), ("  ", "?")],
)
def test_initials(name, expected):
    assert logic.initials(name) == expected


def test_post_labels():
    posted = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)
    event = NewsPost("n1", "Party", "", posted, event_on=date(2026, 11, 7))
    plain = NewsPost("n2", "New holds", "", posted)

    assert logic.event_label(event) == "Saturday, Nov 7"
    assert logic.event_label(plain) is None
    assert logic.posted_label(plain) == "Posted Nov 1"
