# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Whole-tree CI ratchets for staged-only validators changed by OMN-19612."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PRECOMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_CHECKS = REPO_ROOT / ".github" / "required-checks.yaml"

JOB_ID = "spi-validation-gate"
JOB_NAME = "SPI Validation Gate"

pytestmark = pytest.mark.unit


def _load_mapping(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def _workflow() -> dict:
    return _load_mapping(CI_WORKFLOW)


def _job() -> dict:
    job = _workflow()["jobs"][JOB_ID]
    assert job["name"] == JOB_NAME
    return job


def _suite_step() -> dict:
    matches = [
        step
        for step in _job()["steps"]
        if "pre-commit run --all-files" in str(step.get("run", ""))
    ]
    assert len(matches) == 1, (
        f"expected one whole-tree pre-commit step in {JOB_ID}, found {len(matches)}"
    )
    return matches[0]


def _staged_scoped_hook_ids() -> set[str]:
    """Return pre-commit-stage hooks whose file input is the staged diff."""
    config = _load_mapping(PRECOMMIT_CONFIG)
    default_stages = config.get("default_stages", ["pre-commit"])
    hook_ids: set[str] = set()
    for repository in config["repos"]:
        for hook in repository.get("hooks", []):
            stages = hook.get("stages", default_stages)
            if "pre-commit" not in stages:
                continue
            if hook.get("pass_filenames", True) is False:
                continue
            hook_ids.add(str(hook["id"]))
    return hook_ids


def test_every_staged_scoped_hook_has_whole_tree_coverage() -> None:
    staged_ids = _staged_scoped_hook_ids()
    assert staged_ids, "expected at least one staged-file-scoped hook"

    step = _suite_step()
    command = str(step["run"])
    job_env = _job().get("env", {})
    step_env = step.get("env", {})
    assert "SKIP" not in job_env
    assert "SKIP" not in step_env
    assert "SKIP=" not in command

    for hook_id in sorted(staged_ids):
        assert "pre-commit run --all-files" in command, (
            f"{hook_id} is staged-file-scoped but has no whole-tree counterpart"
        )


def test_whole_tree_job_and_step_are_unconditional_and_blocking() -> None:
    job = _job()
    step = _suite_step()
    assert "if" not in job
    assert "needs" not in job
    assert job.get("continue-on-error") is not True
    assert "if" not in step
    assert step.get("continue-on-error") is not True


def test_whole_tree_job_is_required_and_summary_wired() -> None:
    manifest = _load_mapping(REQUIRED_CHECKS)
    matching_gates = [
        gate
        for gate in manifest["gates"]
        if gate.get("name") == JOB_NAME and gate.get("job_path") == [JOB_ID]
    ]
    assert len(matching_gates) == 1
    assert matching_gates[0]["mode"] == "REQUIRED"

    summary = _workflow()["jobs"]["ci-summary"]
    assert JOB_ID in summary["needs"]


def test_workflow_has_no_pull_request_paths_filter() -> None:
    workflow = _workflow()
    triggers = workflow[True] if True in workflow else workflow["on"]
    pull_request = triggers.get("pull_request") or {}
    assert "paths" not in pull_request
    assert "paths-ignore" not in pull_request


def test_namespace_shell_guard_only_checks_supplied_files(tmp_path: Path) -> None:
    script = REPO_ROOT / "scripts" / "validate-namespace-isolation.sh"
    clean = tmp_path / "clean.py"
    dirty = tmp_path / "dirty.py"
    clean.write_text("value = 1\n", encoding="utf-8")
    dirty.write_text("from omnibase.forbidden import value\n", encoding="utf-8")

    clean_run = subprocess.run([str(script), str(clean)], check=False)
    dirty_run = subprocess.run([str(script), str(dirty)], check=False)

    assert clean_run.returncode == 0
    assert dirty_run.returncode == 1
