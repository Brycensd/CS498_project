"""UI for this feature. build_view(ctx) returns one control; the shell places it."""

import flet as ft

from core.context import AppContext

from . import logic


def build_view(ctx: AppContext) -> ft.Control:
    sections = ctx.repos.climbs.list_sections()
    return ft.Container(
        padding=16,
        content=ft.Column(
            [
                ft.Text("New feature", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text(logic.describe(sections)),
            ]
        ),
    )
