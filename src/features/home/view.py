"""Home page UI: profile header (name, picture, hardest send) above the news posts."""

from __future__ import annotations

import flet as ft

from core.context import AppContext
from core.events import ProfileRequested, ProfileUpdated
from core.models import NewsPost, User

from . import logic

AVATAR_RADIUS = 56

# The header of the most recently built home view. The ProfileUpdated handler redraws it so
# edits made on the profile screen show as soon as the user comes back.
_header: ft.Column | None = None


def setup(ctx: AppContext) -> None:
    ctx.events.subscribe(ProfileUpdated, lambda _event: refresh_header(ctx))


def refresh_header(ctx: AppContext) -> None:
    if _header is not None and ctx.current_user is not None:
        _header.controls = profile_header(ctx, ctx.current_user).controls


def build_view(ctx: AppContext) -> ft.Control:
    global _header
    controls: list[ft.Control] = []
    _header = None
    if ctx.current_user is not None:
        _header = profile_header(ctx, ctx.current_user)
        controls.append(_header)
    controls.append(ft.Text("News", theme_style=ft.TextThemeStyle.TITLE_LARGE))
    posts = ctx.repos.news.list_posts()
    controls.extend([news_card(p) for p in posts] or [ft.Text("No news yet")])
    return ft.ListView(expand=True, padding=16, spacing=12, controls=controls)


def profile_header(ctx: AppContext, user: User) -> ft.Column:
    """Name, picture, hardest send and a View profile button, stacked and centered."""
    climbs = {c.id: c for c in ctx.repos.climbs.list_climbs()}
    best = logic.hardest_send(ctx.repos.ascents.list_for_user(user.id), climbs)
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.Text(user.display_name, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            avatar(user),
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    ft.Text(
                        "Hardest send",
                        theme_style=ft.TextThemeStyle.LABEL_LARGE,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Text(
                        logic.hardest_send_label(best),
                        theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    ),
                ],
            ),
            # Opened by the profile feature, which subscribes to ProfileRequested.
            ft.OutlinedButton(
                "View profile",
                icon=ft.Icons.PERSON,
                on_click=lambda _e: ctx.events.publish(ProfileRequested(user.id)),
            ),
        ],
    )


def avatar(user: User) -> ft.CircleAvatar:
    # The initials sit behind the picture, so they show when there is no picture or it
    # fails to load.
    return ft.CircleAvatar(
        radius=AVATAR_RADIUS,
        foreground_image_src=user.avatar,
        content=ft.Text(logic.initials(user.display_name), size=AVATAR_RADIUS * 0.6),
    )


def news_card(post: NewsPost) -> ft.Control:
    lines: list[ft.Control] = [ft.Text(post.title, theme_style=ft.TextThemeStyle.TITLE_MEDIUM)]
    event = logic.event_label(post)
    if event is not None:
        lines.append(ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.EVENT, size=18), ft.Text(event)]))
    lines += [
        ft.Text(post.body),
        ft.Text(
            logic.posted_label(post),
            theme_style=ft.TextThemeStyle.LABEL_SMALL,
            color=ft.Colors.ON_SURFACE_VARIANT,
        ),
    ]
    return ft.Card(content=ft.Container(padding=16, content=ft.Column(spacing=8, controls=lines)))
