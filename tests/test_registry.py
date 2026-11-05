import shutil
import sys
import textwrap
from pathlib import Path

import pytest

from core.feature import Feature
from core.registry import discover_features

SRC = Path(__file__).resolve().parents[1] / "src"

GOOD_FEATURE = """
import flet as ft
from core.feature import Feature
FEATURE = Feature(id={id!r}, title={title!r}, icon=ft.Icons.STAR,
                  build_view=lambda ctx: ft.Text("hi"), order={order})
"""


@pytest.fixture
def make_package(tmp_path, monkeypatch, request):
    """Create an importable features-like package with the given sub-packages."""
    # Unique name per test so sys.modules caching can't leak between tests.
    name = f"fake_features_{request.node.name}"
    root = tmp_path / name
    root.mkdir()
    (root / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))

    def add(sub: str, init_source: str) -> Path:
        pkg = root / sub
        pkg.mkdir()
        (pkg / "__init__.py").write_text(textwrap.dedent(init_source))
        return pkg

    yield name, root, add
    for mod in [m for m in sys.modules if m == name or m.startswith(name + ".")]:
        del sys.modules[mod]


def test_discovers_and_sorts_by_order_then_title(make_package):
    name, _, add = make_package
    add("b", GOOD_FEATURE.format(id="b", title="Beta", order=10))
    add("a", GOOD_FEATURE.format(id="a", title="Alpha", order=20))
    add("c", GOOD_FEATURE.format(id="c", title="Aardvark", order=10))

    features, errors = discover_features(name)

    assert errors == []
    assert [f.id for f in features] == ["c", "b", "a"]


def test_skips_underscore_packages(make_package):
    name, _, add = make_package
    add("_hidden", GOOD_FEATURE.format(id="hidden", title="Hidden", order=1))
    add("shown", GOOD_FEATURE.format(id="shown", title="Shown", order=1))

    features, errors = discover_features(name)

    assert [f.id for f in features] == ["shown"]
    assert errors == []


def test_broken_features_are_reported_not_raised(make_package):
    name, _, add = make_package
    add("ok", GOOD_FEATURE.format(id="ok", title="Ok", order=1))
    add("crashes", "raise RuntimeError('boom')")
    add("no_feature", "X = 1")
    add("zz_dup", GOOD_FEATURE.format(id="ok", title="Dup", order=1))

    features, errors = discover_features(name)

    assert [f.id for f in features] == ["ok"]
    by_module = {e.module.rsplit(".", 1)[-1]: e.message for e in errors}
    assert set(by_module) == {"crashes", "no_feature", "zz_dup"}
    assert "boom" in by_module["crashes"]
    assert "duplicate" in by_module["zz_dup"]


def test_copied_template_becomes_a_feature_without_edits(make_package, ctx):
    name, root, _ = make_package
    shutil.copytree(SRC / "features" / "_template", root / "climb_log")

    features, errors = discover_features(name)

    assert errors == []
    [feature] = features
    assert isinstance(feature, Feature)
    assert feature.id == "climb_log"
    assert feature.title == "Climb Log"
    assert feature.build_view(ctx) is not None


def test_real_features_load_without_errors():
    features, errors = discover_features()
    assert errors == []
    assert "sections" in {f.id for f in features}
    assert features[0].id == "home"  # the app opens on the home page
