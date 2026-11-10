"""Profile screen: header with edit form, hardest send, "log a climb" form and send history."""

from __future__ import annotations

from datetime import UTC, datetime

import flet as ft

from core.context import AppContext
from core.events import ProfileRequested, ProfileUpdated
from core.models import AscentStyle, Climb, TagColor, User

from . import logic

AVATAR_RADIUS = 56


def setup(ctx: AppContext) -> None:
    """Open a profile whenever another feature (e.g. home) asks for one."""
    ctx.events.subscribe(ProfileRequested, lambda event: open_profile(ctx, event.user_id))


def build_view(ctx: AppContext) -> ft.Control:
    if ctx.current_user is None:
        return ft.Container(padding=24, content=ft.Text("Sign in to see your profile"))
    return ProfileScreen(ctx, ctx.current_user).control


def open_profile(ctx: AppContext, user_id: str) -> ProfileScreen | None:
    user = ctx.repos.users.get(user_id)
    if user is None:
        ctx.show_message("That climber's profile no longer exists")
        return None
    screen = ProfileScreen(ctx, user)
    ctx.nav.push("Profile", screen.control)
    return screen


class ProfileScreen:
    """One climber's profile. Editing and logging climbs are only offered on your own."""

    def __init__(self, ctx: AppContext, user: User) -> None:
        self._ctx = ctx
        self.user = user
        self.is_me = ctx.current_user is not None and ctx.current_user.id == user.id
        sections = ctx.repos.climbs.list_sections()
        self._section_names = {s.id: s.name for s in sections}

        # Header: picture, name, bio and the Edit button. Rebuilt by refresh().
        self.header = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
        self.edit_button = ft.OutlinedButton(
            "Edit profile", icon=ft.Icons.EDIT, on_click=lambda _e: self.start_editing()
        )

        # Edit form, hidden until Edit profile is tapped.
        self.name_field = ft.TextField(label="Name", max_length=logic.MAX_NAME_LENGTH)
        self.bio_field = ft.TextField(
            label="Bio",
            hint_text="A few words about your climbing",
            multiline=True,
            min_lines=2,
            max_lines=4,
            max_length=logic.MAX_BIO_LENGTH,
        )
        self.edit_form = ft.Column(
            visible=False,
            controls=[
                self.name_field,
                self.bio_field,
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.TextButton("Cancel", on_click=lambda _e: self.stop_editing()),
                        ft.Button("Save", icon=ft.Icons.CHECK, on_click=lambda _e: self.save()),
                    ],
                ),
            ],
        )

        # "Log a climb" form.
        self.climb_dropdown = ft.Dropdown(
            label="Climb",
            expand=True,
            options=[
                ft.DropdownOption(key=climb_id, text=label)
                for climb_id, label in logic.climb_choices(ctx.repos.climbs.list_climbs(), sections)
            ],
        )
        self.style_dropdown = ft.Dropdown(
            label="Style",
            expand=True,
            value=AscentStyle.SEND,
            options=[ft.DropdownOption(key=s, text=t) for s, t in logic.STYLE_LABELS.items()],
        )
        self.log_button = ft.Button(
            "Log climb", icon=ft.Icons.ADD, on_click=lambda _e: self.log_climb()
        )
        log_form = ft.Column(
            visible=self.is_me,
            controls=[
                heading("Log a climb"),
                ft.Row([self.climb_dropdown]),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.style_dropdown, self.log_button],
                ),
            ],
        )

        self.top_send = ft.Column(spacing=0)
        self.history = ft.Column(spacing=0)
        self.control = ft.ListView(
            expand=True,
            padding=16,
            spacing=12,
            controls=[
                self.header,
                self.edit_form,
                heading("Hardest send"),
                self.top_send,
                log_form,
                heading("Sends"),
                self.history,
            ],
        )
        self.refresh()

    # Display

    def refresh(self) -> None:
        """Redraw everything from the repositories. Flet re-renders after the click handler."""
        user = self.user
        bio = user.bio or ("Add a short bio with Edit profile" if self.is_me else "")
        self.header.controls = [
            avatar(user),
            ft.Text(user.display_name, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Text(
                bio,
                visible=bool(bio),
                text_align=ft.TextAlign.CENTER,
                italic=not user.bio,
                color=None if user.bio else ft.Colors.ON_SURFACE_VARIANT,
            ),
        ]
        if self.is_me and not self.edit_form.visible:
            self.header.controls.append(self.edit_button)

        history = logic.sends(
            self._ctx.repos.ascents.list_for_user(user.id), self._ctx.repos.climbs.get_climb
        )
        best = logic.top_send(history)
        self.top_send.controls = [self._send_tile(best) if best else ft.Text("No sends yet")]
        self.history.controls = [self._send_tile(s) for s in history] or [
            ft.Text("No climbs logged yet")
        ]

    def _send_tile(self, send: logic.Send) -> ft.Control:
        climb = send.climb
        section = self._section_names.get(climb.section_id, "?")
        return ft.ListTile(
            leading=grade_badge(climb),
            title=ft.Text(f"{section} · {climb.title}"),
            subtitle=ft.Text(logic.send_label(send)),
            content_padding=ft.Padding.symmetric(horizontal=0),
        )

    # Editing

    def start_editing(self) -> None:
        self.name_field.value = self.user.display_name
        self.bio_field.value = self.user.bio
        self.name_field.error = None
        self.bio_field.error = None
        self.edit_form.visible = True
        self.refresh()  # hides the Edit button

    def stop_editing(self) -> None:
        self.edit_form.visible = False
        self.refresh()

    def save(self) -> None:
        try:
            updated = logic.edit_profile(
                self.user, self.name_field.value or "", self.bio_field.value or ""
            )
        except logic.ProfileError as err:
            field = self.name_field if err.field == "name" else self.bio_field
            field.error = str(err)
            return
        self._ctx.repos.users.update(updated)
        self.user = updated
        if self.is_me:
            self._ctx.current_user = updated
        self.stop_editing()
        self._ctx.events.publish(ProfileUpdated(updated.id))
        self._ctx.show_message("Profile saved")

    # Logging climbs

    def log_climb(self) -> None:
        climb_id = self.climb_dropdown.value
        if not climb_id:
            self.climb_dropdown.error_text = "Choose a climb"
            return
        self.climb_dropdown.error_text = None
        ascent = logic.new_ascent(
            self.user.id,
            climb_id,
            AscentStyle(self.style_dropdown.value or AscentStyle.SEND),
            datetime.now(UTC),
        )
        self._ctx.repos.ascents.add(ascent)
        self.climb_dropdown.value = None
        self.refresh()
        self._ctx.events.publish(ProfileUpdated(self.user.id))
        self._ctx.show_message("Climb logged")


# Badge (background, text) colors per difficulty tag. Backgrounds match the sections
# feature's TAG_SWATCHES (features can't import each other); text is dark on light tags so
# the grade stays readable. Keep the two tables in step if a shade changes.
TAG_BADGE_COLORS: dict[TagColor, tuple[ft.Colors, ft.Colors]] = {
    TagColor.RED: (ft.Colors.RED, ft.Colors.WHITE),
    TagColor.YELLOW: (ft.Colors.YELLOW, ft.Colors.BLACK),
    TagColor.GREEN: (ft.Colors.GREEN, ft.Colors.WHITE),
    TagColor.WHITE: (ft.Colors.WHITE, ft.Colors.BLACK),
    TagColor.BLUE: (ft.Colors.BLUE, ft.Colors.WHITE),
    TagColor.BLACK: (ft.Colors.BLACK, ft.Colors.WHITE),
    TagColor.PURPLE: (ft.Colors.PURPLE_800, ft.Colors.WHITE),
    TagColor.ORANGE: (ft.Colors.ORANGE, ft.Colors.BLACK),
    TagColor.PINK: (ft.Colors.PINK, ft.Colors.WHITE),
}

BADGE_SIZE = 40


def grade_badge(climb: Climb) -> ft.Control:
    """A circle in the climb's tag color showing its V-grade, e.g. "V5" on black."""
    background, text = TAG_BADGE_COLORS[climb.tag]
    return ft.Container(
        width=BADGE_SIZE,
        height=BADGE_SIZE,
        shape=ft.BoxShape.CIRCLE,
        bgcolor=background,
        # The outline keeps white and black badges visible on light and dark themes.
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        alignment=ft.Alignment.CENTER,
        tooltip=f"{climb.tag} tag ({climb.tag.range_label})",
        content=ft.Text(climb.grade_label, color=text, weight=ft.FontWeight.BOLD),
    )


def heading(text: str) -> ft.Control:
    return ft.Text(text, theme_style=ft.TextThemeStyle.TITLE_LARGE)


def avatar(user: User) -> ft.CircleAvatar:
    # The initials sit behind the picture, so they show when there is no picture or it
    # fails to load.
    return ft.CircleAvatar(
        radius=AVATAR_RADIUS,
        foreground_image_src=user.avatar,
        content=ft.Text(logic.initials(user.display_name), size=AVATAR_RADIUS * 0.6),
    )
