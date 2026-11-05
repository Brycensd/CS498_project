"""Search screen behavior, checked without a UI via RecordingNavigator."""

from core.events import SectionRequested
from features.search_sort import logic, view


def test_starts_with_every_climb_easiest_first(ctx):
    screen = view.SearchScreen(ctx)
    grades = [c.grade for c in screen.visible_climbs()]
    assert len(grades) == len(ctx.repos.climbs.list_climbs())
    assert grades == sorted(grades)


def test_typing_narrows_the_results(ctx):
    climbs = ctx.repos.climbs.list_climbs()
    target = climbs[0]
    expected = {c.id for c in climbs if c.title == target.title}
    screen = view.SearchScreen(ctx)
    screen.search_box.value = target.title
    screen.search_box.on_change(None)
    assert len(expected) < len(climbs)
    assert {c.id for c in screen.visible_climbs()} == expected
    assert {tile.title.value for tile in screen.results.controls} == {target.title}


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
    target = ctx.repos.climbs.list_climbs()[0]
    screen = view.SearchScreen(ctx)
    screen.search_box.value = target.title
    screen.refresh()
    # Titles can repeat, so tap the last result and check the details are that climb's.
    tapped = screen.visible_climbs()[-1]
    screen.results.controls[-1].on_click(None)
    title, detail = ctx.nav.stack[-1]
    assert title == target.title
    # The last control is the View Section button.
    rows = {tile.title.value: tile.trailing.value for tile in detail.controls[:-1]}
    section = ctx.repos.climbs.get_section(tapped.section_id)
    assert rows == dict(logic.climb_details(tapped, section))
    assert screen.search_box.value == target.title


def test_view_section_button_requests_the_climbs_section(ctx):
    requests = []
    ctx.events.subscribe(SectionRequested, requests.append)
    screen = view.SearchScreen(ctx)
    tapped = screen.visible_climbs()[-1]
    screen.results.controls[-1].on_click(None)
    _, detail = ctx.nav.stack[-1]

    button = detail.controls[-1].content
    assert button.content == "View Section"
    button.on_click(None)

    assert requests == [SectionRequested(tapped.section_id)]
