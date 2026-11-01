# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""The pin-resolvability gate reads its wall-clock budgets from pyproject.toml (OMN-21739).

``scripts/ci/verify_pypi_pin_resolvability.py`` held the ``uv venv`` budget as a
code literal and the ``uv pip install`` budget as an environment default literal.
Both are now declared under ``[tool.omnibase_spi.validation_scripts]`` in
pyproject.toml and read at call time; the install budget can still be overridden
by its environment variable from the workflow. An absent table or key raises
``KeyError``: there is no in-code default.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

import pytest

import scripts.ci.verify_pypi_pin_resolvability as pin_gate

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "ci" / "verify_pypi_pin_resolvability.py"


def _declared(key: str) -> int:
    data = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return int(data["tool"]["omnibase_spi"]["validation_scripts"][key])


def _timeouts_used(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[object]:
    """Run the gate with ``subprocess.run`` faked; return the timeout of each call."""
    seen: list[object] = []

    def fake_run(*_args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        seen.append(kwargs["timeout"])
        return subprocess.CompletedProcess([], 0, "", "")

    monkeypatch.setattr(pin_gate, "_resolve_uv", lambda: "uv")
    monkeypatch.setattr(pin_gate.subprocess, "run", fake_run)
    wheel = tmp_path / "x-1-py3-none-any.whl"
    wheel.write_bytes(b"")
    pin_gate.verify_pin_resolvability(wheel)
    return seen


@pytest.mark.unit
def test_budgets_are_the_declared_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("PYPI_PIN_RESOLVE_TIMEOUT_SECONDS", raising=False)
    assert _timeouts_used(monkeypatch, tmp_path)[:2] == [
        _declared("pin_resolve_venv_timeout_seconds"),
        _declared("pin_resolve_install_timeout_seconds"),
    ]


@pytest.mark.unit
def test_environment_overrides_the_install_budget(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PYPI_PIN_RESOLVE_TIMEOUT_SECONDS", "2400")
    assert _timeouts_used(monkeypatch, tmp_path)[1] == 2400


@pytest.mark.unit
def test_absent_key_raises_key_error(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.omnibase_spi.validation_scripts]\n", encoding="utf-8")
    with pytest.raises(KeyError, match="pin_resolve_venv_timeout_seconds"):
        pin_gate.load_script_setting("pin_resolve_venv_timeout_seconds", pyproject)


@pytest.mark.unit
def test_absent_table_raises_key_error(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'x'\n", encoding="utf-8")
    with pytest.raises(KeyError, match="tool"):
        pin_gate.load_script_setting("pin_resolve_install_timeout_seconds", pyproject)


@pytest.mark.unit
def test_script_holds_no_budget_literal() -> None:
    text = _SCRIPT.read_text(encoding="utf-8")
    assert "_VENV_TIMEOUT_SECONDS = " not in text
    assert "_INSTALL_TIMEOUT_SECONDS = " not in text
    assert '"1800"' not in text
