"""Demo feature proving the pipeline: repository -> logic -> view -> tab."""

import flet as ft

from core.feature import Feature

from .view import build_view

FEATURE = Feature(id="hello", title="Hello", icon=ft.Icons.WAVING_HAND, build_view=build_view)
