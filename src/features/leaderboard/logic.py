"""Ranking climbers by their hardest grade. No flet imports.

Modeled on climbing-history.org's "Strongest boulderers" list: climbers are grouped into
tiers by the hardest grade they have sent, and within a tier ranked by how many distinct
climbs they have sent at that grade. Remaining ties are settled alphabetically by name.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from core.models import Ascent, Climb, User


@dataclass(frozen=True)
class Entry:
    """One climber's row: their rank, max grade and the climbs sent at that grade."""

    rank: int
    user: User
    max_grade: int
    top_climbs: tuple[Climb, ...]  # distinct climbs at max_grade

    @property
    def count(self) -> int:
        return len(self.top_climbs)

    @property
    def count_label(self) -> str:
        return f"{self.count} {'climb' if self.count == 1 else 'climbs'}"

    def climbs_label(self, section_names: Mapping[str, str]) -> str:
        """The top climbs, e.g. "Section 1 Yellow holds, Section 4 Green holds"."""
        return ", ".join(
            sorted(f"{section_names.get(c.section_id, '?')} {c.title}" for c in self.top_climbs)
        )


@dataclass(frozen=True)
class Tier:
    """All climbers whose hardest send is `grade`, best first."""

    grade: int
    entries: tuple[Entry, ...]

    @property
    def label(self) -> str:
        return f"V{self.grade}"


def build_leaderboard(
    users: Iterable[User],
    ascents: Iterable[Ascent],
    get_climb: Callable[[str], Climb | None],
) -> list[Tier]:
    """Tiers from hardest to easiest. Climbers without ascents are left out.

    Every ascent style counts as a send. Repeats of the same climb count once, and
    ascents of climbs that no longer exist are ignored.
    """
    sent: dict[str, dict[str, Climb]] = defaultdict(dict)  # user id -> climb id -> climb
    for ascent in ascents:
        climb = get_climb(ascent.climb_id)
        if climb is not None:
            sent[ascent.user_id][climb.id] = climb

    rows: list[tuple[User, int, tuple[Climb, ...]]] = []
    for user in users:
        climbs = sent.get(user.id)
        if not climbs:
            continue
        max_grade = max(c.grade for c in climbs.values())
        top = sorted((c for c in climbs.values() if c.grade == max_grade), key=lambda c: c.id)
        rows.append((user, max_grade, tuple(top)))

    # Hardest grade first, then most climbs at it, then name (id keeps the order stable).
    rows.sort(key=lambda r: (-r[1], -len(r[2]), r[0].display_name.casefold(), r[0].id))

    tiers: list[Tier] = []
    current: list[Entry] = []
    for rank, (user, max_grade, top) in enumerate(rows, start=1):
        if current and current[0].max_grade != max_grade:
            tiers.append(Tier(current[0].max_grade, tuple(current)))
            current = []
        current.append(Entry(rank, user, max_grade, top))
    if current:
        tiers.append(Tier(current[0].max_grade, tuple(current)))
    return tiers
