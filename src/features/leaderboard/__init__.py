"""Leaderboard: climbers in tiers by hardest grade sent, ranked by climbs at that grade."""

import flet as ft

from core.feature import Feature

from .view import build_view

FEATURE = Feature(
    id="leaderboard",
    title="Leaderboard",
    icon=ft.Icons.LEADERBOARD,
    build_view=build_view,
    order=30,
)
