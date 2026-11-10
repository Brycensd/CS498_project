from datetime import UTC, date, datetime
from pathlib import Path

from core.memory_repo import (
    DEMO_USER_ID,
    InMemoryAscentRepository,
    InMemoryNewsRepository,
    seed_repositories,
)
from core.models import Ascent, AscentStyle, Climb, Comment, NewsPost, TagColor

ASSETS = Path(__file__).resolve().parents[1] / "src" / "assets"


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
    ascents = InMemoryAscentRepository()
    now = datetime(2026, 10, 1, tzinfo=UTC)
    ascents.add(Ascent("a1", DEMO_USER_ID, "s1c1", AscentStyle.FLASH, now))
    ascents.add(Ascent("a2", "other", "s1c1", AscentStyle.SEND, now))

    assert [a.id for a in ascents.list_for_user(DEMO_USER_ID)] == ["a1"]
    assert [a.id for a in ascents.list_for_climb("s1c1")] == ["a1", "a2"]


def test_demo_user_starts_with_sends_of_real_climbs():
    repos = seed_repositories()
    sends = repos.ascents.list_for_user(DEMO_USER_ID)
    assert sends
    assert all(repos.climbs.get_climb(a.climb_id) is not None for a in sends)


def test_seeded_ascents_reference_existing_users_and_climbs():
    repos = seed_repositories()
    users = repos.users.list_users()
    assert len(users) > 1
    for user in users:
        for ascent in repos.ascents.list_for_user(user.id):
            assert repos.climbs.get_climb(ascent.climb_id) is not None, ascent
    total = sum(len(repos.ascents.list_for_user(u.id)) for u in users)
    assert total == sum(len(repos.ascents.list_for_climb(c.id)) for c in repos.climbs.list_climbs())


def test_news_is_seeded_with_the_anniversary_post():
    posts = seed_repositories().news.list_posts()
    assert posts[0].title == "Anniversary Party"
    assert posts[0].event_on == date(2026, 11, 7)


def test_news_is_listed_newest_first():
    def post(pid: str, day: int) -> NewsPost:
        return NewsPost(pid, pid, "", datetime(2026, 11, day, tzinfo=UTC))

    news = InMemoryNewsRepository([post("old", 1), post("new", 3), post("mid", 2)])
    assert [p.id for p in news.list_posts()] == ["new", "mid", "old"]


def test_comments_are_returned_oldest_first():
    repos = seed_repositories()
    later = Comment("c2", "s1c1", DEMO_USER_ID, "second", datetime(2026, 10, 2, tzinfo=UTC))
    earlier = Comment("c1", "s1c1", DEMO_USER_ID, "first", datetime(2026, 10, 1, tzinfo=UTC))
    repos.comments.add(later)
    repos.comments.add(earlier)

    assert [c.text for c in repos.comments.list_for_climb("s1c1")] == ["first", "second"]
    assert repos.comments.list_for_climb("s2c1") == []


def test_demo_user_exists_with_a_picture_on_disk():
    users = seed_repositories().users
    user = users.get(DEMO_USER_ID)
    assert user.display_name == "Daniel Woods"
    assert (ASSETS / user.avatar).is_file()
    assert users.get("nobody") is None


def test_climb_title_comes_from_hold_color():
    climb = Climb("x", "s1", 2, TagColor.GREEN, "Blue")
    assert climb.title == "Blue holds"


def test_seeded_climbs_differ_by_hold_color_or_tag_within_a_section():
    repo = seed_repositories().climbs
    for section in repo.list_sections():
        pairs = [(c.hold_color, c.tag) for c in repo.list_climbs(section.id)]
        assert len(pairs) == len(set(pairs))
