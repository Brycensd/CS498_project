"""Leaderboard list: a header per grade tier followed by that tier's climbers."""

from __future__ import annotations

from collections.abc import Mapping

import flet as ft

from core.context import AppContext

from . import logic


def build_view(ctx: AppContext) -> ft.Control:
    # Rebuilt on every tab switch by the shell, so newly logged ascents show up.
    users = ctx.repos.users.list_users()
    ascents = [a for u in users for a in ctx.repos.ascents.list_for_user(u.id)]
    tiers = logic.build_leaderboard(users, ascents, ctx.repos.climbs.get_climb)
    if not tiers:
        return ft.Container(padding=24, content=ft.Text("No ascents logged yet"))

    me = ctx.current_user.id if ctx.current_user else None
    section_names = {s.id: s.name for s in ctx.repos.climbs.list_sections()}
    controls: list[ft.Control] = []
    for tier in tiers:
        controls.append(tier_header(tier))
        controls.extend(entry_tile(e, section_names, is_me=e.user.id == me) for e in tier.entries)
    return ft.ListView(expand=True, controls=controls)


def tier_header(tier: logic.Tier) -> ft.Control:
    noun = "climber" if len(tier.entries) == 1 else "climbers"
    return ft.Container(
        padding=ft.Padding.only(left=16, right=16, top=16, bottom=4),
        content=ft.Row(
            [
                ft.Text(tier.label, theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Text(f"{len(tier.entries)} {noun}", color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )


def entry_tile(
    entry: logic.Entry, section_names: Mapping[str, str], is_me: bool = False
) -> ft.ListTile:
    name = f"{entry.user.display_name} (you)" if is_me else entry.user.display_name
    return ft.ListTile(
        leading=ft.CircleAvatar(content=ft.Text(str(entry.rank))),
        title=ft.Text(name, weight=ft.FontWeight.BOLD if is_me else None),
        subtitle=ft.Text(entry.climbs_label(section_names)),
        trailing=ft.Text(entry.count_label),
        bgcolor=ft.Colors.SECONDARY_CONTAINER if is_me else None,
    )
