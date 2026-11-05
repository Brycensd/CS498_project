"""Core navigation and shell behavior, using a minimal stand-in for ft.Page."""

import flet as ft
import pytest

from core.feature import Feature
from core.navigation import PageNavigator
from core.registry import LoadError
from core.shell import AppShell


class FakePage:
    """Just the parts of ft.Page that the shell and navigator use."""

    def __init__(self) -> None:
        self.views = [ft.View()]
        self.on_view_pop = None
        self.updates = 0

    def update(self) -> None:
        self.updates += 1


def feature(fid: str, build=lambda ctx: ft.Text("ok"), setup=None) -> Feature:
    return Feature(id=fid, title=fid.title(), icon=ft.Icons.STAR, build_view=build, setup=setup)


def test_push_and_pop():
    page = FakePage()
    nav = PageNavigator(page)

    nav.push("Detail", ft.Text("x"))
    nav.push("Deeper", ft.Text("y"))
    assert nav.depth == 2
    assert page.views[-1].appbar.title.value == "Deeper"
    assert page.views[1].route != page.views[2].route

    nav.pop()
    nav.pop()
    nav.pop()  # popping at the root does nothing
    assert nav.depth == 0


def test_back_button_removes_the_popped_view_but_never_the_root():
    page = FakePage()
    nav = PageNavigator(page)
    nav.push("Detail", ft.Text("x"))
    top = page.views[-1]

    page.on_view_pop(ft.ViewPopEvent(name="view_pop", control=page, route=top.route, view=top))
    assert nav.depth == 0

    root = page.views[0]
    page.on_view_pop(ft.ViewPopEvent(name="view_pop", control=page, route="/", view=root))
    assert page.views == [root]


@pytest.mark.parametrize("count", [0, 1, 2, 3])
def test_navigation_bar_only_with_two_or_more_features(ctx, count):
    page = FakePage()
    AppShell(page, ctx, [feature(f"f{i}") for i in range(count)]).mount()

    bar = page.views[0].navigation_bar
    if count >= 2:
        assert len(bar.destinations) == count
    else:
        assert bar is None


def test_no_features_shows_load_errors(ctx):
    page = FakePage()
    shell = AppShell(page, ctx, [], [LoadError("features.x", "boom")])
    shell.mount()
    assert "features.x: boom" in _texts(shell._body.content)


def test_feature_that_crashes_while_building_shows_error_panel(ctx):
    def crash(_ctx):
        raise RuntimeError("kaput")

    page = FakePage()
    shell = AppShell(page, ctx, [feature("good"), feature("bad", crash)])
    shell.mount()

    shell.show_tab(1)
    texts = _texts(shell._body.content)
    assert any("kaput" in t for t in texts)

    shell.show_tab(0)  # the rest of the app still works
    assert _texts(shell._body.content) == ["ok"]


def test_every_feature_is_set_up_once_before_the_first_view_is_built(ctx):
    calls = []

    def build(_ctx):
        calls.append("build")
        return ft.Text("ok")

    page = FakePage()
    shell = AppShell(
        page,
        ctx,
        [
            feature("first", build, setup=lambda _ctx: calls.append("setup first")),
            feature("second", setup=lambda _ctx: calls.append("setup second")),
            feature("plain"),  # no setup hook
        ],
    )
    shell.mount()
    shell.show_tab(0)

    # The second tab was never opened but was still set up; tab switches don't set up again.
    assert calls == ["setup first", "setup second", "build", "build"]


def test_feature_that_crashes_during_setup_does_not_stop_the_others(ctx):
    def crash(_ctx):
        raise RuntimeError("kaput")

    set_up = []
    page = FakePage()
    shell = AppShell(
        page,
        ctx,
        [feature("bad", setup=crash), feature("good", setup=lambda _ctx: set_up.append(1))],
    )
    shell.mount()

    assert set_up == [1]
    assert _texts(shell._body.content) == ["ok"]  # the broken feature's tab still shows


def _texts(control: ft.Control) -> list[str]:
    """All Text values under a control (depth-first)."""
    found = []
    if isinstance(control, ft.Text):
        found.append(control.value)
    for attr in ("content", "controls"):
        child = getattr(control, attr, None)
        for c in child if isinstance(child, list) else [child]:
            if isinstance(c, ft.Control):
                found.extend(_texts(c))
    return found
