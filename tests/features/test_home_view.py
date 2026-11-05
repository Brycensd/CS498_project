"""Home page content, checked without a UI."""

from dataclasses import replace

import flet as ft

from core.memory_repo import InMemoryNewsRepository
from core.models import User
from features.home import view


def texts(control: ft.Control) -> list[str]:
    """All Text values under a control (depth-first)."""
    found = []
    if isinstance(control, ft.Text):
        found.append(control.value)
    for attr in ("content", "controls"):
        child = getattr(control, attr, None)
        for c in child if isinstance(child, list) else [child]:
            if isinstance(c, ft.Control):
                found.extend(texts(c))
    return found


def test_header_stacks_name_then_picture_then_hardest_send(ctx):
    header = view.build_view(ctx).controls[0]

    name, picture, send = header.controls
    assert name.value == "Daniel Woods"
    assert isinstance(picture, ft.CircleAvatar)
    assert picture.foreground_image_src == "avatars/daniel_woods.png"
    assert texts(send) == ["Hardest send", "V8"]


def test_news_shows_the_anniversary_post(ctx):
    shown = texts(view.build_view(ctx))
    assert "News" in shown
    assert "Anniversary Party" in shown
    assert "Saturday, Nov 7" in shown


def test_new_climber_without_picture_or_sends(ctx):
    ctx.current_user = User("u2", "New Climber")

    header = view.build_view(ctx).controls[0]

    picture = header.controls[1]
    assert picture.foreground_image_src is None
    assert picture.content.value == "NC"
    assert "No sends yet" in texts(header)


def test_no_news_shows_message(ctx):
    ctx.repos = replace(ctx.repos, news=InMemoryNewsRepository([]))
    assert texts(view.build_view(ctx))[-1] == "No news yet"


def test_no_signed_in_user_shows_only_news(ctx):
    ctx.current_user = None
    assert view.build_view(ctx).controls[0].value == "News"
