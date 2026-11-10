from __future__ import annotations

from dataclasses import dataclass

import flet as ft

from core.events import EventBus
from core.models import User
from core.navigation import Navigator
from core.repositories import Repositories


@dataclass
class AppContext:
    """Everything a feature may use. Passed to Feature.build_view."""

    repos: Repositories
    events: EventBus
    nav: Navigator
    current_user: User | None = None
    # None in tests. Features should prefer the helpers below over using the page directly.
    page: ft.Page | None = None

    def show_message(self, text: str) -> None:
        """Show a short snackbar message. No-op when there is no page (tests)."""
        if self.page is not None:
            self.page.show_dialog(ft.SnackBar(content=ft.Text(text)))
            # show_dialog updates only the snackbar, and any explicit update makes Flet skip
            # its automatic update after the event handler. Update the whole page so changes
            # the handler made before showing the message are still sent.
            self.page.update()
