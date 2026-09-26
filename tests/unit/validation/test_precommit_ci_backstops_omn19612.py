# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Whole-tree CI ratchets for staged-only validators changed by OMN-19612."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from scripts.ci.detect_test_paths import compute_selection

REPO_ROOT = Path(__file__).resolve().parents[3]
PRECOMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_CHECKS = REPO_ROOT / ".github" / "required-checks.yaml"
ADJACENCY_PATH = REPO_ROOT / "scripts" / "ci" / "test_selection_adjacency.yaml"
HOOK_SCRIPT = REPO_ROOT / ".pre-commit-hooks" / "reject-required-check-skip-vector.sh"
PIN_TEST_PATH = "tests/unit/validation/test_precommit_ci_backstops_omn19612.py"

JOB_ID = "spi-validation-gate"
JOB_NAME = "SPI Validation Gate"
FETCH_STEP_NAME = "Fetch skip-vector validator (omniclaude canonical source)"
VALIDATOR_FILENAME = "validate_no_required_check_skip_vectors.py"
WORKFLOW_MODEL_FILENAME = "_workflow_model.py"

pytestmark = pytest.mark.unit


def _load_mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def _workflow() -> dict[str, Any]:
    return _load_mapping(CI_WORKFLOW)


def _job() -> dict[str, Any]:
    jobs = cast("dict[str, dict[str, Any]]", _workflow()["jobs"])
    job = jobs[JOB_ID]
    assert job["name"] == JOB_NAME
    return job


def _suite_step() -> dict[str, Any]:
    steps = cast("list[dict[str, Any]]", _job()["steps"])
    matches = [
        step
        for step in steps
        if "pre-commit run --all-files" in str(step.get("run", ""))
    ]
    assert len(matches) == 1, (
        f"expected one whole-tree pre-commit step in {JOB_ID}, found {len(matches)}"
    )
    return matches[0]


def _validator_fetch_step() -> dict[str, Any]:
    steps = cast("list[dict[str, Any]]", _job()["steps"])
    matches = [step for step in steps if step.get("name") == FETCH_STEP_NAME]
    assert len(matches) == 1, (
        f"expected one {FETCH_STEP_NAME!r} step in {JOB_ID}, found {len(matches)}"
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
    assert "if" not in job
    assert "needs" not in job
    assert job.get("continue-on-error") is not True

    for step in job["steps"]:
        if str(step.get("uses", "")).startswith("actions/upload-artifact"):
            continue
        assert "if" not in step, (
            f"{step.get('name', step.get('uses'))} must be unconditional"
        )
        assert step.get("continue-on-error") is not True, (
            f"{step.get('name', step.get('uses'))} must be blocking"
        )


def test_validator_fetch_precedes_and_configures_whole_tree_step() -> None:
    job = _job()
    fetch_step = _validator_fetch_step()
    suite_step = _suite_step()

    assert job["steps"].index(fetch_step) < job["steps"].index(suite_step)
    assert fetch_step["uses"] == "actions/checkout@v7"
    checkout = fetch_step["with"]
    assert checkout["repository"] == "OmniNode-ai/omniclaude"
    assert checkout["ref"] == "dev"
    assert checkout["persist-credentials"] is False
    assert checkout["sparse-checkout-cone-mode"] is False

    sparse_checkout = {
        path.strip() for path in str(checkout["sparse-checkout"]).splitlines()
    }
    guard_path = ".github/actions/required-check-skip-guard"
    assert f"{guard_path}/{VALIDATOR_FILENAME}" in sparse_checkout
    assert f"{guard_path}/{WORKFLOW_MODEL_FILENAME}" in sparse_checkout

    checkout_path = str(checkout["path"])
    validator_path = str(
        suite_step.get("env", {}).get("REQUIRED_CHECK_SKIP_GUARD_VALIDATOR", "")
    )
    assert validator_path.startswith(f"${{{{ github.workspace }}}}/{checkout_path}/")
    assert validator_path.endswith(f"/{VALIDATOR_FILENAME}")


def test_required_check_skip_hook_remains_installed_for_pre_commit() -> None:
    config = _load_mapping(PRECOMMIT_CONFIG)
    default_stages = config.get("default_stages", ["pre-commit"])
    matches = [
        hook
        for repository in config["repos"]
        for hook in repository.get("hooks", [])
        if hook.get("id") == "reject-required-check-skip-vector"
    ]
    assert len(matches) == 1
    stages = matches[0].get("stages", default_stages)
    assert isinstance(stages, list)
    assert "pre-commit" in stages


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


def test_test_jobs_are_fail_closed_and_summary_wired() -> None:
    jobs = _workflow()["jobs"]
    assert "if" not in jobs["test-parallel"]
    assert jobs["tests-gate"]["if"] == "always()"
    assert "test-parallel" in jobs["tests-gate"]["needs"]
    assert "tests-gate" in jobs["ci-summary"]["needs"]


def test_pin_test_is_selected_for_ci_configuration_changes() -> None:
    config_paths = [
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
        ".pre-commit-hooks/reject-required-check-skip-vector.sh",
    ]
    source_path = "src/omnibase_spi/factories/factory_something.py"

    for config_path in config_paths:
        for changed_files in ([config_path], [config_path, source_path]):
            selection = compute_selection(
                changed_files=changed_files,
                adjacency_path=ADJACENCY_PATH,
                ref_name="feature/x",
                event_name="pull_request",
                feature_flag_enabled=True,
            )
            assert any(
                path == PIN_TEST_PATH
                or (path.endswith("/") and PIN_TEST_PATH.startswith(path))
                for path in selection.selected_paths
            ), f"{changed_files} selected {selection.selected_paths}"


def test_workflow_has_no_pull_request_paths_filter() -> None:
    workflow = cast("dict[object, Any]", _workflow())
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


def _run_skip_vector_hook(
    validator: Path | None,
    *,
    include_override: bool = True,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("OMNI_HOME", None)
    env.pop("REQUIRED_CHECK_SKIP_GUARD_VALIDATOR", None)
    env["PYTHON_BIN"] = sys.executable
    if include_override:
        assert validator is not None
        env["REQUIRED_CHECK_SKIP_GUARD_VALIDATOR"] = str(validator)
    return subprocess.run(
        [str(HOOK_SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(("stub_exit", "expected_exit"), [(0, 0), (3, 3)])
def test_skip_vector_hook_propagates_override_validator_exit(
    tmp_path: Path,
    stub_exit: int,
    expected_exit: int,
) -> None:
    validator = tmp_path / VALIDATOR_FILENAME
    validator.write_text(f"import sys\nsys.exit({stub_exit})\n", encoding="utf-8")

    result = _run_skip_vector_hook(validator)

    assert result.returncode == expected_exit


def test_skip_vector_hook_rejects_missing_override(tmp_path: Path) -> None:
    result = _run_skip_vector_hook(tmp_path / VALIDATOR_FILENAME)

    assert result.returncode == 1


def test_skip_vector_hook_requires_omni_home_without_override() -> None:
    result = _run_skip_vector_hook(None, include_override=False)

    assert result.returncode == 1
    assert "OMNI_HOME" in result.stderr
