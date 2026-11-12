"""Canonical research utilities for the small-cap event-alpha project."""

from .core import (
    HORIZONS,
    REQUIRED_COLUMNS,
    add_canonical_features,
    build_event_sample,
    validate_input_panel,
)

__all__ = [
    "HORIZONS",
    "REQUIRED_COLUMNS",
    "add_canonical_features",
    "build_event_sample",
    "validate_input_panel",
]
