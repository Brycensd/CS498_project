"""In-memory repositories with placeholder seed data.

Data lives only for the lifetime of the process; every launch starts from the seed.
"""

from __future__ import annotations

from collections import defaultdict

from core.models import Ascent, Climb, Comment, Gym, Section, TagColor, User
from core.repositories import Repositories

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


# Section number -> (hold color, tag, grade) placeholders for each climb on that wall.
# Every tag is used at least once. A hold color can repeat within a section, so hold color
# and tag together tell its climbs apart.
_SECTION_CLIMBS: dict[int, list[tuple[str, TagColor, int]]] = {
    1: [
        ("Red", TagColor.RED, 0),
        ("White", TagColor.WHITE, 3),
        ("Blue", TagColor.YELLOW, 1),
        ("Red", TagColor.YELLOW, 1),
        ("Yellow", TagColor.PINK, 8),
    ],
    2: [
        ("Pink", TagColor.BLUE, 4),
        ("Green", TagColor.BLACK, 5),
        ("Yellow", TagColor.PURPLE, 6),
        ("Green", TagColor.WHITE, 3),
        ("Blue", TagColor.RED, 0),
    ],
    3: [
        ("Blue", TagColor.ORANGE, 7),
        ("Green", TagColor.BLUE, 4),
        ("Red", TagColor.WHITE, 3),
        ("White", TagColor.PURPLE, 6),
        ("Red", TagColor.GREEN, 2),
    ],
    4: [
        ("Purple", TagColor.BLACK, 5),
        ("Green", TagColor.PINK, 8),
        ("Purple", TagColor.ORANGE, 7),
        ("Yellow", TagColor.YELLOW, 1),
    ],
}


def seed_repositories() -> Repositories:
    """Build repositories with the sections and placeholder climbs in _SECTION_CLIMBS."""
    gym = Gym(id="g1", name="Demo Gym")
    sections: list[Section] = []
    climbs: list[Climb] = []
    for number, section_climbs in _SECTION_CLIMBS.items():
        section = Section(
            id=f"s{number}",
            gym_id=gym.id,
            number=number,
            name=f"Section {number}",
            wall_image=f"walls/section_{number}.jpg",
        )
        sections.append(section)
        for i, (hold_color, tag, grade) in enumerate(section_climbs):
            climbs.append(
                Climb(
                    id=f"s{number}c{i + 1}",
                    section_id=section.id,
                    grade=grade,
                    tag=tag,
                    hold_color=hold_color,
                )
            )
    users = [User(id=DEMO_USER_ID, display_name="Demo Climber")]
    return Repositories(
        climbs=InMemoryClimbRepository(gym, sections, climbs),
        ascents=InMemoryAscentRepository(),
        comments=InMemoryCommentRepository(),
        users=InMemoryUserRepository(users),
    )
