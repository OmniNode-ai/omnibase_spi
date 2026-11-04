# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Values the hardcoded-model-config hook found now come from data (OMN-22360).

The scripts take the repository location as an argument, and the budgets that sat
as literals in workflows and ``validation_config.yaml`` are declared under
``[tool.omnibase_spi.validation_scripts]`` in pyproject.toml.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "validation"))

import check_unused_exports
import timeout_utils
import validate_precommit_fail_loud

pytestmark = pytest.mark.unit

MOVED_SETTINGS = {
    "file_analysis_timeout_seconds": 30,
    "ast_parsing_timeout_seconds": 10,
    "rule_execution_timeout_seconds": 5,
    "uv_http_timeout_seconds": 600,
    "pin_resolve_gate_install_timeout_seconds": 900,
}


@pytest.mark.parametrize(("key", "value"), sorted(MOVED_SETTINGS.items()))
def test_moved_budget_keeps_its_value(key: str, value: int) -> None:
    assert timeout_utils.load_script_setting(key) == value


def test_validation_config_holds_no_timeout_literal() -> None:
    config = yaml.safe_load((REPO_ROOT / "validation_config.yaml").read_text("utf-8"))
    assert not [k for k in config["performance"] if k.endswith("_timeout_seconds")]


def test_unused_exports_takes_the_repository_root_as_argument(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    results = check_unused_exports.check_unused_exports(
        allowlist_path=REPO_ROOT / "scripts" / "export_allowlist.txt",
        repo_root=REPO_ROOT,
    )
    assert len(results) >= 150


def test_fail_loud_takes_the_repository_root_as_argument(tmp_path: Path) -> None:
    assert validate_precommit_fail_loud.main(tmp_path) == 1
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "default_install_hook_types: [pre-commit]\nrepos: []\n", encoding="utf-8"
    )
    assert validate_precommit_fail_loud.main(tmp_path) == 0


def test_fail_loud_passes_on_this_repository() -> None:
    assert validate_precommit_fail_loud.main(REPO_ROOT) == 0


def _workflow(name: str) -> str:
    return (REPO_ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")


def test_contract_validation_reads_the_uv_http_budget_from_pyproject() -> None:
    text = _workflow("contract-validation.yml")
    assert 'UV_HTTP_TIMEOUT: "600"' not in text
    assert "uv_http_timeout_seconds" in text


def test_pin_gate_reads_the_install_budget_from_pyproject() -> None:
    text = _workflow("pin-resolvability-gate.yml")
    assert "PYPI_PIN_RESOLVE_TIMEOUT_SECONDS: '900'" not in text
    assert "pin_resolve_gate_install_timeout_seconds" in text


def test_namespace_validation_builds_the_core_url_from_the_runner_context() -> None:
    assert "git+https://github.com/OmniNode-ai" not in _workflow(
        "namespace-validation.yml"
    )
