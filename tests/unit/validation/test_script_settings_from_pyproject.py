# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Validation scripts read their timeouts and pin pairs from pyproject.toml (OMN-21623)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATION_SCRIPTS = REPO_ROOT / "scripts" / "validation"
sys.path.insert(0, str(VALIDATION_SCRIPTS))

import run_all_validations
import timeout_utils
import validate_precommit_pin_parity

pytestmark = pytest.mark.unit

SETTING_KEYS = (
    "validator_timeout_seconds",
    "timer_join_grace_seconds",
    "file_operation_timeout_seconds",
)


@pytest.mark.parametrize("key", SETTING_KEYS)
def test_setting_is_declared_in_pyproject(key: str) -> None:
    assert timeout_utils.load_script_setting(key) > 0


def test_missing_setting_fails_loud(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.omnibase_spi.validation_scripts]\n", encoding="utf-8")
    with pytest.raises(KeyError, match="validator_timeout_seconds"):
        timeout_utils.load_script_setting("validator_timeout_seconds", pyproject)


def test_missing_table_fails_loud(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool]\n", encoding="utf-8")
    with pytest.raises(KeyError, match="omnibase_spi"):
        timeout_utils.load_script_setting("validator_timeout_seconds", pyproject)


def test_runner_timeout_comes_from_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def fake_run(_cmd: list[str], **kwargs: object) -> object:
        seen.update(kwargs)
        raise RuntimeError("stop")

    monkeypatch.setattr(run_all_validations.subprocess, "run", fake_run)
    monkeypatch.setattr(run_all_validations, "load_script_setting", lambda _key: 7)
    config = run_all_validations.VALIDATORS[0]
    run_all_validations.run_validator(config, REPO_ROOT)
    assert seen["timeout"] == 7


def test_file_operation_default_timeout_comes_from_setting(tmp_path: Path) -> None:
    target = tmp_path / "f.txt"
    target.write_text("x", encoding="utf-8")
    assert timeout_utils.safe_file_operation(target, lambda p: p.read_text()) == "x"


def test_pin_pairs_come_from_pyproject() -> None:
    pairs = timeout_utils.load_script_setting("precommit_pin_pairs")
    assert pairs
    for hook_id, repo_url, ci_workflow, validator in pairs:
        assert hook_id and validator
        assert repo_url.startswith("https://")
        assert (REPO_ROOT / ci_workflow).is_file()


def test_pin_parity_script_passes_on_this_repository() -> None:
    assert validate_precommit_pin_parity.main() == 0


def test_timeout_fires_when_the_operation_outlives_it() -> None:
    with (
        pytest.raises(timeout_utils.TimeoutError),
        timeout_utils.timeout_context("general", 1),
    ):
        time.sleep(2)


def test_timeout_does_not_fire_when_the_operation_finishes() -> None:
    with timeout_utils.timeout_context("general", 2):
        time.sleep(0.1)


def test_runner_timeout_message_names_the_configured_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(_cmd: list[str], **_kwargs: object) -> object:
        raise run_all_validations.subprocess.TimeoutExpired("v", 7)

    monkeypatch.setattr(run_all_validations.subprocess, "run", fake_run)
    result = run_all_validations.run_validator(
        run_all_validations.VALIDATORS[0], REPO_ROOT
    )
    assert result.error == "Validator timed out after 7 seconds"
