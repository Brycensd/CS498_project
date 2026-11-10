from datetime import UTC, datetime

import pytest

from core.models import Ascent, AscentStyle, Climb, Section, TagColor, User
from features.profile import logic

V3 = Climb("c3", "s1", 3, TagColor.WHITE, "Blue")
V5 = Climb("c5", "s2", 5, TagColor.BLACK, "Green")
V5B = Climb("c5b", "s1", 5, TagColor.BLUE, "Red")
CLIMBS = {c.id: c for c in (V3, V5, V5B)}
SECTIONS = [Section("s2", "g", 2, "Section 2"), Section("s1", "g", 1, "Section 1")]


def ascent(aid: str, climb_id: str, day: int, style=AscentStyle.SEND) -> Ascent:
    return Ascent(aid, "u", climb_id, style, datetime(2026, 10, day, tzinfo=UTC))


def test_sends_are_newest_first_and_skip_removed_climbs():
    history = logic.sends(
        [ascent("a1", "c3", 1), ascent("a2", "gone", 5), ascent("a3", "c5", 3)], CLIMBS.get
    )
    assert [s.ascent.id for s in history] == ["a3", "a1"]
    assert history[0].climb == V5


def test_top_send_is_hardest_and_earliest_on_a_tie():
    history = logic.sends(
        [ascent("a1", "c3", 1), ascent("a2", "c5b", 9), ascent("a3", "c5", 4)], CLIMBS.get
    )
    assert logic.top_send(history).ascent.id == "a3"
    assert logic.top_send([]) is None


def test_labels():
    send = logic.Send(ascent("a", "c5", 3, AscentStyle.FLASH), V5)
    assert logic.send_label(send) == "Flash · Oct 3"
    assert logic.climb_label(V5, {"s2": "Section 2"}) == "Section 2 · Green holds · V5"


def test_climb_choices_ordered_by_section_then_grade():
    choices = logic.climb_choices(CLIMBS.values(), SECTIONS)
    assert [cid for cid, _ in choices] == ["c3", "c5b", "c5"]
    assert choices[0][1] == "Section 1 · Blue holds · V3 (White tag)"


def test_new_ascent_gets_a_fresh_id():
    now = datetime(2026, 11, 10, tzinfo=UTC)
    a = logic.new_ascent("u", "c3", AscentStyle.FLASH, now)
    b = logic.new_ascent("u", "c3", AscentStyle.FLASH, now)
    assert a.id != b.id
    assert (a.user_id, a.climb_id, a.style, a.climbed_at) == ("u", "c3", AscentStyle.FLASH, now)


def test_edit_profile_trims_and_keeps_other_fields():
    user = User("u", "Old", avatar="avatars/x.png", bio="old bio")
    updated = logic.edit_profile(user, "  New   Name ", "  Hello  \n")
    assert updated == User("u", "New Name", avatar="avatars/x.png", bio="Hello")
    assert user.display_name == "Old"  # original untouched


@pytest.mark.parametrize(
    ("name", "bio", "field"),
    [
        ("   ", "", "name"),
        ("x" * (logic.MAX_NAME_LENGTH + 1), "", "name"),
        ("Ok", "x" * (logic.MAX_BIO_LENGTH + 1), "bio"),
    ],
)
def test_edit_profile_rejects_invalid_input(name, bio, field):
    with pytest.raises(logic.ProfileError) as err:
        logic.edit_profile(User("u", "Old"), name, bio)
    assert err.value.field == field


def test_edit_profile_allows_empty_bio_and_limits_exactly():
    user = User("u", "Old", bio="something")
    name = "x" * logic.MAX_NAME_LENGTH
    bio = "y" * logic.MAX_BIO_LENGTH
    assert logic.edit_profile(user, name, "").bio == ""
    assert logic.edit_profile(user, name, bio).bio == bio


def test_initials():
    assert logic.initials("Daniel Woods") == "DW"
    assert logic.initials("cher") == "C"
    assert logic.initials("") == "?"
