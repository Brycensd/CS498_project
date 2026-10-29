"""Pure logic for this feature. No flet imports, so it is testable with plain pytest."""

from core.models import Section


def describe(sections: list[Section]) -> str:
    """Example logic: a one-line summary the view can display."""
    return f"{len(sections)} sections in the gym"
