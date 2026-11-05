"""Browse the gym: section list -> section wall photo and climbs -> climb details."""

import flet as ft

from core.feature import Feature

from .view import build_view, setup

FEATURE = Feature(
    id="sections",
    title="Sections",
    icon=ft.Icons.TERRAIN,
    build_view=build_view,
    order=10,
    setup=setup,
)
