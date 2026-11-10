from datetime import UTC, datetime

from core.models import Ascent, AscentStyle, Climb, TagColor, User
from features.leaderboard.logic import build_leaderboard

WHEN = datetime(2026, 10, 1, tzinfo=UTC)


def climb(climb_id: str, grade: int, hold_color: str = "Red", section_id: str = "s1") -> Climb:
    tag = next(t for t in TagColor if t.covers(grade))
    return Climb(climb_id, section_id, grade, tag, hold_color)


CLIMBS = {
    c.id: c
    for c in [
        climb("v8a", 8),
        climb("v7a", 7, "Yellow", "s2"),
        climb("v7b", 7, "Blue", "s2"),
        climb("v5a", 5),
        climb("v5b", 5),
        climb("v3a", 3),
    ]
}


def ascents(user_id: str, *climb_ids: str) -> list[Ascent]:
    return [
        Ascent(f"{user_id}-{i}", user_id, cid, AscentStyle.SEND, WHEN)
        for i, cid in enumerate(climb_ids)
    ]


def board(users: list[User], all_ascents: list[Ascent]):
    return build_leaderboard(users, all_ascents, CLIMBS.get)


def names(tier) -> list[str]:
    return [e.user.display_name for e in tier.entries]


def test_tiers_are_ordered_by_max_grade_hardest_first():
    users = [User("a", "Ann"), User("b", "Bob"), User("c", "Cy")]
    tiers = board(users, ascents("a", "v5a") + ascents("b", "v8a", "v3a") + ascents("c", "v7a"))

    assert [t.label for t in tiers] == ["V8", "V7", "V5"]
    assert [names(t) for t in tiers] == [["Bob"], ["Cy"], ["Ann"]]


def test_within_a_tier_more_climbs_at_the_max_grade_ranks_higher():
    users = [User("a", "Ann"), User("b", "Bob")]
    # Ann has more climbs overall, but only Bob's climbs at the tier grade count.
    tiers = board(users, ascents("a", "v5a", "v3a", "v3a") + ascents("b", "v5a", "v5b"))

    assert names(tiers[0]) == ["Bob", "Ann"]
    assert [e.count for e in tiers[0].entries] == [2, 1]


def test_ties_are_settled_alphabetically_ignoring_case():
    users = [User("z", "zoe"), User("m", "Mia"), User("a", "Ari")]
    tiers = board(users, ascents("z", "v5a") + ascents("m", "v5b") + ascents("a", "v5a"))

    assert names(tiers[0]) == ["Ari", "Mia", "zoe"]


def test_ranks_run_consecutively_across_tiers():
    users = [User("a", "Ann"), User("b", "Bob"), User("c", "Cy")]
    tiers = board(users, ascents("a", "v8a") + ascents("b", "v5a") + ascents("c", "v5b"))

    assert [e.rank for t in tiers for e in t.entries] == [1, 2, 3]


def test_repeats_count_once_and_top_climbs_are_labeled_by_section_and_holds():
    tiers = board([User("a", "Ann")], ascents("a", "v7a", "v7a", "v7b", "v5a"))
    entry = tiers[0].entries[0]

    assert entry.count == 2
    assert entry.climbs_label({"s2": "Section 2"}) == "Section 2 Blue holds, Section 2 Yellow holds"
    assert entry.count_label == "2 climbs"


def test_climbers_without_ascents_and_unknown_climbs_are_left_out():
    users = [User("a", "Ann"), User("b", "Bob")]
    tiers = board(users, ascents("a", "gone") + ascents("b", "v3a", "gone"))

    assert [names(t) for t in tiers] == [["Bob"]]
    assert tiers[0].entries[0].count_label == "1 climb"


def test_no_ascents_gives_an_empty_board():
    assert board([User("a", "Ann")], []) == []
