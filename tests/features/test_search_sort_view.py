"""Search screen behavior, checked without a UI via RecordingNavigator."""

from features.search_sort import view


def test_starts_with_every_climb_easiest_first(ctx):
    screen = view.SearchScreen(ctx)
    grades = [c.grade for c in screen.visible_climbs()]
    assert len(grades) == len(ctx.repos.climbs.list_climbs())
    assert grades == sorted(grades)


def test_typing_narrows_the_results(ctx):
    screen = view.SearchScreen(ctx)
    screen.search_box.value = "crimp"
    screen.search_box.on_change(None)
    assert {tile.title.value for tile in screen.results.controls} == {"Crimp Lord"}


def test_changing_the_sort_reorders_the_results(ctx):
    screen = view.SearchScreen(ctx)
    screen.sort_dropdown.value = "section"
    screen.sort_dropdown.on_select(None)
    section_ids = [c.section_id for c in screen.visible_climbs()]
    assert section_ids == sorted(section_ids)


def test_no_matches_shows_message(ctx):
    screen = view.SearchScreen(ctx)
    screen.search_box.value = "zzz"
    screen.refresh()
    assert screen.results.controls[0].title.value == "No climbs match your search"


def test_tapping_a_result_pushes_its_detail_screen_and_keeps_the_search(ctx):
    screen = view.SearchScreen(ctx)
    screen.search_box.value = "crimp"
    screen.refresh()
    screen.results.controls[0].on_click(None)
    title, _ = ctx.nav.stack[-1]
    assert title == "Crimp Lord"
    assert screen.search_box.value == "crimp"
