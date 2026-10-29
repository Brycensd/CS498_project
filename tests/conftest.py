import pytest

from core.context import AppContext
from core.events import EventBus
from core.memory_repo import DEMO_USER_ID, seed_repositories
from core.navigation import RecordingNavigator


@pytest.fixture
def ctx() -> AppContext:
    """A fresh app context without a UI: seeded repos, real event bus, recording navigator."""
    repos = seed_repositories()
    return AppContext(
        repos=repos,
        events=EventBus(),
        nav=RecordingNavigator(),
        current_user=repos.users.get(DEMO_USER_ID),
        page=None,
    )
