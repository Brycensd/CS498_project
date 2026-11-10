"""Home page: the current climber's name, picture and hardest send, then gym news."""

import flet as ft

from core.feature import Feature

from .view import build_view, setup

FEATURE = Feature(
    id="home",
    title="Home",
    icon=ft.Icons.HOME,
    build_view=build_view,
    order=0,
    setup=setup,
)
