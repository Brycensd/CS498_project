# Architecture

This document describes how the app is put together and lists the design decisions the
team should confirm. Code lives in `src/` (the `flet create` layout); tests live in `tests/`.

## Folder structure

```
pyproject.toml            dependencies, pytest/ruff config, flet build config
src/
  main.py                 entry point: ft.run(core.app.main)
  assets/                 icon.png, walls/ (wall photos), avatars/ (profile pictures)
  core/                   stable framework - changes need review (see CODEOWNERS)
    models.py             shared dataclasses: Gym, Section, Climb, Ascent, Comment, User,
                          NewsPost
    repositories.py       repository interfaces (Protocols) + Repositories bundle
    memory_repo.py        in-memory implementation, seeded with 4 sections, a demo user,
                          their sends and one news post
    events.py             EventBus (publish/subscribe by event type)
    navigation.py         Navigator: push/pop full-screen detail views
    context.py            AppContext handed to every feature
    feature.py            Feature descriptor (the feature contract)
    registry.py           discovers features under src/features/
    shell.py              owns the Page and NavigationBar, isolates feature errors
    app.py                wires everything together
  features/
    _template/            copy this to start a feature (ignored by discovery)
    home/                 profile summary (name, picture, hardest send) and gym news
    sections/             section -> wall photo -> climb detail browsing
    search_sort/          search every climb, sort, jump to its section
    profile/              your profile: edit name and bio, log climbs, hardest send, send
                          history (no tab; opened from home via ProfileRequested)
tests/
  conftest.py             fake AppContext fixture (page=None, recording navigator)
  test_*.py               core tests + smoke test over every feature
  features/               per-feature logic tests
```

## The feature contract

A feature is a package `src/features/<name>/` whose `__init__.py` exposes:

```python
FEATURE = Feature(id=..., title=..., icon=ft.Icons.X, build_view=build_view, order=50)
```

`build_view(ctx: AppContext) -> ft.Control` is the whole contract. The shell puts the
returned control in the body area; features never touch `page.navigation_bar`, `page.views`
or page layout.

Optionally, `Feature(..., setup=setup)` gives a `setup(ctx)` hook that the shell runs once
at startup, before any view is built and whether or not the tab is ever opened. Subscribe
to events there, not in `build_view`, which runs again on every tab switch.

Inside the package:

- `logic.py` - pure Python, **no flet imports**, unit tested.
- `view.py` - builds controls, calls `logic.py`, talks to `ctx`.

Features never import other features.

## AppContext

| Field          | Purpose                                                                 |
|----------------|-------------------------------------------------------------------------|
| `repos`        | `Repositories(climbs, ascents, comments, users, news)` - all data access |
| `events`       | `EventBus` for cross-feature notifications                              |
| `nav`          | `Navigator.push(title, control)` / `pop()` for drill-down screens       |
| `current_user` | the signed-in `User` (a seeded demo user for now)                       |
| `page`         | the `ft.Page`, or `None` in tests. Prefer `ctx.show_message()` over it. |

## Models

Frozen dataclasses with string ids (so server UUIDs work later). Values are converted once
when created: grades are `int` (V-scale), moments are `datetime` and calendar days (such
as an event day) are `date`.

Each climb has three separate difficulty/appearance fields:

- `grade` - the exact V-grade, e.g. V5.
- `tag` - the colored difficulty tag (`TagColor`). Tags overlap: Red V0, Yellow V0–V2,
  Green V1–V3, White V2–V4, Blue V3–V5, Black V4–V6, Purple V5–V7, Orange V6–V8,
  Pink V8+. The ranges live in one table, `TAG_GRADE_RANGES` in `core/models.py`.
- `hold_color` - any color; unrelated to the tag.

Images are stored as
a string that is either an asset path (`walls/section_1.png`) or a URL - `ft.Image` accepts
both, so moving photos to a server later does not change the model.

## Discovery and tabs

`registry.discover_features()` imports every package under `features/` that does not start
with `_`, reads its `FEATURE`, and sorts by `(order, title)`. Each feature becomes one
`NavigationBar` destination, unless it sets `Feature(..., show_tab=False)`: such a feature
gets no tab but its `setup` hook still runs, so it can open screens with `ctx.nav.push` in
response to an event (the profile screen works this way). The counts below are of tabs.

- **0 features** - the shell shows a "no features" message (plus any load errors).
- **1 feature** - no `NavigationBar` (Flutter requires 2+ destinations); the view fills the
  page.
- **2+ features** - one tab per feature. Views are rebuilt on every tab switch so they
  always show fresh repository data.

## Drill-down screens and the back button

Chosen: a **core navigation helper** (`ctx.nav`). `push(title, control)` appends a
full-screen `ft.View` with an `AppBar` to `page.views`; Flutter shows a back arrow
automatically. The Android back button and the back arrow both fire `page.on_view_pop`,
which the helper handles by removing the top view. On the root view, Android back exits
the app (Flutter default).

Compared with each feature managing its own sub-views:

| Core helper (chosen)                                   | Per-feature sub-views                              |
|--------------------------------------------------------|----------------------------------------------------|
| Identical back behavior everywhere                     | Each feature re-implements back handling            |
| Features stay ignorant of `page.views`                 | Features must touch page internals                  |
| Tested without UI via a recording fake navigator       | Hard to test                                        |
| Detail screens hide the tab bar (normal on Android)    | Tab bar can stay visible                            |
| No URL/deep links (not needed on Android)              | Could use `page.route` for deep links               |

## Keeping a broken feature from crashing the app

1. **Import time** - `discover_features` catches any exception while importing a feature,
   logs it, and skips that feature. Missing/invalid `FEATURE` and duplicate ids are treated
   the same way.
2. **Build time** - the shell wraps `build_view` and shows an error panel in that tab
   instead of crashing.
3. **Events** - `EventBus.publish` catches and logs a failing subscriber so the other
   subscribers still run.
4. **CI** - the smoke test builds every feature's view with a fake context, so a broken
   feature fails the PR instead of the app.

Exceptions inside a feature's own click handlers are logged by Flet and do not crash the
app.

## Decisions for the team

1. **Models** - are the fields in `core/models.py` right? Are gyms bouldering-only
   (V-scale `int` grades) or do we also need rope grades (YDS)? Confirm the tag ranges from
   White through Orange against the gym's chart.
2. **Cross-feature navigation** - e.g. the ascents feature opening a climb detail page.
   Features can't import each other. Options: (a) a shared event such as
   `ClimbDetailRequested(climb_id)` in `core/events.py` that the sections feature handles,
   or (b) move "climb detail" into core as a shared view. Recommended: (a). The search
   feature's View Section button already works this way: it publishes `SectionRequested`,
   and the sections feature, which subscribes in its `setup` hook, opens the page.
3. **Tab bar on detail screens** - currently hidden (full-screen detail). Keep?
4. **Data backend** - the in-memory repo resets every launch. When do we add persistence
   (local SQLite vs. a server), and who owns it?
5. **Python version** - the team should all use the same local version (3.12 recommended).
