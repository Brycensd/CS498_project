"""Profile screen behavior, checked without a UI."""

import flet as ft

from core.events import ProfileRequested, ProfileUpdated
from core.memory_repo import DEMO_USER_ID
from core.models import TagColor, User
from features.profile import logic, view


def texts(control: ft.Control) -> list[str]:
    """All Text values under a control (depth-first), including ListTile parts."""
    found = []
    if isinstance(control, ft.Text):
        found.append(control.value)
    for attr in ("content", "controls", "leading", "title", "subtitle"):
        child = getattr(control, attr, None)
        for c in child if isinstance(child, list) else [child]:
            if isinstance(c, ft.Control):
                found.extend(texts(c))
    return found


def my_screen(ctx) -> view.ProfileScreen:
    return view.ProfileScreen(ctx, ctx.current_user)


def test_shows_name_bio_and_hardest_send(ctx):
    screen = my_screen(ctx)
    header = texts(screen.header)
    assert "Daniel Woods" in header
    assert ctx.current_user.bio in header
    assert screen.edit_button in screen.header.controls
    # The demo user's V8s: s1c5 on Oct 17 comes before s4c2 on Oct 24.
    assert texts(screen.top_send) == ["V8", "Section 1 · Yellow holds", "Send · Oct 17"]
    assert len(screen.history.controls) == 4


def test_grade_badges_use_the_climbs_tag_color(ctx):
    assert set(view.TAG_BADGE_COLORS) == set(TagColor)
    screen = my_screen(ctx)
    history = logic.sends(ctx.repos.ascents.list_for_user(DEMO_USER_ID), ctx.repos.climbs.get_climb)
    for tile, send in zip(screen.history.controls, history, strict=True):
        assert tile.leading.bgcolor == view.TAG_BADGE_COLORS[send.climb.tag][0]
        assert tile.leading.content.value == send.climb.grade_label
    # Top send s1c5 is a Pink-tag V8.
    top = screen.top_send.controls[0].leading
    assert (top.bgcolor, top.content.color) == (ft.Colors.PINK, ft.Colors.WHITE)


def test_edit_and_save_updates_repo_current_user_and_notifies(ctx):
    updates = []
    ctx.events.subscribe(ProfileUpdated, updates.append)
    screen = my_screen(ctx)

    screen.edit_button.on_click(None)
    assert screen.edit_form.visible
    assert screen.edit_button not in screen.header.controls
    assert screen.name_field.value == "Daniel Woods"

    screen.name_field.value = "Dan Woods"
    screen.bio_field.value = "Crimps all day"
    screen.save()

    saved = ctx.repos.users.get(DEMO_USER_ID)
    assert (saved.display_name, saved.bio) == ("Dan Woods", "Crimps all day")
    assert saved.avatar == "avatars/daniel_woods.png"
    assert ctx.current_user == saved
    assert not screen.edit_form.visible
    assert "Dan Woods" in texts(screen.header)
    assert updates == [ProfileUpdated(DEMO_USER_ID)]


def test_invalid_name_shows_error_and_saves_nothing(ctx):
    screen = my_screen(ctx)
    screen.start_editing()
    screen.name_field.value = "   "
    screen.save()

    assert screen.name_field.error == "Name can't be empty"
    assert screen.edit_form.visible
    assert ctx.repos.users.get(DEMO_USER_ID).display_name == "Daniel Woods"


def test_cancel_discards_changes(ctx):
    screen = my_screen(ctx)
    screen.start_editing()
    screen.name_field.value = "Someone Else"
    screen.stop_editing()
    assert ctx.current_user.display_name == "Daniel Woods"
    assert not screen.edit_form.visible


def test_log_climb_adds_ascent_and_refreshes(ctx):
    updates = []
    ctx.events.subscribe(ProfileUpdated, updates.append)
    screen = my_screen(ctx)

    screen.climb_dropdown.value = "s1c1"
    screen.style_dropdown.value = "flash"
    screen.log_button.on_click(None)

    mine = ctx.repos.ascents.list_for_user(DEMO_USER_ID)
    assert len(mine) == 5
    assert mine[-1].climb_id == "s1c1" and mine[-1].style == "flash"
    assert len(screen.history.controls) == 5
    assert texts(screen.history.controls[0])[:2] == ["V0", "Section 1 · Red holds"]
    assert screen.climb_dropdown.value is None
    assert updates == [ProfileUpdated(DEMO_USER_ID)]


def test_log_without_a_climb_shows_error(ctx):
    screen = my_screen(ctx)
    screen.log_climb()
    assert screen.climb_dropdown.error_text == "Choose a climb"
    assert len(ctx.repos.ascents.list_for_user(DEMO_USER_ID)) == 4


def test_new_climber_sees_empty_states(ctx):
    ctx.current_user = User("new", "New Climber")
    screen = my_screen(ctx)
    assert "Add a short bio with Edit profile" in texts(screen.header)
    assert texts(screen.top_send) == ["No sends yet"]
    assert texts(screen.history) == ["No climbs logged yet"]


def test_someone_elses_profile_is_read_only(ctx):
    screen = view.ProfileScreen(ctx, ctx.repos.users.get("maya"))
    assert not screen.is_me
    assert screen.edit_button not in screen.header.controls
    assert not screen.control.controls[4].visible  # log form


def test_profile_requested_event_pushes_the_screen(ctx):
    view.setup(ctx)
    ctx.events.publish(ProfileRequested(DEMO_USER_ID))
    title, control = ctx.nav.stack[-1]
    assert title == "Profile"
    assert "Daniel Woods" in texts(control)


def test_unknown_profile_pushes_nothing(ctx):
    assert view.open_profile(ctx, "nobody") is None
    assert ctx.nav.stack == []


def test_tab_without_signed_in_user(ctx):
    ctx.current_user = None
    assert texts(view.build_view(ctx)) == ["Sign in to see your profile"]
