"""Starting point for a new feature. Packages starting with "_" are not loaded.

To create a feature:
  1. Copy this folder to src/features/<your_feature>/ (lowercase, underscores).
     It shows up as a new tab immediately - no changes to src/core/ needed.
  2. Set TITLE, ICON and ORDER below. The id defaults to the folder name.
  3. Put rules and data shaping in logic.py (no flet imports) and test it in
     tests/features/test_<your_feature>_logic.py.
  4. Build the UI in view.py from ctx (repositories, events, navigation, current user).

Rules: never import another feature, never change page layout or page.navigation_bar,
use ctx.nav.push(...) for detail screens and ctx.show_message(...) for snackbars.
"""

import flet as ft

from core.feature import Feature

from .view import build_view

# The folder name, e.g. "features.ascents" -> "ascents". Keeps ids unique without edits.
FEATURE_ID = __name__.rsplit(".", 1)[-1]
TITLE = FEATURE_ID.replace("_", " ").strip().title()
ICON = ft.Icons.EXTENSION
ORDER = 100

FEATURE = Feature(id=FEATURE_ID, title=TITLE, icon=ICON, build_view=build_view, order=ORDER)
