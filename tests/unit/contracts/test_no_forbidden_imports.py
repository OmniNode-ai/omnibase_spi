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

# Utility modules that start with "contract_" but are NOT Pydantic model files.
_NON_MODEL_UTILITIES = frozenset(
    {
        "contract_wire_codec.py",
        "contract_schema_compat.py",
    }
)

# Directories containing contracts that deliberately use extra="forbid"
# instead of extra="allow".  Measurement and delegation contracts use
# forbid + explicit extensions field for high-integrity gating data.
_EXTRA_FORBID_DIRS = frozenset({"measurement", "delegation", "enrichment"})


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
            if f.name.startswith("contract_")
            and not f.name.startswith("__")
            and f.name not in _NON_MODEL_UTILITIES
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_schema_version_field(self, py_file: pathlib.Path) -> None:
        """Each contract file should contain 'schema_version' as a field."""
        source = py_file.read_text()
        assert "schema_version" in source, (
            f"{py_file.relative_to(CONTRACTS_ROOT)} is missing schema_version field"
        )


@pytest.mark.unit
class TestFrozenConfig:
    """Verify every Contract* model uses frozen=True."""

    @pytest.mark.parametrize(
        "py_file",
        [
            f
            for f in _collect_python_files()
            if f.name.startswith("contract_")
            and not f.name.startswith("__")
            and f.name not in _NON_MODEL_UTILITIES
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_frozen_config(self, py_file: pathlib.Path) -> None:
        """Each contract file should have frozen=True in model_config."""
        source = py_file.read_text()
        has_frozen = (
            '"frozen": True' in source
            or "'frozen': True" in source
            or "frozen=True" in source
        )
        assert has_frozen, (
            f"{py_file.relative_to(CONTRACTS_ROOT)} is missing frozen=True config"
        )


@pytest.mark.unit
class TestExtraAllow:
    """Verify every Contract* model uses the correct extra policy.

    Most contracts use ``extra="allow"`` for forward compatibility.
    Measurement contracts use ``extra="forbid"`` with an explicit
    ``extensions`` field for high-integrity gating data.
    """

    @pytest.mark.parametrize(
        "py_file",
        [
            f
            for f in _collect_python_files()
            if f.name.startswith("contract_")
            and not f.name.startswith("__")
            and f.name not in _NON_MODEL_UTILITIES
            and not any(
                part in _EXTRA_FORBID_DIRS
                for part in f.relative_to(CONTRACTS_ROOT).parts
            )
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_extra_allow(self, py_file: pathlib.Path) -> None:
        """Each non-measurement contract file should have extra='allow' in model_config."""
        source = py_file.read_text()
        assert '"extra": "allow"' in source or "'extra': 'allow'" in source, (
            f"{py_file.relative_to(CONTRACTS_ROOT)} is missing extra='allow' config"
        )

    @pytest.mark.parametrize(
        "py_file",
        [
            f
            for f in _collect_python_files()
            if f.name.startswith("contract_")
            and not f.name.startswith("__")
            and f.name not in _NON_MODEL_UTILITIES
            and any(
                part in _EXTRA_FORBID_DIRS
                for part in f.relative_to(CONTRACTS_ROOT).parts
            )
        ],
        ids=lambda p: str(p.relative_to(CONTRACTS_ROOT)),
    )
    def test_extra_forbid_with_extensions(self, py_file: pathlib.Path) -> None:
        """Measurement/delegation contracts must use extra='forbid' and have an extensions field."""
        source = py_file.read_text()
        has_forbid = (
            '"extra": "forbid"' in source
            or "'extra': 'forbid'" in source
            or 'extra="forbid"' in source
        )
        has_extensions = "extensions:" in source or "extensions :" in source
        assert has_forbid, (
            f"{py_file.relative_to(CONTRACTS_ROOT)} is missing extra='forbid' config"
        )
        assert has_extensions, (
            f"{py_file.relative_to(CONTRACTS_ROOT)} is missing extensions field"
        )
