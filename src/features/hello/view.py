import flet as ft

from core.context import AppContext

from . import logic


def build_view(ctx: AppContext) -> ft.Control:
    repo = ctx.repos.climbs
    rows = logic.section_rows(repo.list_sections(), repo.list_climbs())
    name = ctx.current_user.display_name if ctx.current_user else "climber"
    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                padding=16,
                content=ft.Text(
                    f"Hello, {name}! Welcome to {repo.get_gym().name}.",
                    theme_style=ft.TextThemeStyle.TITLE_LARGE,
                ),
            ),
            ft.ListView(
                expand=True,
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.TERRAIN),
                        title=ft.Text(title),
                        subtitle=ft.Text(subtitle),
                    )
                    for title, subtitle in rows
                ],
            ),
        ],
    )
