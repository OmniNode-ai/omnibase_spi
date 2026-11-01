# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20032, OMN-21854: the caller pins the receipt-gate reusable that enforces the verifier floor and installs its verifier from a dev-merge tag."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
CALLER = REPO_ROOT / ".github" / "workflows" / "call-repo-evidence-gate.yml"

# Squash commit of omnibase_core#1914, the last pin before omnibase_core#1932 added
# VERIFIER_FLOOR to the reusable's "Install the pinned verifier" step. The pin is a
# dev-merge tag of a descendant of #1932 now, so a tag never equals this sha.
PRE_FLOOR_PIN = "fb0c6c2117d5868a398b0920cd0048d0824415b1"

VERIFIER_TAG_PATTERN = r"dev-\d{14}-[0-9a-f]{12}"


def _job() -> dict[str, Any]:
    doc = yaml.safe_load(CALLER.read_text(encoding="utf-8"))
    job: dict[str, Any] = doc["jobs"]["repo-evidence"]
    return job


def test_caller_pins_the_reusable_that_carries_the_verifier_floor() -> None:
    uses = _job()["uses"]
    assert re.fullmatch(
        r"OmniNode-ai/omnibase_core/\.github/workflows/receipt-gate\.yml@dev-\d{14}-[0-9a-f]{12}",
        uses,
    )
    assert uses.split("@", 1)[1] != PRE_FLOOR_PIN, (
        "pin the omnibase_core receipt-gate reusable at or past omnibase_core#1932"
    )


def test_caller_verifier_tag_replaces_the_version_at_or_above_the_floor() -> None:
    inputs = _job()["with"]
    assert re.fullmatch(VERIFIER_TAG_PATTERN, inputs["verifier-tag"]), (
        "verifier-tag must be an omnimarket dev-merge tag; the reusable refuses a tag "
        "that does not descend from its floor commit"
    )
    assert "verifier-version" not in inputs


def test_verifier_tag_pattern_admits_a_dev_merge_tag() -> None:
    assert re.fullmatch(VERIFIER_TAG_PATTERN, "dev-20261101000200-949993edf3b7")


@pytest.mark.parametrize(
    "tag",
    [
        "0.4.310",
        "main",
        "dev-20261101000200",
        "dev-20261101000200-949993edf3b",
        "dev-20261101000200-949993EDF3B7",
        "dev-20261101000200-949993edf3b7a",
        "949993edf3b76b95bd2eb38326ea8d74cac9b40f",
        "",
    ],
)
def test_verifier_tag_pattern_refuses_a_version_branch_sha_or_malformed_tag(
    tag: str,
) -> None:
    assert not re.fullmatch(VERIFIER_TAG_PATTERN, tag)
