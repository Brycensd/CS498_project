from datetime import UTC, datetime

from core.memory_repo import DEMO_USER_ID, seed_repositories
from core.models import Ascent, AscentStyle, Climb, Comment, TagColor


def test_seed_has_four_numbered_sections_that_all_have_climbs():
    repo = seed_repositories().climbs
    sections = repo.list_sections()

    assert [s.number for s in sections] == list(range(1, 5))
    for section in sections:
        climbs = repo.list_climbs(section.id)
        assert climbs
        assert all(c.section_id == section.id for c in climbs)
        assert section.wall_image == f"walls/section_{section.number}.jpg"


def test_seeded_grades_fall_inside_their_tag_range():
    for climb in seed_repositories().climbs.list_climbs():
        assert climb.tag.covers(climb.grade), climb


def test_every_tag_has_at_least_one_climb():
    tags = {c.tag for c in seed_repositories().climbs.list_climbs()}
    assert tags == set(TagColor)


def test_lookups_by_id():
    repo = seed_repositories().climbs
    climb = repo.list_climbs("s3")[0]

    assert repo.get_section("s3").number == 3
    assert repo.get_climb(climb.id) == climb
    assert repo.get_section("missing") is None
    assert repo.get_climb("missing") is None
    assert len(repo.list_climbs()) == sum(len(repo.list_climbs(s.id)) for s in repo.list_sections())


def test_ascents_filter_by_user_and_climb():
    repos = seed_repositories()
    now = datetime(2026, 10, 1, tzinfo=UTC)
    repos.ascents.add(Ascent("a1", DEMO_USER_ID, "s1c1", AscentStyle.FLASH, now))
    repos.ascents.add(Ascent("a2", "other", "s1c1", AscentStyle.SEND, now))

    assert [a.id for a in repos.ascents.list_for_user(DEMO_USER_ID)] == ["a1"]
    assert [a.id for a in repos.ascents.list_for_climb("s1c1")] == ["a1", "a2"]


def test_comments_are_returned_oldest_first():
    repos = seed_repositories()
    later = Comment("c2", "s1c1", DEMO_USER_ID, "second", datetime(2026, 10, 2, tzinfo=UTC))
    earlier = Comment("c1", "s1c1", DEMO_USER_ID, "first", datetime(2026, 10, 1, tzinfo=UTC))
    repos.comments.add(later)
    repos.comments.add(earlier)

    assert [c.text for c in repos.comments.list_for_climb("s1c1")] == ["first", "second"]
    assert repos.comments.list_for_climb("s2c1") == []


def test_demo_user_exists():
    users = seed_repositories().users
    assert users.get(DEMO_USER_ID).display_name
    assert users.get("nobody") is None


def test_climb_title_comes_from_hold_color():
    climb = Climb("x", "s1", 2, TagColor.GREEN, "Blue")
    assert climb.title == "Blue holds"


def test_seeded_climbs_differ_by_hold_color_or_tag_within_a_section():
    repo = seed_repositories().climbs
    for section in repo.list_sections():
        pairs = [(c.hold_color, c.tag) for c in repo.list_climbs(section.id)]
        assert len(pairs) == len(set(pairs))
