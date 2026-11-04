"""Section list, section screen (wall photo + filterable climbs) and climb detail screen."""

from __future__ import annotations

import flet as ft

from core.context import AppContext
from core.models import Climb, Section, TagColor

from . import logic

ALL_COLORS = "all"


def build_view(ctx: AppContext) -> ft.Control:
    repo = ctx.repos.climbs
    tiles = []
    for section in repo.list_sections():
        climbs = repo.list_climbs(section.id)
        tiles.append(
            ft.ListTile(
                leading=ft.CircleAvatar(content=ft.Text(str(section.number))),
                title=ft.Text(section.name),
                subtitle=ft.Text(logic.section_summary(climbs)),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                on_click=lambda _e, s=section: open_section(ctx, s),
            )
        )
    return ft.ListView(expand=True, controls=tiles)


def open_section(ctx: AppContext, section: Section) -> SectionScreen:
    screen = SectionScreen(ctx, section)
    ctx.nav.push(section.name, screen.control)
    return screen


def open_climb(ctx: AppContext, climb: Climb) -> None:
    section = ctx.repos.climbs.get_section(climb.section_id)
    # Label first, value after it on the same line: "Proposed grade      V5".
    rows = [
        ft.ListTile(title=ft.Text(label), trailing=ft.Text(value, size=16))
        for label, value in logic.climb_details(climb, section)
    ]
    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        content=ft.Row(
            [
                tag_chip(climb.tag, height=24),
                ft.Text(climb.title, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ]
        ),
    )
    ctx.nav.push(
        climb.title, ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[header, *rows])
    )


class SectionScreen:
    """Wall photo, sort/color controls and the matching climbs for one section."""

    def __init__(self, ctx: AppContext, section: Section) -> None:
        self._ctx = ctx
        self._climbs = ctx.repos.climbs.list_climbs(section.id)

        self.sort_dropdown = ft.Dropdown(
            label="Sort",
            expand=True,
            value=logic.SortOrder.GRADE_ASC,
            options=[
                ft.DropdownOption(key=o, text=label) for o, label in logic.SORT_LABELS.items()
            ],
            on_select=lambda _e: self.refresh(),
        )
        self.hold_color_dropdown = ft.Dropdown(
            label="Hold color",
            expand=True,
            value=ALL_COLORS,
            options=[ft.DropdownOption(key=ALL_COLORS, text="All colors")]
            + [ft.DropdownOption(key=c, text=c) for c in logic.available_hold_colors(self._climbs)],
            on_select=lambda _e: self.refresh(),
        )
        self.climb_list = ft.Column(spacing=0)
        self.control = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                wall_photo(section),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Row([self.sort_dropdown, self.hold_color_dropdown]),
                ),
                self.climb_list,
            ],
        )
        self.refresh()

    def visible_climbs(self) -> list[Climb]:
        color = self.hold_color_dropdown.value
        colors = frozenset() if color in (None, ALL_COLORS) else frozenset({color})
        matching = logic.filter_climbs(self._climbs, logic.ClimbFilter(hold_colors=colors))
        return logic.sort_climbs(matching, logic.SortOrder(self.sort_dropdown.value))

    def refresh(self) -> None:
        # Called from dropdown handlers; Flet re-renders automatically after a handler.
        climbs = self.visible_climbs()
        self.climb_list.controls = [self._climb_tile(c) for c in climbs] or [
            ft.ListTile(title=ft.Text("No climbs match these filters"))
        ]

    def _climb_tile(self, climb: Climb) -> ft.Control:
        return ft.ListTile(
            leading=tag_chip(climb.tag),
            title=ft.Text(climb.title),
            subtitle=ft.Text(logic.climb_subtitle(climb)),
            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
            on_click=lambda _e, c=climb: open_climb(self._ctx, c),
        )


WALL_PHOTO_HEIGHT = 220


def wall_photo(section: Section) -> ft.Control:
    placeholder = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=48),
    )
    content = placeholder
    if section.wall_image:
        content = ft.Image(
            src=section.wall_image,
            expand=True,
            height=WALL_PHOTO_HEIGHT,
            fit=ft.BoxFit.COVER,
            semantics_label=f"{section.name} wall",
            error_content=placeholder,
        )
    return ft.Container(
        height=WALL_PHOTO_HEIGHT,
        margin=ft.Margin.symmetric(horizontal=16),
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        # An expanded child of a Row gets the full width, so COVER fills the box on any
        # screen size instead of keeping the image's natural width.
        content=ft.Row([content], spacing=0),
    )


# On-screen color for each tag. Adjust a shade here to better match the physical tags.
TAG_SWATCHES: dict[TagColor, ft.Colors] = {
    TagColor.RED: ft.Colors.RED,
    TagColor.YELLOW: ft.Colors.YELLOW,
    TagColor.GREEN: ft.Colors.GREEN,
    TagColor.WHITE: ft.Colors.WHITE,
    TagColor.BLUE: ft.Colors.BLUE,
    TagColor.BLACK: ft.Colors.BLACK,
    TagColor.PURPLE: ft.Colors.PURPLE_800,  # darker than Material's default purple
    TagColor.ORANGE: ft.Colors.ORANGE,
    TagColor.PINK: ft.Colors.PINK,
}


def tag_chip(tag: TagColor, height: int = 18) -> ft.Control:
    """A small rectangle in the climb's difficulty-tag color, like the physical tag."""
    return ft.Container(
        width=height * 1.6,
        height=height,
        border_radius=4,
        bgcolor=TAG_SWATCHES[tag],
        # The outline keeps black and white tags visible on dark and light themes.
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        tooltip=f"{tag} tag ({tag.range_label})",
    )
