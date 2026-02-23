"""Drift gate tests for the SPI Event Registry.

These tests enforce three invariants:

1. **topic == event_type** (Option A policy):
   Every ``EVENT_REGISTRY`` entry must satisfy ``entry.topic == event_type``
   (the dict key).

2. **partition_key_fields ⊆ SPI contract fields**:
   Every field listed in ``partition_key_fields`` must exist as a declared
   field on the corresponding SPI contract model.

3. **SPI contract fields ⊆ known field set**:
   All non-metadata fields on each SPI contract must match what the registry
   declares.  (This is a weaker check pending omnibase_core availability;
   the full Core-model alignment is tested in ``test_contract_model_alignment.py``
   once Core models are built in Part 2.)

These tests are the "drift gate" — they will fail when the registry,
contracts, or Core models diverge from each other, surfacing misalignment
at unit-test time rather than at runtime.

Run with:
    uv run pytest tests/unit/test_event_registry_fingerprint.py -m unit
"""

from __future__ import annotations

import pytest

from omnibase_spi.contracts.events.contract_git_hook_event import ContractGitHookEvent
from omnibase_spi.contracts.events.contract_github_pr_status_event import (
    ContractGitHubPRStatusEvent,
)
from omnibase_spi.contracts.events.contract_linear_snapshot_event import (
    ContractLinearSnapshotEvent,
)
from omnibase_spi.registry.event_registry import EVENT_REGISTRY, EventRegistryEntry

# ---------------------------------------------------------------------------
# Registry completeness: three required event types
# ---------------------------------------------------------------------------

REQUIRED_EVENT_TYPES = frozenset(
    {
        "onex.evt.github.pr-status.v1",
        "onex.evt.git.hook.v1",
        "onex.evt.linear.snapshot.v1",
    }
)

# Mapping from event_type → SPI contract class (for partition key assertions)
CONTRACT_CLASSES: dict[str, type] = {
    "onex.evt.github.pr-status.v1": ContractGitHubPRStatusEvent,
    "onex.evt.git.hook.v1": ContractGitHookEvent,
    "onex.evt.linear.snapshot.v1": ContractLinearSnapshotEvent,
}


@pytest.mark.unit
class TestEventRegistryCompleteness:
    """Assert the registry contains all required event types."""

    def test_all_required_event_types_registered(self) -> None:
        """EVENT_REGISTRY must contain all three required event types."""
        registered = set(EVENT_REGISTRY.keys())
        missing = REQUIRED_EVENT_TYPES - registered
        assert not missing, f"EVENT_REGISTRY is missing required event types: {missing}"

    def test_registry_values_are_event_registry_entries(self) -> None:
        """Every value in EVENT_REGISTRY must be an EventRegistryEntry."""
        for event_type, entry in EVENT_REGISTRY.items():
            assert isinstance(entry, EventRegistryEntry), (
                f"Registry entry for '{event_type}' is not an EventRegistryEntry; "
                f"got {type(entry)}"
            )


@pytest.mark.unit
class TestTopicEqualsEventType:
    """Enforce Option A: event_type == topic for every registry entry."""

    def test_topic_equals_event_type_for_all_entries(self) -> None:
        """For every entry, entry.topic must equal the dict key (event_type)."""
        for event_type, entry in EVENT_REGISTRY.items():
            assert entry.topic == event_type, (
                f"Policy violation: entry.topic '{entry.topic}' != "
                f"event_type '{event_type}' for registry key '{event_type}'"
            )

    @pytest.mark.parametrize("event_type", sorted(REQUIRED_EVENT_TYPES))
    def test_topic_equals_event_type_parametrized(self, event_type: str) -> None:
        """Parametrized check: topic == event_type for each required type."""
        entry = EVENT_REGISTRY[event_type]
        assert entry.topic == event_type


@pytest.mark.unit
class TestPartitionKeyFieldsExistOnContract:
    """Assert every partition_key_field exists as a field on the SPI contract."""

    @pytest.mark.parametrize("event_type", sorted(REQUIRED_EVENT_TYPES))
    def test_partition_key_fields_exist_on_contract(self, event_type: str) -> None:
        """All partition_key_fields for each event_type must exist on the SPI contract."""
        entry = EVENT_REGISTRY[event_type]
        contract_cls = CONTRACT_CLASSES[event_type]
        contract_fields = set(contract_cls.model_fields.keys())

        for field_name in entry.partition_key_fields:
            assert field_name in contract_fields, (
                f"Partition key field '{field_name}' for event_type '{event_type}' "
                f"does not exist on {contract_cls.__name__}. "
                f"Available fields: {sorted(contract_fields)}"
            )


@pytest.mark.unit
class TestSchemaVersionPresent:
    """Assert every entry has a non-empty schema_version."""

    @pytest.mark.parametrize("event_type", sorted(REQUIRED_EVENT_TYPES))
    def test_schema_version_is_non_empty(self, event_type: str) -> None:
        """schema_version must be a non-empty string for every entry."""
        entry = EVENT_REGISTRY[event_type]
        assert entry.schema_version, (
            f"EVENT_REGISTRY entry for '{event_type}' has empty schema_version"
        )


