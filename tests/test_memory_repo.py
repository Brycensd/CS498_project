from datetime import UTC, datetime

from core.memory_repo import DEMO_USER_ID, SECTION_COUNT, seed_repositories
from core.models import Ascent, AscentStyle, Comment


def test_seed_has_eight_numbered_sections_with_two_or_three_climbs():
    repo = seed_repositories().climbs
    sections = repo.list_sections()

    assert SECTION_COUNT == 8
    assert [s.number for s in sections] == list(range(1, 9))
    for section in sections:
        climbs = repo.list_climbs(section.id)
        assert 2 <= len(climbs) <= 3
        assert all(c.section_id == section.id for c in climbs)
        assert section.wall_image == f"walls/section_{section.number}.png"


def test_seeded_grades_fall_inside_their_tag_range():
    for climb in seed_repositories().climbs.list_climbs():
        low, high = climb.tag.grade_range
        assert low <= climb.grade <= high, climb


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
