"""In-memory repositories with placeholder seed data.

Data lives only for the lifetime of the process; every launch starts from the seed.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from core.models import Ascent, Climb, Comment, Gym, Section, TagColor, User
from core.repositories import Repositories

SECTION_COUNT = 8
DEMO_USER_ID = "u1"


class InMemoryClimbRepository:
    def __init__(self, gym: Gym, sections: list[Section], climbs: list[Climb]) -> None:
        self._gym = gym
        self._sections = {s.id: s for s in sections}
        self._climbs = {c.id: c for c in climbs}

    def get_gym(self) -> Gym:
        return self._gym

    def list_sections(self) -> list[Section]:
        return sorted(self._sections.values(), key=lambda s: s.number)

    def get_section(self, section_id: str) -> Section | None:
        return self._sections.get(section_id)

    def list_climbs(self, section_id: str | None = None) -> list[Climb]:
        climbs = self._climbs.values()
        return [c for c in climbs if section_id is None or c.section_id == section_id]

    def get_climb(self, climb_id: str) -> Climb | None:
        return self._climbs.get(climb_id)


class InMemoryAscentRepository:
    def __init__(self) -> None:
        self._ascents: list[Ascent] = []

    def add(self, ascent: Ascent) -> None:
        self._ascents.append(ascent)

    def list_for_user(self, user_id: str) -> list[Ascent]:
        return [a for a in self._ascents if a.user_id == user_id]

    def list_for_climb(self, climb_id: str) -> list[Ascent]:
        return [a for a in self._ascents if a.climb_id == climb_id]


class InMemoryCommentRepository:
    def __init__(self) -> None:
        self._by_climb: dict[str, list[Comment]] = defaultdict(list)

    def add(self, comment: Comment) -> None:
        self._by_climb[comment.climb_id].append(comment)

    def list_for_climb(self, climb_id: str) -> list[Comment]:
        return sorted(self._by_climb.get(climb_id, []), key=lambda c: c.created_at)


class InMemoryUserRepository:
    def __init__(self, users: list[User]) -> None:
        self._users = {u.id: u for u in users}

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def list_users(self) -> list[User]:
        return list(self._users.values())


# (name, grade, tag, hold color) placeholders, cycled through the sections. Every tag is
# used at least once, and hold colors deliberately differ from tags so the UI shows they
# are independent.
_PLACEHOLDER_CLIMBS = [
    ("Warm Welcome", 0, TagColor.RED, "Yellow"),
    ("Crimp Lord", 4, TagColor.BLUE, "Red"),
    ("Slab City", 2, TagColor.GREEN, "Blue"),
    ("Dyno Might", 6, TagColor.PURPLE, "Black"),
    ("Pinch Me", 3, TagColor.WHITE, "Green"),
    ("Heel Yeah", 5, TagColor.BLACK, "Purple"),
    ("Sloper Opera", 7, TagColor.ORANGE, "Green"),
    ("Jug Life", 1, TagColor.YELLOW, "Pink"),
    ("Phases of Crimp", 8, TagColor.PINK, "White"),
    ("Mantle Piece", 2, TagColor.YELLOW, "Pink"),
    ("Gaston Station", 5, TagColor.PURPLE, "Red"),
    ("Toe Hook Tango", 3, TagColor.GREEN, "Blue"),
    ("Flag Day", 1, TagColor.GREEN, "Orange"),
    ("Sidepull Sally", 4, TagColor.WHITE, "Yellow"),
    ("Undercling Ring", 3, TagColor.BLUE, "Black"),
    ("Campus Tour", 6, TagColor.BLACK, "White"),
    ("Kneebar Hopping", 5, TagColor.BLUE, "Orange"),
    ("Smear Campaign", 0, TagColor.YELLOW, "Purple"),
    ("Match Point", 7, TagColor.PURPLE, "Blue"),
    ("Roof Rack", 8, TagColor.ORANGE, "Red"),
]
_SETTERS = ["Alex", "Sam", "Jordan", "Riley"]


def seed_repositories() -> Repositories:
    """Build repositories with 8 sections and 2-3 placeholder climbs each."""
    gym = Gym(id="g1", name="Demo Gym")
    sections: list[Section] = []
    climbs: list[Climb] = []
    placeholders = iter(_PLACEHOLDER_CLIMBS)
    for number in range(1, SECTION_COUNT + 1):
        section = Section(
            id=f"s{number}",
            gym_id=gym.id,
            number=number,
            name=f"Section {number}",
            wall_image=f"walls/section_{number}.png",
        )
        sections.append(section)
        # Alternate 2 and 3 climbs so tests and UI see both sizes.
        for i in range(2 + number % 2):
            name, grade, tag, hold_color = name, grade, tag, hold_color = next(placeholders)
            climbs.append(
                Climb(
                    id=f"s{number}c{i + 1}",
                    section_id=section.id,
                    name=name,
                    grade=grade,
                    tag=tag,
                    hold_color=hold_color,
                    setter=_SETTERS[(number + i) % len(_SETTERS)],
                    set_on=date(2026, 9, number + i),
                )
            )
    users = [User(id=DEMO_USER_ID, display_name="Demo Climber")]
    return Repositories(
        climbs=InMemoryClimbRepository(gym, sections, climbs),
        ascents=InMemoryAscentRepository(),
        comments=InMemoryCommentRepository(),
        users=InMemoryUserRepository(users),
    )
