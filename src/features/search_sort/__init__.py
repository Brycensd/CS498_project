"""Search every climb in the gym by text and sort the results by grade or section."""

import flet as ft

from core.feature import Feature

from .view import build_view

FEATURE = Feature(
    id="search_sort",
    title="Search",
    icon=ft.Icons.SEARCH,
    build_view=build_view,
    order=20,
)
