# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""The omnibase-core pin sits at the handshake bump floor (OMN-9050)."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLOOR = (0, 47, 66)


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


def test_pyproject_lower_bound_is_at_floor() -> None:
    deps = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"][
        "dependencies"
    ]
    spec = next(d for d in deps if d.startswith("omnibase-core"))
    match = re.search(r">=\s*([0-9.]+)", spec)
    assert match is not None, spec
    assert _version(match.group(1)) >= FLOOR


def test_lock_entry_is_at_floor() -> None:
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    entry = next(p for p in lock["package"] if p["name"] == "omnibase-core")
    assert _version(entry["version"]) >= FLOOR
