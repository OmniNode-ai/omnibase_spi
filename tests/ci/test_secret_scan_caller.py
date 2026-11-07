# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""The secret scan caller: nightly on the default branch, the scan hosted in omnibase_core.

Rebuild plan, step 0, safety source 1. The scan and its planted and clean controls live in
omnibase_core's reusable workflow (repositories of the same type run the same CI); this
repository's workflow must call it by a full-sha pin, run nightly and on a push to a default
branch, and stay out of the pull-request workflow budget.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
CALLER = REPO_ROOT / ".github" / "workflows" / "secret-scan.yml"

JOB_ID = "secret-scan"
NIGHTLY_CRON = "0 2 * * *"
CORE_REUSABLE = "OmniNode-ai/omnibase_core/.github/workflows/secret-scan-reusable.yml"


def _pinned_core_reusable(uses: str) -> bool:
    return re.fullmatch(rf"{re.escape(CORE_REUSABLE)}@[0-9a-f]{{40}}", uses) is not None


def _load() -> dict[Any, Any]:
    loaded = yaml.safe_load(CALLER.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_caller_uses_the_core_reusable_at_a_full_sha() -> None:
    uses = _load()["jobs"][JOB_ID]["uses"]
    assert _pinned_core_reusable(uses), uses


def test_pin_check_has_controls() -> None:
    assert _pinned_core_reusable(CORE_REUSABLE + "@" + "a" * 40)
    assert not _pinned_core_reusable(CORE_REUSABLE + "@dev")
    assert not _pinned_core_reusable(CORE_REUSABLE + "@" + "a" * 39)


def test_runs_nightly_and_on_a_default_branch_push_but_not_on_pull_requests() -> None:
    data = _load()
    # PyYAML 1.1 resolves the bare `on:` key to the boolean True.
    triggers = data.get("on", data.get(True))
    assert {"cron": NIGHTLY_CRON} in triggers["schedule"]
    assert set(triggers["push"]["branches"]) == {"main", "dev"}
    assert "pull_request" not in triggers


def test_caller_grants_read_only_contents() -> None:
    job = _load()["jobs"][JOB_ID]
    assert job["permissions"] == {"contents": "read"}
