"""Profile summary and news text for the home page. No flet imports."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from core.models import Ascent, Climb, NewsPost


def hardest_send(ascents: Iterable[Ascent], climbs: Mapping[str, Climb]) -> Climb | None:
    """The highest-graded climb among the ascents, or None if there are none.

    Every ascent style (flash, send, repeat) counts as a send. Ascents of climbs missing
    from `climbs` (e.g. taken down when a wall is reset) are ignored.
    """
    sent = [climbs[a.climb_id] for a in ascents if a.climb_id in climbs]
    return max(sent, key=lambda c: c.grade, default=None)


def hardest_send_label(climb: Climb | None) -> str:
    return climb.grade_label if climb is not None else "No sends yet"


def initials(name: str) -> str:
    """Up to two initials for when there is no profile picture, e.g. "Daniel Woods" -> "DW"."""
    words = name.split()
    if not words:
        return "?"
    first, last = words[0], words[-1]
    return (first[0] + (last[0] if len(words) > 1 else "")).upper()


def event_label(post: NewsPost) -> str | None:
    """When the announced event happens, e.g. "Saturday, Nov 7", or None for plain news."""
    day = post.event_on
    if day is None:
        return None
    # Day of month added separately because "%-d" (no leading zero) doesn't work on Windows.
    return f"{day:%A, %b} {day.day}"


def posted_label(post: NewsPost) -> str:
    """E.g. "Posted Nov 1"."""
    return f"Posted {post.posted_at:%b} {post.posted_at.day}"
