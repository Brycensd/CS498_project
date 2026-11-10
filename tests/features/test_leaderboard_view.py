"""The leaderboard view over the seeded data, checked without a UI."""

from dataclasses import replace

import flet as ft

from core.memory_repo import InMemoryAscentRepository
from features.leaderboard import view


def rows(root: ft.ListView) -> list[str]:
    """Tier headers as "# V8" and climber tiles as their name, in display order."""
    out = []
    for control in root.controls:
        if isinstance(control, ft.ListTile):
            out.append(control.title.value)
        else:
            out.append("# " + control.content.controls[0].value)
    return out


def test_seeded_leaderboard_is_tiered_and_ranked(ctx):
    assert rows(view.build_view(ctx)) == [
        "# V8",
        "Daniel Woods (you)",
        "Leo Park",
        "Maya Chen",
        "# V7",
        "Ana Ruiz",
        "Ben Okafor",
        "# V6",
        "Chris Dunn",
        "# V5",
        "Dana Fox",
        "Fay Lin",
        "# V3",
        "Eli Grant",
        "# V0",
        "Gus Moreno",
    ]


def test_tiles_show_rank_count_and_climbs(ctx):
    tiles = [c for c in view.build_view(ctx).controls if isinstance(c, ft.ListTile)]
    me = next(t for t in tiles if t.title.value.endswith("(you)"))

    assert [t.leading.content.value for t in tiles] == [str(n) for n in range(1, len(tiles) + 1)]
    assert me.trailing.value == "2 climbs"
    assert me.subtitle.value == "Section 1 Yellow holds, Section 4 Green holds"


def test_empty_leaderboard_shows_message(ctx):
    ctx.repos = replace(ctx.repos, ascents=InMemoryAscentRepository())
    assert view.build_view(ctx).content.value == "No ascents logged yet"