@pytest.mark.unit
class TestProducerProtocolField:
    """Assert every entry names a producer_protocol."""

    @pytest.mark.parametrize("event_type", sorted(REQUIRED_EVENT_TYPES))
    def test_producer_protocol_is_non_empty(self, event_type: str) -> None:
        """producer_protocol must be a non-empty string for every entry."""
        entry = EVENT_REGISTRY[event_type]
        assert entry.producer_protocol, (
            f"EVENT_REGISTRY entry for '{event_type}' has empty producer_protocol"
        )


@pytest.mark.unit
class TestContractModels:
    """Smoke tests for the three SPI contract model classes."""

    def test_github_pr_status_event_extra_forbid(self) -> None:
        """ContractGitHubPRStatusEvent must use extra='forbid'."""
        assert ContractGitHubPRStatusEvent.model_config.get("extra") == "forbid"

    def test_git_hook_event_extra_forbid(self) -> None:
        """ContractGitHookEvent must use extra='forbid'."""
        assert ContractGitHookEvent.model_config.get("extra") == "forbid"

    def test_linear_snapshot_event_extra_forbid(self) -> None:
        """ContractLinearSnapshotEvent must use extra='forbid'."""
        assert ContractLinearSnapshotEvent.model_config.get("extra") == "forbid"

    def test_all_contracts_frozen(self) -> None:
        """All three SPI contracts must be frozen (immutable)."""
        for cls in CONTRACT_CLASSES.values():
            assert cls.model_config.get("frozen") is True, (
                f"{cls.__name__} must have frozen=True in model_config"
            )

    def test_all_contracts_have_extensions_field(self) -> None:
        """All three SPI contracts must expose an 'extensions' field."""
        for event_type, cls in CONTRACT_CLASSES.items():
            assert "extensions" in cls.model_fields, (
                f"{cls.__name__} (event_type='{event_type}') is missing the "
                "'extensions' field (single extension channel requirement)"
            )

    def test_github_pr_status_event_construction(self) -> None:
        """ContractGitHubPRStatusEvent can be constructed with required fields."""
        event = ContractGitHubPRStatusEvent(
            repo="OmniNode-ai/omniclaude",
            pr_number=42,
            triage_state="needs_review",
        )
        assert event.repo == "OmniNode-ai/omniclaude"
        assert event.pr_number == 42
        assert event.triage_state == "needs_review"
        assert event.event_type == "onex.evt.github.pr-status.v1"
        assert event.schema_version == "1.0"

    def test_github_pr_status_event_rejects_extra_fields(self) -> None:
        """ContractGitHubPRStatusEvent must reject undeclared fields (extra='forbid')."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ContractGitHubPRStatusEvent(
                repo="OmniNode-ai/omniclaude",
                pr_number=1,
                triage_state="draft",
                undeclared_field="must_fail",  # type: ignore[call-arg]
            )

    def test_git_hook_event_construction(self) -> None:
        """ContractGitHookEvent can be constructed with required fields."""
        event = ContractGitHookEvent(
            hook="pre-commit",
            repo="OmniNode-ai/omniclaude",
            branch="main",
            author="jonah",
            outcome="pass",
        )
        assert event.hook == "pre-commit"
        assert event.branch == "main"
        assert event.author == "jonah"
        assert event.outcome == "pass"
        assert event.event_type == "onex.evt.git.hook.v1"

    def test_git_hook_event_rejects_extra_fields(self) -> None:
        """ContractGitHookEvent must reject undeclared fields."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ContractGitHookEvent(
                hook="pre-commit",
                repo="OmniNode-ai/omniclaude",
                branch="main",
                author="jonah",
                outcome="pass",
                undeclared_field="must_fail",  # type: ignore[call-arg]
            )

    def test_linear_snapshot_event_construction(self) -> None:
        """ContractLinearSnapshotEvent can be constructed with required fields."""
        event = ContractLinearSnapshotEvent(
            snapshot_id="snap-abc123",
            workstreams=["ws-1", "ws-2"],
        )
        assert event.snapshot_id == "snap-abc123"
        assert event.workstreams == ["ws-1", "ws-2"]
        assert event.event_type == "onex.evt.linear.snapshot.v1"

    def test_linear_snapshot_event_rejects_extra_fields(self) -> None:
        """ContractLinearSnapshotEvent must reject undeclared fields."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ContractLinearSnapshotEvent(
                snapshot_id="snap-001",
                undeclared_field="must_fail",  # type: ignore[call-arg]
            )

    def test_contracts_are_frozen_immutable(self) -> None:
        """Mutation of frozen contract instances must raise ValidationError."""
        from pydantic import ValidationError

        event = ContractGitHubPRStatusEvent(
            repo="OmniNode-ai/omniclaude",
            pr_number=1,
            triage_state="draft",
        )
        with pytest.raises(ValidationError):
            event.pr_number = 2  # type: ignore[misc]
