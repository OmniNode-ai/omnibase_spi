# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Whole-tree CI ratchets for staged-only validators changed by OMN-19612."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PRECOMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"

pytestmark = pytest.mark.unit


def _hook_script_path(hook_id: str) -> str:
    config = PRECOMMIT_CONFIG.read_text(encoding="utf-8")
    hook = re.search(
        rf"(?ms)^      - id: {re.escape(hook_id)}\n(?P<body>.*?)(?=^      - id:|\Z)",
        config,
    )
    assert hook is not None, f"missing pre-commit hook: {hook_id}"

    entry = re.search(r"(?m)^        entry:\s*(?P<entry>.+)$", hook["body"])
    assert entry is not None, f"missing entry for pre-commit hook: {hook_id}"

    script = re.search(r"(?:\.?/)?(?:[\w.-]+/)+[\w.-]+\.(?:py|sh)", entry["entry"])
    assert script is not None, f"hook entry has no script path: {hook_id}"
    return script.group(0).removeprefix("./")


def _spi_validation_gate_commands() -> list[str]:
    workflow = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    job = workflow["jobs"]["spi-validation-gate"]
    assert job["name"] == "SPI Validation Gate"
    return [step["run"] for step in job["steps"] if "run" in step]


@pytest.mark.parametrize(
    ("hook_id", "expected_script"),
    [
        (
            "validate-spi-typing-patterns",
            "scripts/validation/validate_spi_typing_patterns.py",
        ),
        (
            "validate-spi-naming-conventions",
            "scripts/validation/validate_spi_naming.py",
        ),
        ("validate-namespace-isolation", "scripts/validate-namespace-isolation.sh"),
    ],
)
def test_staged_hook_has_whole_tree_ci_backstop(
    hook_id: str, expected_script: str
) -> None:
    script = _hook_script_path(hook_id)
    commands = "\n".join(_spi_validation_gate_commands())

    assert script == expected_script
    assert script in commands, (
        f"{hook_id} has no whole-tree CI backstop in spi-validation-gate"
    )


@pytest.mark.parametrize(
    ("hook_id", "expected_script"),
    [
        (
            "validate-naming-patterns",
            "scripts/validation/validate_naming_patterns.py",
        ),
        (
            "validate-namespace-isolation-new",
            "scripts/validation/validate_namespace_isolation.py",
        ),
    ],
)
def test_unified_staged_hook_has_strict_required_ci_backstop(
    hook_id: str, expected_script: str
) -> None:
    script = _hook_script_path(hook_id)
    unified_commands = [
        command
        for command in _spi_validation_gate_commands()
        if "scripts/validation/run_all_validations.py" in command
    ]

    assert script == expected_script
    assert len(unified_commands) == 1
    assert "--strict" in unified_commands[0].split()


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
