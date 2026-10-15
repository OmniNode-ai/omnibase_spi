# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20074: omnibase_spi's repo-evidence caller enforces repo-owned evidence.

S6 cut-over: ``shadow`` and ``compare-with-occ`` are both "false", so
``repo-evidence / dod-verify`` carries a real verdict without an OCC comparison.
The OCC minting callers and their helper are gone (see
``test_no_occ_callers_omn20074.py``).

These tests guard the base-branch trigger, immutable pin, caller inputs, stable
context prefix, retirement of the OCC callers and runnable contract falsifiers.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CALLER = WORKFLOWS / "call-repo-evidence-gate.yml"
CONTRACT = REPO_ROOT / "contracts" / "OMN-20074.yaml"

RECEIPT_GATE_PATH = "OmniNode-ai/omnibase_core/.github/workflows/receipt-gate.yml"
# Squash commit of omnibase_core#1914, which predates the VERIFIER_FLOOR refusal of
# #1932 (OMN-20032). Dependabot only advances the pin, so this is the one pin to refuse.
PRE_FLOOR_PIN = "fb0c6c2117d5868a398b0920cd0048d0824415b1"
# 0.4.305 is the first omnimarket release carrying omnimarket#3563, the verifier half
# of the contract-home marker, and it ships the node_dod_verify occ-difference
# classifier (omnimarket#3277, 0.4.294).
VERIFIER_FLOOR = (0, 4, 305)


def _load(path: Path) -> dict[Any, Any]:
    assert path.is_file(), f"missing {path}"
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _job() -> dict[str, Any]:
    job: dict[str, Any] = _load(CALLER)["jobs"]["repo-evidence"]
    return job


def test_caller_runs_from_the_base_branch_on_dev_and_main() -> None:
    doc = _load(CALLER)
    # YAML 1.1 reads a bare `on` as the boolean True.
    triggers = doc["on"] if "on" in doc else doc[True]
    assert set(triggers) == {"pull_request_target"}
    assert triggers["pull_request_target"]["branches"] == ["dev", "main"]
    assert triggers["pull_request_target"]["types"] == [
        "opened",
        "synchronize",
        "reopened",
        "edited",
        "ready_for_review",
    ]
    assert doc["permissions"] == {"contents": "read", "pull-requests": "read"}
    assert set(doc["jobs"]) == {"repo-evidence"}


def test_caller_job_is_a_bare_call_with_no_secrets() -> None:
    job = _job()
    for key in ("steps", "secrets", "if", "name", "permissions"):
        assert key not in job, f"caller job must not declare {key}"
    assert "secrets: inherit" not in CALLER.read_text(encoding="utf-8")


def _is_pinned_receipt_gate(uses: str) -> bool:
    # Dependabot may advance the immutable pin without changing the reusable.
    match = re.fullmatch(rf"{re.escape(RECEIPT_GATE_PATH)}@([0-9a-f]{{40}})", uses)
    return match is not None and match.group(1) != PRE_FLOOR_PIN


def test_caller_pins_the_current_receipt_gate_by_full_sha() -> None:
    assert _is_pinned_receipt_gate(_job()["uses"])


@pytest.mark.parametrize(
    "pin",
    [
        "4e4f5e0404d364e296c5d37db6aa3ab9e07f8ffa",
        "5bfbf807ad684e820733ab3d4eeb26e78d15327e",
    ],
)
def test_receipt_gate_pin_accepts_full_sha_pin_updates(pin: str) -> None:
    assert _is_pinned_receipt_gate(f"{RECEIPT_GATE_PATH}@{pin}")


@pytest.mark.parametrize(
    "ref",
    [
        "main",
        "dev",
        "v1.0.0",
        "4e4f5e04",
        "a" * 39,
        "a" * 41,
        "g" * 40,
        "",
        PRE_FLOOR_PIN,
    ],
)
def test_receipt_gate_pin_rejects_mutable_malformed_or_pre_floor_refs(ref: str) -> None:
    assert not _is_pinned_receipt_gate(f"{RECEIPT_GATE_PATH}@{ref}")


@pytest.mark.parametrize(
    "path",
    [
        "OmniNode-ai/onex_change_control/.github/workflows/receipt-gate.yml",
        "other/omnibase_core/.github/workflows/receipt-gate.yml",
        "OmniNode-ai/omnibase_core/.github/workflows/codeql-reusable.yml",
        f"prefix/{RECEIPT_GATE_PATH}",
    ],
)
def test_receipt_gate_pin_rejects_other_workflows(path: str) -> None:
    assert not _is_pinned_receipt_gate(f"{path}@{'a' * 40}")


def test_current_receipt_gate_verifier_version_is_at_or_above_the_floor() -> None:
    version = tuple(int(part) for part in _job()["with"]["verifier-version"].split("."))
    assert version >= VERIFIER_FLOOR


def test_caller_shadow_mode_is_off_and_the_evidence_source_is_the_caller() -> None:
    inputs = _job()["with"]
    assert inputs["evidence-source"] == "caller"
    # Quoted strings: the reusable's boolean-like inputs are string inputs.
    assert inputs["shadow"] == "false"
    assert inputs["compare-with-occ"] == "false"
    version = tuple(int(part) for part in inputs["verifier-version"].split("."))
    assert version >= VERIFIER_FLOOR


def test_caller_ends_the_occ_comparison() -> None:
    assert _job()["with"]["compare-with-occ"] == "false"


def test_caller_passes_no_occ_context() -> None:
    assert "occ-context" not in _job()["with"]


def test_occ_callers_are_removed() -> None:
    for name in ("call-occ-autobind.yml", "call-occ-companion-effect.yml"):
        assert not (WORKFLOWS / name).exists(), f"{name} is retired at S6"
    assert not (REPO_ROOT / "scripts/ci/occ_manual_replay_precheck.py").exists()


def test_repo_contract_names_a_falsifier_per_criterion() -> None:
    contract = _load(CONTRACT)
    assert contract["ticket_id"] == "OMN-20074"
    criteria = [ac for req in contract["requirements"] for ac in req["acceptance"]]
    assert criteria, "contract must declare acceptance criteria"
    checks = [
        check["check_value"]
        for item in contract["dod_evidence"]
        for check in item["checks"]
    ]
    for criterion in criteria:
        assert "falsifier:" in criterion["statement"]
        falsifier = criterion["statement"].split("falsifier:", 1)[1].strip()
        assert falsifier in checks, f"{criterion['id']} falsifier has no dod check"
        test_file = falsifier.split()[3]
        assert (REPO_ROOT / test_file).is_file(), f"{test_file} does not exist"
