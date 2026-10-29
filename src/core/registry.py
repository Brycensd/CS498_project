"""Finds feature packages so adding a feature never requires editing core."""

from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass

from core.feature import Feature

log = logging.getLogger(__name__)

FEATURES_PACKAGE = "features"


@dataclass(frozen=True)
class LoadError:
    module: str
    message: str


def discover_features(package: str = FEATURES_PACKAGE) -> tuple[list[Feature], list[LoadError]]:
    """Import every sub-package of `package` not starting with "_" and collect its FEATURE.

    A feature that fails to import, lacks a valid FEATURE, or reuses another feature's id
    is skipped and reported in the returned errors instead of raising, so one broken
    feature can't stop the app from starting.
    """
    features: list[Feature] = []
    errors: list[LoadError] = []
    seen_ids: set[str] = set()

    root = importlib.import_module(package)
    for info in sorted(pkgutil.iter_modules(root.__path__), key=lambda m: m.name):
        if not info.ispkg or info.name.startswith("_"):
            continue
        module_name = f"{package}.{info.name}"
        try:
            module = importlib.import_module(module_name)
            feature = getattr(module, "FEATURE", None)
            if not isinstance(feature, Feature):
                raise TypeError("module has no FEATURE = Feature(...)")
            if feature.id in seen_ids:
                raise ValueError(f"duplicate feature id {feature.id!r}")
        except Exception as exc:
            log.exception("Failed to load feature %s", module_name)
            errors.append(LoadError(module_name, f"{type(exc).__name__}: {exc}"))
            continue
        seen_ids.add(feature.id)
        features.append(feature)

    features.sort(key=lambda f: (f.order, f.title))
    return features, errors
