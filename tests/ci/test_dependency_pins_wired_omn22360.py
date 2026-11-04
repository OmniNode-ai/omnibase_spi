# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""The core dependency-pin check gates SPI's CI Summary (OMN-22360)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
CORE = "OmniNode-ai/omnibase_core"
WORKFLOW = f"{CORE}/.github/workflows/dependency-pins.yml@"


def _jobs() -> dict[str, Any]:
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    jobs = ci["jobs"]
    assert isinstance(jobs, dict)
    return jobs


def _core_repos() -> list[dict[str, Any]]:
    config = yaml.safe_load(
        (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    return [
        entry
        for entry in config["repos"]
        if str(entry.get("repo", "")).rstrip("/").endswith(CORE)
    ]


def test_dependency_pins_job_calls_the_core_workflow() -> None:
    job = _jobs()["dependency-pins"]
    assert str(job["uses"]).startswith(WORKFLOW)
    assert job["permissions"] == {"contents": "read"}
    assert "if" not in job
    assert not job.get("continue-on-error", False)


def test_dependency_pins_job_uses_the_core_hook_tag() -> None:
    tag = str(_jobs()["dependency-pins"]["uses"]).removeprefix(WORKFLOW)
    assert tag.startswith("dev-")
    # Hooks pinned by the full-sha tests carry the commit the tag's 12-hex suffix names.
    suffix = tag.rsplit("-", 1)[1]
    for entry in _core_repos():
        rev = str(entry["rev"])
        assert rev == tag or (len(rev) == 40 and rev.startswith(suffix))


def test_dependency_pins_hook_is_wired() -> None:
    hooks = [
        hook
        for entry in _core_repos()
        for hook in entry["hooks"]
        if hook["id"] == "check-dependency-pins"
    ]
    assert hooks == [{"id": "check-dependency-pins"}]


def test_stub_validator_runs_in_the_pinned_hook_environment() -> None:
    hooks = [
        hook
        for entry in _core_repos()
        for hook in entry["hooks"]
        if hook["id"] == "check-stub-implementations"
    ]
    assert len(hooks) == 1
    assert hooks[0]["language"] == "python"
    assert hooks[0]["entry"] == (
        "env -u PYTHONPATH python -m "
        "omnibase_core.nodes.node_validation_report_write_effect.runtime_validator_run "
        "omnibase_core.validation.validator_stub_implementations:ValidatorStubImplementations"
    )


@pytest.mark.parametrize(
    ("job_id", "variable"),
    [
        ("ai-slop-check", "AI_SLOP_CORE"),
        ("canonical-file-shape", "CANONICAL_FILE_SHAPE_CORE"),
        ("public-runner-placement", "RUNNER_PLACEMENT_CORE"),
    ],
)
def test_ci_validators_install_the_core_hook_tag_from_the_contract(
    job_id: str, variable: str
) -> None:
    job = _jobs()[job_id]
    contract = yaml.safe_load((ROOT / job["env"][variable]).read_text(encoding="utf-8"))
    requirement = contract["context"]["core_validation_requirement"]
    tag = str(_jobs()["dependency-pins"]["uses"]).removeprefix(WORKFLOW)
    assert requirement == (f"omnibase-core @ git+https://github.com/{CORE}@{tag}")
    runs = "\n".join(step.get("run", "") for step in job["steps"])
    assert f'"${variable}"' in runs
    assert '--with "$(uv run --no-project --with pyyaml python -c' in runs
    assert "core_validation_requirement" in runs


def test_lifecycle_job_installs_the_same_contract() -> None:
    jobs = _jobs()
    overlay = jobs["canonical-file-shape"]["env"]["CANONICAL_FILE_SHAPE_CORE"]
    runs = "\n".join(
        step.get("run", "")
        for step in jobs["no-noncanonical-lifecycle-classes"]["steps"]
    )
    assert overlay in runs
    assert "core_validation_requirement" in runs


def test_shape_gate_consumes_the_exported_core_runtime() -> None:
    hooks = [
        hook
        for entry in _core_repos()
        for hook in entry["hooks"]
        if hook["id"] == "check-shape-gate-independence"
    ]
    assert hooks == [{"id": "check-shape-gate-independence"}]
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/shape-gate-independence.yml").read_text(
            encoding="utf-8"
        )
    )
    run = workflow["jobs"]["shape-gate-independence"]["steps"][-1]["run"]
    assert (
        "omnibase_core.nodes.node_shape_gate_independence_check_effect."
        "runtime_shape_gate_independence" in run
    )
    overlay = _jobs()["canonical-file-shape"]["env"]["CANONICAL_FILE_SHAPE_CORE"]
    assert overlay in run
    assert "core_validation_requirement" in run


def test_validator_spec_declares_emits_for_every_entry() -> None:
    spec = yaml.safe_load(
        (ROOT / "architecture-handshakes/validator-requirements.yaml").read_text(
            encoding="utf-8"
        )
    )
    for entry in spec["required_validators"].values():
        assert entry["emits"] in {"required", "exempt"}
        if entry["emits"] == "exempt":
            assert entry["emits_exempt_reason"]


def test_ci_summary_needs_dependency_pins() -> None:
    summary = _jobs()["ci-summary"]
    assert "dependency-pins" in summary["needs"]
    assert summary["if"] == "always()"


@pytest.mark.parametrize(
    "result", ["success", "failure", "cancelled", "skipped", "", "unexpected"]
)
def test_ci_summary_accepts_only_success(result: str) -> None:
    """Execute the gate with every other job green and a varied pin verdict."""
    step = _jobs()["ci-summary"]["steps"][0]
    env = {**os.environ, **dict.fromkeys(step["env"], "success")}
    pin_env = [
        key
        for key, value in step["env"].items()
        if value == "${{ needs.dependency-pins.result }}"
    ]
    assert len(pin_env) == 1
    env[pin_env[0]] = result
    bash = shutil.which("bash")
    assert bash is not None
    run = subprocess.run(
        [bash, "-e", "-c", step["run"]],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert (run.returncode == 0) == (result == "success"), run.stdout + run.stderr
    if result != "success":
        assert "dependency-pins" in run.stdout
