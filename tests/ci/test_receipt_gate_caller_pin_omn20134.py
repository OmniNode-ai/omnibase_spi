# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20134: the receipt-gate caller pins the omnibase_core dev-merge tag that carries the fix-parent fallback."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tests.ci.receipt_gate_pin import RECEIPT_GATE_PIN_TAG, RECEIPT_GATE_REUSABLE

pytestmark = pytest.mark.unit

CALLER = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "workflows"
    / "call-repo-evidence-gate.yml"
)


def _uses() -> str:
    doc = yaml.safe_load(CALLER.read_text(encoding="utf-8"))
    uses: str = doc["jobs"]["repo-evidence"]["uses"]
    return uses


def test_caller_pins_the_reusable_at_the_pin_tag() -> None:
    assert _uses() == f"{RECEIPT_GATE_REUSABLE}@{RECEIPT_GATE_PIN_TAG}"


def test_pin_tag_is_a_dev_merge_tag_and_not_a_commit_sha() -> None:
    assert re.fullmatch(r"dev-\d{14}-[0-9a-f]{12}", RECEIPT_GATE_PIN_TAG)
    assert not re.fullmatch(r"[0-9a-f]{40}", _uses().split("@", 1)[1])


def test_pin_tag_is_the_omnibase_core_tag_that_carries_the_verifier_tag_input() -> None:
    # OMN-21854: dev-20261101005012-ac2f26e3e5bf contains omnibase_core#2203, whose
    # receipt-gate.yml accepts verifier-tag.
    assert RECEIPT_GATE_PIN_TAG == "dev-20261101005012-ac2f26e3e5bf"
