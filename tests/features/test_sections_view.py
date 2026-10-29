"""Drill-down behavior of the sections view, checked without a UI via RecordingNavigator."""

import flet as ft

from features.sections import view


def test_section_list_shows_all_eight_sections(ctx):
    root = view.build_view(ctx)
    assert [tile.title.value for tile in root.controls] == [f"Section {n}" for n in range(1, 9)]


def test_tapping_a_section_then_a_climb_pushes_two_screens(ctx):
    root = view.build_view(ctx)

    root.controls[2].on_click(None)  # Section 3
    title, screen = ctx.nav.stack[-1]
    assert title == "Section 3"
    image = screen.controls[0].content.controls[0]
    assert isinstance(image, ft.Image)
    assert image.src == "walls/section_3.png"

    climb_list = screen.controls[2]
    climb_list.controls[0].on_click(None)
    assert len(ctx.nav.stack) == 2
    climb_title, _ = ctx.nav.stack[-1]
    expected = min(ctx.repos.climbs.list_climbs("s3"), key=lambda c: (c.grade, c.name))
    assert climb_title == expected.name


def test_section_screen_sorts_and_filters(ctx):
    section = ctx.repos.climbs.get_section("s1")
    screen = view.open_section(ctx, section)
    climbs = ctx.repos.climbs.list_climbs("s1")

    screen.sort_dropdown.value = "grade_desc"
    screen.refresh()
    grades = [c.grade for c in screen.visible_climbs()]
    assert grades == sorted(grades, reverse=True)
    assert len(screen.climb_list.controls) == len(climbs)

    color = climbs[0].hold_color
    screen.hold_color_dropdown.value = color
    screen.refresh()
    assert {c.hold_color for c in screen.visible_climbs()} == {color}


def test_filter_with_no_matches_shows_message(ctx):
    screen = view.open_section(ctx, ctx.repos.climbs.get_section("s1"))
    screen.hold_color_dropdown.value = "Chartreuse"
    screen.refresh()
    assert screen.climb_list.controls[0].title.value == "No climbs match these filters"


def test_every_tag_has_a_swatch():
    from core.models import TagColor

    assert set(view.TAG_SWATCHES) == set(TagColor)
    assert view.TAG_SWATCHES[TagColor.PURPLE] == ft.Colors.PURPLE_800


def test_section_without_photo_shows_placeholder():
    from core.models import Section

    photo = view.wall_photo(Section("s9", "g1", 9, "Section 9", wall_image=None))
    assert isinstance(photo.content.controls[0], ft.Container)
