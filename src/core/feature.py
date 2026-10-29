from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from core.context import AppContext


@dataclass(frozen=True)
class Feature:
    """What a feature package exposes as FEATURE in its __init__.py."""

    id: str
    title: str  # tab label
    icon: ft.IconData  # e.g. ft.Icons.TERRAIN
    build_view: Callable[[AppContext], ft.Control]
    order: int = 100  # tab position; lower comes first, ties sorted by title
