"""Profile page: picture, name and bio (editable), hardest send, logging climbs and send history.

Has no tab of its own: the home page's View profile button opens it through the
ProfileRequested event.
"""

import flet as ft

from core.feature import Feature

from .view import build_view, setup

FEATURE = Feature(
    id="profile",
    title="Profile",
    icon=ft.Icons.PERSON,
    build_view=build_view,
    order=40,
    setup=setup,
    show_tab=False,
)
