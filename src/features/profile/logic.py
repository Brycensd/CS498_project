"""Profile page rules: top send, send history, climb choices and profile edits. No flet imports."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime

from core.models import Ascent, AscentStyle, Climb, Section, User, new_id

MAX_NAME_LENGTH = 40
MAX_BIO_LENGTH = 160

STYLE_LABELS: dict[AscentStyle, str] = {
    AscentStyle.FLASH: "Flash",
    AscentStyle.SEND: "Send",
    AscentStyle.REPEAT: "Repeat",
}


@dataclass(frozen=True)
class Send:
    """One logged ascent together with the climb it was on."""

    ascent: Ascent
    climb: Climb


def sends(ascents: Iterable[Ascent], get_climb: Callable[[str], Climb | None]) -> list[Send]:
    """The ascents newest first, skipping climbs that no longer exist (e.g. after a reset)."""
    found = []
    for ascent in ascents:
        climb = get_climb(ascent.climb_id)
        if climb is not None:
            found.append(Send(ascent, climb))
    return sorted(found, key=lambda s: s.ascent.climbed_at, reverse=True)


def top_send(history: Iterable[Send]) -> Send | None:
    """The highest-graded send; on a tie, the earliest one (when that grade was first reached).

    Every ascent style (flash, send, repeat) counts, as on the home page.
    """
    return min(history, key=lambda s: (-s.climb.grade, s.ascent.climbed_at), default=None)


def climb_label(climb: Climb, section_names: Mapping[str, str]) -> str:
    """E.g. "Section 1 · Yellow holds · V8"."""
    section = section_names.get(climb.section_id, "?")
    return f"{section} · {climb.title} · {climb.grade_label}"


def send_label(send: Send) -> str:
    """E.g. "Flash · Oct 3"."""
    day = send.ascent.climbed_at
    # Day of month added separately because "%-d" (no leading zero) doesn't work on Windows.
    return f"{STYLE_LABELS[send.ascent.style]} · {day:%b} {day.day}"


def climb_choices(climbs: Iterable[Climb], sections: Iterable[Section]) -> list[tuple[str, str]]:
    """(climb id, label) pairs for the "log a climb" picker, by section then grade."""
    numbers = {s.id: s.number for s in sections}
    names = {s.id: s.name for s in sections}
    ordered = sorted(climbs, key=lambda c: (numbers.get(c.section_id, 0), c.grade, c.id))
    return [(c.id, f"{climb_label(c, names)} ({c.tag} tag)") for c in ordered]


def new_ascent(user_id: str, climb_id: str, style: AscentStyle, now: datetime) -> Ascent:
    return Ascent(id=new_id(), user_id=user_id, climb_id=climb_id, style=style, climbed_at=now)


class ProfileError(ValueError):
    """A profile edit was rejected. `field` is "name" or "bio"; str(err) is shown to the user."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field


def edit_profile(user: User, name: str, bio: str) -> User:
    """A copy of user with the new name and bio, trimmed. Raises ProfileError if invalid."""
    name = " ".join(name.split())  # trim and collapse runs of spaces
    bio = bio.strip()
    if not name:
        raise ProfileError("name", "Name can't be empty")
    if len(name) > MAX_NAME_LENGTH:
        raise ProfileError("name", f"Name must be at most {MAX_NAME_LENGTH} characters")
    if len(bio) > MAX_BIO_LENGTH:
        raise ProfileError("bio", f"Bio must be at most {MAX_BIO_LENGTH} characters")
    return replace(user, display_name=name, bio=bio)


def initials(name: str) -> str:
    """Up to two initials for when there is no profile picture, e.g. "Daniel Woods" -> "DW"."""
    words = name.split()
    if not words:
        return "?"
    return (words[0][0] + (words[-1][0] if len(words) > 1 else "")).upper()
