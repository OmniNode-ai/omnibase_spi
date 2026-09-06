# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""The runner-IP gate must actually see this repository's tests (OMN-17993).

`.github/workflows/ban-hardcoded-runner-ip.yml` calls a reusable gate that
rejects the literal lab runner address. Until OMN-17993 the reusable scanned
`.github/workflows/**` only, and omnibase_compat — a repository that ships the
same caller — carried the exact banned literal as a test fixture with the gate
reporting green. Root cause 4.4 of the 2026-09-06 public-repo hygiene
inventory: a gate scoped to a subtree reports green over the rest of the tree.

Two halves, both required. The reusable now scans `tests/**`; this caller's
`paths:` filter must list it too, or the change that introduces a violation
never triggers the job that would catch it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CALLER = REPO_ROOT / ".github" / "workflows" / "ban-hardcoded-runner-ip.yml"

# The banned literal, assembled rather than spelled, so this file is not
# itself a finding for the gate it pins.
BANNED = ".".join(["192", "168", "86", "201"])
_ANNOTATION = "onex-allow-internal-ip"


@pytest.mark.unit
def test_caller_paths_filter_includes_tests() -> None:
    doc = yaml.safe_load(CALLER.read_text(encoding="utf-8"))
    paths = doc[True]["pull_request"]["paths"]  # YAML 1.1 parses `on:` as True
    assert "tests/**" in paths
    assert ".github/workflows/**" in paths


@pytest.mark.unit
def test_no_unannotated_runner_ip_literal_in_tests() -> None:
    """The live invariant the widened scope now enforces in CI."""
    offenders: list[str] = []
    for path in sorted((REPO_ROOT / "tests").rglob("*")):
        if not path.is_file() or path.suffix in {".pyc", ".png", ".gz"}:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if re.search(re.escape(BANNED), line) and _ANNOTATION not in line:
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")
    assert offenders == [], "\n".join(offenders)
