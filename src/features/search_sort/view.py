"""Search box, sort dropdown, matching climbs from every section and a climb detail screen."""

from __future__ import annotations

import flet as ft

from core.context import AppContext
from core.models import Climb

from . import logic


def build_view(ctx: AppContext) -> ft.Control:
    return SearchScreen(ctx).control


class SearchScreen:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._climbs = ctx.repos.climbs.list_climbs()
        self._sections = {s.id: s for s in ctx.repos.climbs.list_sections()}

        self.search_box = ft.TextField(
            hint_text="Search climbs",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            on_change=lambda _e: self.refresh(),
        )
        self.sort_dropdown = ft.Dropdown(
            label="Sort",
            width=140,
            value=logic.SortOrder.GRADE_ASC,
            options=[
                ft.DropdownOption(key=o, text=label) for o, label in logic.SORT_LABELS.items()
            ],
            on_select=lambda _e: self.refresh(),
        )
        self.results = ft.ListView(expand=True)
        self.control = ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Row([self.search_box, self.sort_dropdown]),
                ),
                self.results,
            ],
        )
        self.refresh()

    def visible_climbs(self) -> list[Climb]:
        return logic.search_climbs(
            self._climbs,
            self.search_box.value or "",
            logic.SortOrder(self.sort_dropdown.value),
            self._sections,
        )

    def refresh(self) -> None:
        # Called from input handlers; Flet re-renders automatically after a handler.
        self.results.controls = [self._climb_tile(c) for c in self.visible_climbs()] or [
            ft.ListTile(title=ft.Text("No climbs match your search"))
        ]

    def _climb_tile(self, climb: Climb) -> ft.Control:
        section = self._sections[climb.section_id]
        return ft.ListTile(
            title=ft.Text(climb.title),
            subtitle=ft.Text(logic.result_subtitle(climb, section)),
            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
            on_click=lambda _e, c=climb: self._open_climb(c),
        )

    def _open_climb(self, climb: Climb) -> None:
        # Features can't import each other, so this can't reuse the sections detail screen.
        rows = [
            ft.ListTile(title=ft.Text(label), trailing=ft.Text(value, size=16))
            for label, value in logic.climb_details(climb, self._sections[climb.section_id])
        ]
        self._ctx.nav.push(
            climb.title, ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=rows)
        )
