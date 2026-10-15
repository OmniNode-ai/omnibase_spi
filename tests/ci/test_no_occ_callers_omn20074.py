# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20074 S6: omnibase_spi admits repo-owned evidence without OCC callers.

Adapted from omnimemory's S6 retirement gate. Assertions inspect parsed YAML,
so historical comments do not count as callers. OMN20074_BASE_TREE can select
an archived base tree for the negative control.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(
    os.environ.get("OMN20074_BASE_TREE", Path(__file__).resolve().parents[2])
)
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
RUNNER_IP_PIN = "a45ba68f053e9979c6edef21103c0e674e5f7630"
RECEIPT_GATE_PATH = "OmniNode-ai/omnibase_core/.github/workflows/receipt-gate.yml"


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def _workflows() -> dict[str, dict[str, Any]]:
    parsed = {
        path.relative_to(WORKFLOWS).as_posix(): _load(path)
        for path in sorted(WORKFLOWS.rglob("*"))
        if path.suffix in {".yml", ".yaml"}
    }
    assert parsed, f"no workflows found in {WORKFLOWS}"
    return parsed


def _jobs() -> list[tuple[str, str, dict[str, Any]]]:
    rows = []
    for name, data in _workflows().items():
        for job_id, job in (data.get("jobs") or {}).items():
            assert isinstance(job, dict), f"{name}:{job_id}"
            rows.append((name, job_id, job))
    return rows


def _python_body(run: str) -> str:
    head, separator, rest = run.partition("<<'PY'\n")
    assert separator and "uv run python3" in head, run
    body, separator, _ = rest.partition("\nPY")
    assert separator, run
    return body


def test_no_occ_callers_retired_workflows_and_helper_are_absent() -> None:
    retired = (
        ".github/workflows/call-occ-autobind.yml",
        ".github/workflows/call-occ-companion-effect.yml",
        "scripts/ci/occ_manual_replay_precheck.py",
    )
    assert not [path for path in retired if (REPO_ROOT / path).exists()]


def test_no_occ_callers_workflow_calls_an_occ_reusable() -> None:
    offenders = []
    for name, job_id, job in _jobs():
        uses = str(job.get("uses", "")).lower()
        if any(
            token in uses
            for token in (
                "call-occ-autobind",
                "call-occ-companion-effect",
                "occ-preflight",
                "omninode-ai/onex_change_control/",
            )
        ):
            offenders.append(f"{name}:{job_id} -> {uses}")
    assert not offenders, offenders


def test_no_occ_callers_workflow_checks_out_occ() -> None:
    offenders = []
    for name, job_id, job in _jobs():
        for step in job.get("steps") or []:
            if str(step.get("uses", "")).lower().startswith("actions/checkout@"):
                repository = (step.get("with") or {}).get("repository", "")
                if str(repository).lower() == "omninode-ai/onex_change_control":
                    offenders.append(f"{name}:{job_id}:{step.get('name')}")
    assert not offenders, offenders


def test_no_occ_callers_workflow_clones_or_fetches_occ() -> None:
    offenders = []
    for name, job_id, job in _jobs():
        for step in job.get("steps") or []:
            run = str(step.get("run", ""))
            if re.search(r"\bgit\b[^\n]*\b(?:clone|fetch)\b", run) and re.search(
                r"onex_change_control\.git\b", run, re.IGNORECASE
            ):
                offenders.append(f"{name}:{job_id}:{step.get('name')}")
    assert not offenders, offenders


def test_no_occ_callers_repo_evidence_caller_enforces_without_occ() -> None:
    job = _workflows()["call-repo-evidence-gate.yml"]["jobs"]["repo-evidence"]
    # Dependabot may advance the immutable pin without changing the reusable.
    assert re.fullmatch(rf"{re.escape(RECEIPT_GATE_PATH)}@[0-9a-f]{{40}}", job["uses"])
    inputs = job["with"]
    assert inputs.get("evidence-source") == "caller"
    assert inputs.get("shadow") == "false"
    assert inputs.get("compare-with-occ") == "false"
    assert "occ-context" not in inputs
    assert inputs.get("verifier-version") == "0.4.310"


def test_no_occ_callers_runner_ip_reusable_has_no_nested_preflight() -> None:
    job = _workflows()["ban-hardcoded-runner-ip.yml"]["jobs"]["ban-hardcoded-runner-ip"]
    assert job["uses"] == (
        "OmniNode-ai/omniclaude/.github/workflows/ban-hardcoded-runner-ip.yml@"
        + RUNNER_IP_PIN
    )


def test_no_occ_callers_contract_compliance_validates_repo_contracts() -> None:
    workflows = _workflows()
    job = workflows["ci.yml"]["jobs"]["contract-compliance"]
    assert job["name"] == "Contract Compliance Check"
    steps = job["steps"]
    assert all("working-directory" not in step for step in steps)
    setup = [
        step
        for step in steps
        if str(step.get("uses", "")).startswith("astral-sh/setup-uv@")
    ]
    assert len(setup) == 1
    assert setup[0]["with"]["cache-dependency-glob"] == "uv.lock"
    assert any(step.get("run") == "uv sync --frozen" for step in steps)
    validate = [
        step for step in steps if step.get("name") == "Validate contract YAML files"
    ]
    assert len(validate) == 1
    run = validate[0]["run"]
    assert re.search(
        r'find\s+(?:"\$GITHUB_WORKSPACE/contracts"|contracts)\s+-maxdepth 1\s+-type f\s+-name "OMN-\*\.yaml"',
        run,
    ), run
    assert 'uv run python3 - "${CONTRACTS[@]}"' in run
    reference = next(
        step["run"]
        for step in workflows["contract-validation.yml"]["jobs"]["contract-validation"][
            "steps"
        ]
        if step.get("id") == "validate-contract"
    )
    body = _python_body(run)
    assert (
        "from omnibase_core.models.ticket.model_ticket_contract import ModelTicketContract"
        in body
    )
    assert "ModelTicketContract.from_yaml" in body
    assert body == _python_body(reference)
    assert "onex_change_control" not in run


def test_no_occ_callers_required_checks_manifest_names_no_occ_context() -> None:
    manifest = _load(REPO_ROOT / ".github" / "required-checks.yaml")
    names = [row["name"] for row in manifest["gates"]]
    assert names, "the manifest lists no check"
    assert not [
        name for name in names if "occ-preflight" in name.lower() or "OCC" in name
    ]


def test_no_occ_callers_precommit_runs_no_occ_hook() -> None:
    config = _load(REPO_ROOT / ".pre-commit-config.yaml")
    hooks = [hook for repo in config["repos"] for hook in repo.get("hooks") or []]
    assert hooks, "no pre-commit hook found"
    offenders = [
        hook["id"]
        for hook in hooks
        if any(
            token in str(hook.get(key, ""))
            for key in ("entry", "id")
            for token in ("occ_manual_replay_precheck", "onex_change_control")
        )
    ]
    assert not offenders, offenders
