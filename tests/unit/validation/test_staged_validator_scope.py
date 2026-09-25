# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Commit-time validators accept the complete staged-file argv set."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VALIDATION_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts" / "validation"
sys.path.insert(0, str(VALIDATION_SCRIPTS))

import validate_namespace_isolation
import validate_naming_patterns
import validate_spi_naming
import validate_spi_typing_patterns

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "module",
    [validate_spi_naming, validate_spi_typing_patterns],
)
def test_file_discovery_accepts_one_staged_file(module: object, tmp_path: Path) -> None:
    staged = tmp_path / "protocol_clean.py"
    staged.write_text("from typing import Protocol\n", encoding="utf-8")
    unstaged = tmp_path / "protocol_unstaged.py"
    unstaged.write_text("class Unstaged: ...\n", encoding="utf-8")

    assert module.discover_python_files(staged) == [staged]  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "module",
    [validate_naming_patterns, validate_namespace_isolation],
)
def test_cli_accepts_multiple_staged_files(
    module: object, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("", encoding="utf-8")
    second.write_text("", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["validator", str(first), str(second)])

    assert module.main() == 0  # type: ignore[attr-defined]
