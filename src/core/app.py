"""Wires repositories, context, features and the shell together."""

from __future__ import annotations

import logging

import flet as ft

from core.context import AppContext
from core.events import EventBus
from core.memory_repo import DEMO_USER_ID, seed_repositories
from core.navigation import PageNavigator
from core.registry import discover_features
from core.shell import AppShell

APP_TITLE = "Climbing Gym"


def main(page: ft.Page) -> None:
    logging.basicConfig(level=logging.INFO)
    page.title = APP_TITLE
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)

    repos = seed_repositories()
    ctx = AppContext(
        repos=repos,
        events=EventBus(),
        nav=PageNavigator(page),
        current_user=repos.users.get(DEMO_USER_ID),
        page=page,
    )
    features, errors = discover_features()
    AppShell(page, ctx, features, errors).mount()
