"""Drill-down navigation shared by all features.

Each pushed screen is a full-screen ft.View on top of page.views. Flutter draws a back
arrow in its AppBar, and both that arrow and the Android back button fire
page.on_view_pop, which removes the top view. Features only call push()/pop().
"""

from __future__ import annotations

import itertools
from typing import Protocol

import flet as ft

ROOT_ROUTE = "/"


class Navigator(Protocol):
    def push(self, title: str, content: ft.Control) -> None:
        """Show content full-screen with a back button and the given title."""
        ...

    def pop(self) -> None:
        """Close the top screen. Does nothing on the root screen."""
        ...


class PageNavigator:
    def __init__(self, page: ft.Page) -> None:
        self._page = page
        # ViewPopEvent identifies the view by route, so every pushed view needs a unique
        # one. Routes are internal ids only; we don't use them for deep links.
        self._ids = itertools.count(1)
        page.on_view_pop = self._on_view_pop

    @property
    def depth(self) -> int:
        """Number of screens above the root."""
        return len(self._page.views) - 1

    def push(self, title: str, content: ft.Control) -> None:
        self._page.views.append(
            ft.View(
                route=f"/screen/{next(self._ids)}",
                appbar=ft.AppBar(title=ft.Text(title)),
                controls=[content],
            )
        )
        self._page.update()

    def pop(self) -> None:
        if self.depth > 0:
            self._page.views.pop()
            self._page.update()

    def _on_view_pop(self, e: ft.ViewPopEvent) -> None:
        # Never remove the root view; Android back on the root exits the app instead.
        if e.view is not None and e.view is not self._page.views[0]:
            self._page.views.remove(e.view)
            self._page.update()


class RecordingNavigator:
    """Navigator for tests: records pushed screens instead of showing them."""

    def __init__(self) -> None:
        self.stack: list[tuple[str, ft.Control]] = []

    def push(self, title: str, content: ft.Control) -> None:
        self.stack.append((title, content))

    def pop(self) -> None:
        if self.stack:
            self.stack.pop()
