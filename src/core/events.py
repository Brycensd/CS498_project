"""Publish/subscribe bus for notifications between features.

Events are plain objects (usually frozen dataclasses) and are dispatched by their exact
type. Event types that more than one feature uses belong in this module so features
never import each other.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

log = logging.getLogger(__name__)

E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class SectionRequested:
    """Ask for a section's page to be opened. The sections feature handles this."""

    section_id: str


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> Callable[[], None]:
        """Register handler for event_type. Returns a function that unsubscribes it."""
        self._handlers[event_type].append(handler)

        def unsubscribe() -> None:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

        return unsubscribe

    def publish(self, event: object) -> None:
        # Copy so handlers may unsubscribe while being called. A failing handler is
        # logged and skipped so one broken feature can't block the others.
        for handler in list(self._handlers.get(type(event), [])):
            try:
                handler(event)
            except Exception:
                log.exception("Event handler %r failed for %r", handler, event)
