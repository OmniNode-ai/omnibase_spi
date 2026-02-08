"""Tests that contracts do NOT import from omnibase_core, omnibase_infra, or omniclaude.

This is a critical architectural guardrail: all Contract* classes must be
standalone Pydantic models with zero heavy imports.
"""

import ast
import pathlib

import pytest

# Root of the contracts source tree
CONTRACTS_ROOT = (
    pathlib.Path(__file__).resolve().parents[3] / "src" / "omnibase_spi" / "contracts"
)

FORBIDDEN_PREFIXES = ("omnibase_core", "omnibase_infra", "omniclaude")


def _collect_python_files() -> list[pathlib.Path]:
    """Collect all .py files under the contracts directory."""
    return sorted(CONTRACTS_ROOT.rglob("*.py"))


@pytest.mark.unit
class TestNoForbiddenImports:
    """Verify no contracts import from forbidden packages."""

    @pytest.mark.parametrize(
        "py_file",
        _collect_python_files(),
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_no_forbidden_imports(self, py_file: pathlib.Path) -> None:
        """Check that a contract file does not import forbidden packages."""
        source = py_file.read_text()
        tree = ast.parse(source, filename=str(py_file))

        violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(FORBIDDEN_PREFIXES):
                        violations.append(f"import {alias.name} (line {node.lineno})")
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith(FORBIDDEN_PREFIXES)
            ):
                violations.append(f"from {node.module} import ... (line {node.lineno})")

        assert not violations, (
            f"Forbidden imports in {py_file.relative_to(CONTRACTS_ROOT)}:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


@pytest.mark.unit
class TestSchemaVersionPresent:
    """Verify every Contract* model has a schema_version field."""

    @pytest.mark.parametrize(
        "py_file",
        [
            f
            for f in _collect_python_files()
            if f.name.startswith("contract_") and not f.name.startswith("__")
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_schema_version_field(self, py_file: pathlib.Path) -> None:
        """Each contract file should contain 'schema_version' as a field."""
        source = py_file.read_text()
        assert (
            "schema_version" in source
        ), f"{py_file.relative_to(CONTRACTS_ROOT)} is missing schema_version field"


@pytest.mark.unit
class TestFrozenConfig:
    """Verify every Contract* model uses frozen=True."""

    @pytest.mark.parametrize(
        "py_file",
        [
            f
            for f in _collect_python_files()
            if f.name.startswith("contract_") and not f.name.startswith("__")
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_frozen_config(self, py_file: pathlib.Path) -> None:
        """Each contract file should have frozen=True in model_config."""
        source = py_file.read_text()
        assert (
            '"frozen": True' in source or "'frozen': True" in source
        ), f"{py_file.relative_to(CONTRACTS_ROOT)} is missing frozen=True config"


@pytest.mark.unit
class TestExtraAllow:
    """Verify every Contract* model uses extra='allow' for forward compat."""

    @pytest.mark.parametrize(
        "py_file",
        [
            f
            for f in _collect_python_files()
            if f.name.startswith("contract_") and not f.name.startswith("__")
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_extra_allow(self, py_file: pathlib.Path) -> None:
        """Each contract file should have extra='allow' in model_config."""
        source = py_file.read_text()
        assert (
            '"extra": "allow"' in source or "'extra': 'allow'" in source
        ), f"{py_file.relative_to(CONTRACTS_ROOT)} is missing extra='allow' config"
