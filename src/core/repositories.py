"""Repository interfaces. Features read and write data only through these.

The in-memory implementation lives in memory_repo.py; a SQLite or server-backed
implementation can replace it later without touching features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.models import Ascent, Climb, Comment, Gym, Section, User


class ClimbRepository(Protocol):
    """The gym, its sections and their climbs."""

    def get_gym(self) -> Gym: ...

    def list_sections(self) -> list[Section]:
        """Sections ordered by number."""
        ...

    def get_section(self, section_id: str) -> Section | None: ...

    def list_climbs(self, section_id: str | None = None) -> list[Climb]:
        """Climbs in one section, or all climbs when section_id is None."""
        ...

    def get_climb(self, climb_id: str) -> Climb | None: ...


class AscentRepository(Protocol):
    def add(self, ascent: Ascent) -> None: ...

    def list_for_user(self, user_id: str) -> list[Ascent]: ...

    def list_for_climb(self, climb_id: str) -> list[Ascent]: ...


class CommentRepository(Protocol):
    def add(self, comment: Comment) -> None: ...

    def list_for_climb(self, climb_id: str) -> list[Comment]:
        """Comments oldest first."""
        ...


class UserRepository(Protocol):
    def get(self, user_id: str) -> User | None: ...

    def list_users(self) -> list[User]: ...


@dataclass(frozen=True)
class Repositories:
    climbs: ClimbRepository
    ascents: AscentRepository
    comments: CommentRepository
    users: UserRepository
