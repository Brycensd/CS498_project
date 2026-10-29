# Climbing Gym

An Android-first app for climbing gyms, written in Python with [Flet](https://flet.dev) 1.x.
A gym has sections 1-8; each section has a wall photo and a set of climbs. Planned features:
section/climb browsing, ascent tracking, comments and user profiles.

See [docs/architecture.md](docs/architecture.md) for how the app is structured and
[CONTRIBUTING.md](CONTRIBUTING.md) for how to add a feature.

## Setup (Windows)

Requires Python 3.11+ (the team standard is 3.12) and Git.

```powershell
git clone https://github.com/Brycensd/CS498_project.git
cd CS498_project
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --group dev
pre-commit install
```

`--group dev` needs pip 25.1 or newer, which the upgrade step provides. It installs Flet
with its CLI, desktop and web runners, plus pytest, ruff and pre-commit.

In VS Code, pick `.venv\Scripts\python.exe` as the interpreter (Ctrl+Shift+P →
"Python: Select Interpreter").

## Run

```powershell
flet run                 # desktop window
flet run --web           # in a browser
flet run -d -r           # desktop, hot reload on file changes
flet run --android -d -r # on a phone running the Flet app (scan the QR code)
```

`-d -r` reloads the app whenever any file under `src/` is saved; without it only
`main.py` is watched.

The app has no persistent storage yet: every launch starts from the seeded in-memory data.

## Test and lint

```powershell
pytest
ruff check .
ruff format .
```

CI runs the same checks on every pull request.

## Build the Android APK

```powershell
flet build apk
```

The first build downloads Flutter, a JDK and the Android SDK (several GB) and takes a
while; later builds are much faster. The APK is written to `build/apk/`. Install it on a
phone with USB debugging enabled using `adb install build/apk/<name>.apk`, or copy the
file to the phone.

APK builds are slow, so day-to-day development uses `flet run`; build the APK occasionally
(or have one person own it) to catch Android-only issues early.

## Project layout

```
src/main.py          entry point
src/core/            framework (reviewed changes only)
src/features/        one folder per feature; copy _template/ to start
src/assets/          icon and wall photos
tests/               pytest suite
```
