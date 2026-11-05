"""The app shell: owns the Page, the NavigationBar and the body area features render into."""

from __future__ import annotations

import logging

import flet as ft

from core.context import AppContext
from core.feature import Feature
from core.navigation import ROOT_ROUTE
from core.registry import LoadError

log = logging.getLogger(__name__)


def run_feature_setup(feature: Feature, ctx: AppContext) -> None:
    """Run a feature's optional startup hook, logging a crash instead of raising.

    A failed setup only loses what that hook did (e.g. an event subscription); the feature's
    tab is still shown, and build_view reports its own errors.
    """
    if feature.setup is None:
        return
    try:
        feature.setup(ctx)
    except Exception:
        log.exception("Feature %r failed to set up", feature.id)


def build_feature_view(feature: Feature, ctx: AppContext) -> ft.Control:
    """Build a feature's view, replacing a crash with an error panel."""
    try:
        return feature.build_view(ctx)
    except Exception as exc:
        log.exception("Feature %r failed to build its view", feature.id)
        return error_panel(f"{feature.title} failed to load", f"{type(exc).__name__}: {exc}")


def error_panel(title: str, detail: str) -> ft.Control:
    return ft.Container(
        padding=24,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.ERROR, size=40),
                ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(detail, selectable=True),
            ]
        ),
    )


class AppShell:
    def __init__(
        self,
        page: ft.Page,
        ctx: AppContext,
        features: list[Feature],
        load_errors: list[LoadError] | None = None,
    ) -> None:
        self._page = page
        self._ctx = ctx
        self._features = features
        self._load_errors = load_errors or []
        self._body = ft.Container(expand=True)

    def mount(self) -> None:
        root = self._page.views[0]
        root.route = ROOT_ROUTE
        root.padding = 0
        root.controls = [ft.SafeArea(expand=True, content=self._body)]

        for feature in self._features:
            run_feature_setup(feature, self._ctx)

        # Flutter's NavigationBar needs at least 2 destinations, so with a single
        # feature we skip the bar and let that feature fill the page.
        if len(self._features) >= 2:
            root.navigation_bar = ft.NavigationBar(
                selected_index=0,
                destinations=[
                    ft.NavigationBarDestination(icon=f.icon, label=f.title) for f in self._features
                ],
                on_change=self._on_tab_change,
            )

        if self._features:
            self.show_tab(0)
        else:
            details = "\n".join(f"{e.module}: {e.message}" for e in self._load_errors)
            self._body.content = error_panel("No features installed", details)
        self._page.update()

    def show_tab(self, index: int) -> None:
        # Rebuild on every switch so the view always reflects current repository data.
        self._body.content = build_feature_view(self._features[index], self._ctx)

    def _on_tab_change(self, e: ft.Event[ft.NavigationBar]) -> None:
        self.show_tab(e.control.selected_index)
