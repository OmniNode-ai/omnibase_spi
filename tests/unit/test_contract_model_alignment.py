"""SPI contract → Core model field alignment tests.

Asserts that SPI contract fields ⊆ Core model fields for all three event
types defined in OMN-2655.

These tests are gated on the availability of omnibase_core models.  When
Part 2 (OMN-2655 omnibase_core scope) has not yet been merged, the Core
models do not exist and the tests are auto-skipped with an informative
message.

Once omnibase_core ships ``ModelGitHubPRStatusEvent``,
``ModelGitHookEvent``, and ``ModelLinearSnapshotEvent``, these tests will
run and enforce the alignment invariant.

Run with:
    uv run pytest tests/unit/test_contract_model_alignment.py -m unit
"""

from __future__ import annotations

import importlib

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CORE_MODELS_AVAILABLE = False
try:
    _core = importlib.import_module("omnibase_core.models.events")
    # All three Core models must be present for alignment tests to run
    _CORE_MODELS_AVAILABLE = all(
        hasattr(_core, name)
        for name in (
            "ModelGitHubPRStatusEvent",
            "ModelGitHookEvent",
            "ModelLinearSnapshotEvent",
        )
    )
except ModuleNotFoundError:
    pass

_skip_reason = (
    "omnibase_core.models.events does not yet export ModelGitHubPRStatusEvent, "
    "ModelGitHookEvent, ModelLinearSnapshotEvent — "
    "skipping alignment tests until Part 2 (omnibase_core scope) is merged"
)


def _get_contract_fields(cls: type) -> set[str]:
    """Return the set of declared field names for a Pydantic model class."""
    return set(cls.model_fields.keys())


def _get_core_model_fields(class_name: str) -> set[str]:
    """Return the set of declared field names for a Core model class."""
    core = importlib.import_module("omnibase_core.models.events")
    cls = getattr(core, class_name)
    return set(cls.model_fields.keys())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.skipif(not _CORE_MODELS_AVAILABLE, reason=_skip_reason)
class TestGitHubPRStatusAlignment:
    """ContractGitHubPRStatusEvent fields ⊆ ModelGitHubPRStatusEvent fields."""

    def test_spi_fields_subset_of_core_fields(self) -> None:
        """Every field on ContractGitHubPRStatusEvent must exist on the Core model."""
        from omnibase_spi.contracts.events.contract_github_pr_status_event import (
            ContractGitHubPRStatusEvent,
        )

        spi_fields = _get_contract_fields(ContractGitHubPRStatusEvent)
        core_fields = _get_core_model_fields("ModelGitHubPRStatusEvent")

        # Exclude metadata-only fields that live only in SPI
        spi_domain_fields = spi_fields - {"schema_version", "extensions"}

        extra = spi_domain_fields - core_fields
        assert not extra, (
            f"SPI ContractGitHubPRStatusEvent has fields not in Core model: {extra}"
        )


@pytest.mark.unit
@pytest.mark.skipif(not _CORE_MODELS_AVAILABLE, reason=_skip_reason)
class TestGitHookAlignment:
    """ContractGitHookEvent fields ⊆ ModelGitHookEvent fields."""

    def test_spi_fields_subset_of_core_fields(self) -> None:
        """Every field on ContractGitHookEvent must exist on the Core model."""
        from omnibase_spi.contracts.events.contract_git_hook_event import (
            ContractGitHookEvent,
        )

        spi_fields = _get_contract_fields(ContractGitHookEvent)
        core_fields = _get_core_model_fields("ModelGitHookEvent")

        spi_domain_fields = spi_fields - {"schema_version", "extensions"}

        extra = spi_domain_fields - core_fields
        assert not extra, (
            f"SPI ContractGitHookEvent has fields not in Core model: {extra}"
        )


@pytest.mark.unit
@pytest.mark.skipif(not _CORE_MODELS_AVAILABLE, reason=_skip_reason)
class TestLinearSnapshotAlignment:
    """ContractLinearSnapshotEvent fields ⊆ ModelLinearSnapshotEvent fields."""

    def test_spi_fields_subset_of_core_fields(self) -> None:
        """Every field on ContractLinearSnapshotEvent must exist on the Core model."""
        from omnibase_spi.contracts.events.contract_linear_snapshot_event import (
            ContractLinearSnapshotEvent,
        )

        spi_fields = _get_contract_fields(ContractLinearSnapshotEvent)
        core_fields = _get_core_model_fields("ModelLinearSnapshotEvent")

        spi_domain_fields = spi_fields - {"schema_version", "extensions"}

        extra = spi_domain_fields - core_fields
        assert not extra, (
            f"SPI ContractLinearSnapshotEvent has fields not in Core model: {extra}"
        )


@pytest.mark.unit
class TestAlignmentSmokeWhenCoreUnavailable:
    """Smoke test that runs regardless of Core model availability.

    Verifies that contract imports work and the alignment test module itself
    is importable.
    """

    def test_contract_github_pr_status_importable(self) -> None:
        """ContractGitHubPRStatusEvent is importable from omnibase_spi."""
        from omnibase_spi.contracts.events.contract_github_pr_status_event import (
            ContractGitHubPRStatusEvent,
        )

        assert ContractGitHubPRStatusEvent is not None

    def test_contract_git_hook_importable(self) -> None:
        """ContractGitHookEvent is importable from omnibase_spi."""
        from omnibase_spi.contracts.events.contract_git_hook_event import (
            ContractGitHookEvent,
        )

        assert ContractGitHookEvent is not None

    def test_contract_linear_snapshot_importable(self) -> None:
        """ContractLinearSnapshotEvent is importable from omnibase_spi."""
        from omnibase_spi.contracts.events.contract_linear_snapshot_event import (
            ContractLinearSnapshotEvent,
        )

        assert ContractLinearSnapshotEvent is not None
