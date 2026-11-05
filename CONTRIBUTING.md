# Contributing

Read [docs/architecture.md](docs/architecture.md) first. Setup steps are in the
[README](README.md).

## Creating a feature

1. Copy `src/features/_template/` to `src/features/<name>/` (lowercase, underscores, e.g.
   `ascents`). Run `flet run`; your feature already shows up as a tab.
2. In `<name>/__init__.py` set `TITLE`, `ICON` (an `ft.Icons` value) and `ORDER` (tab
   position, lower first). Replace the docstring with a description of your feature.
3. Put rules, filtering, sorting and data shaping in `logic.py`. It must not import
   `flet`, so it can be tested with plain pytest.
4. Build the UI in `view.py`. `build_view(ctx)` returns one control. Use:
   - `ctx.repos.*` for all data access,
   - `ctx.nav.push(title, control)` to open a detail screen (back button is handled),
   - `ctx.show_message(text)` for a snackbar,
   - `ctx.events` to notify or listen to other features,
   - `ctx.current_user` for the signed-in user.

   To subscribe to events, add a `setup(ctx)` function and pass `setup=setup` to
   `Feature(...)`. It runs once at startup; `build_view` runs on every tab switch, so
   subscribing there would add a handler each time.
5. Add tests in `tests/features/test_<name>_logic.py`. The `ctx` fixture in
   `tests/conftest.py` gives you a UI-free context with seeded data and a
   `RecordingNavigator`, so you can also check that tapping something pushes a screen.
6. The smoke test (`tests/test_smoke_features.py`) builds your view automatically.

### Feature rules

- Only change files in `src/features/<name>/`, `tests/` and your feature's assets.
- Never import another feature. If two features need to talk, use an event type in
  `src/core/events.py` (that is a core change - see below).
- Never touch `page.navigation_bar`, `page.views` or page layout; return a control.
- Use Flet 1.x APIs: `ft.run`, `ft.Icons`, `ft.Colors`, `ft.Button`. Use the imperative
  style (build controls, change their properties); event handlers update the page
  automatically.

## Changing `src/core/`

`src/core/` is shared by everyone, so it changes slowly:

- Open an issue or ask in the team chat first describing what you need and why.
- Make core changes in their own PR, separate from feature work.
- Core PRs need an approving review from a code owner (see `.github/CODEOWNERS`).

## Branches

Branch from `main` and name branches `<type>/<short-description>`:

- `feature/ascent-tracking`
- `fix/section-photo-missing`
- `core/climb-detail-event`
- `chore/update-flet`

## Pull requests

- Keep PRs small and focused on one feature or fix.
- Before pushing: `pytest`, `ruff check .`, `ruff format .` (pre-commit runs ruff for you
  on every commit).
- CI must pass, and every PR needs at least one approving review before merging.
- Squash-merge into `main`; delete the branch afterwards.
- Never push directly to `main`.
