"""Every installed feature must load and build its view without a UI.

This is what makes a broken feature fail CI instead of the app.
"""

import flet as ft
import pytest

from core.registry import discover_features

FEATURES, LOAD_ERRORS = discover_features()


def test_all_features_import():
    assert LOAD_ERRORS == []


@pytest.mark.parametrize("feature", FEATURES, ids=lambda f: f.id)
def test_build_view_returns_a_control(feature, ctx):
    # Call build_view directly (not via the shell) so errors surface instead of being caught.
    view = feature.build_view(ctx)
    assert isinstance(view, ft.Control)
