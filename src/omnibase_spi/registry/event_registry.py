"""SPI Event Registry — canonical mapping of event_type → wire metadata.

Policy: ``event_type == wire topic suffix`` (Option A from OMN-2655).

Each entry maps a fully-qualified ``event_type`` string to the tuple:
    (topic, schema_version, partition_key_fields, producer_protocol_name)

These values are consumed by:
- The ONEX runtime when constructing Kafka producer calls.
- The drift gate test (``test_event_registry_fingerprint.py``) that asserts
  alignment between SPI registry entries and Core model field sets.

Registered Topics
-----------------
``onex.evt.github.pr-status.v1``
    GitHub PR polling results.
    Partition key: ``{repo}:{pr_number}`` for PR-ordered processing.

``onex.evt.git.hook.v1``
    Git hook events (push, pre-receive, post-receive, etc.).
    Partition key: ``{repo}:{branch}`` for per-branch ordering.

``onex.evt.linear.snapshot.v1``
    Linear workstream snapshots.
    Partition key: ``snapshot_id`` for idempotent snapshot delivery.

This file must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

from typing import NamedTuple


class EventRegistryEntry(NamedTuple):
    """Describes a single registered event type.

    Attributes:
        topic: Fully-qualified Kafka topic name. By policy (Option A),
            ``event_type == topic`` — both strings are identical.
        schema_version: Wire-format version string (e.g. ``"1.0"``).
        partition_key_fields: Ordered tuple of field names from the
            corresponding Core model that are concatenated (with ``:``)
            to form the Kafka partition key.
        producer_protocol: Fully-qualified class name of the SPI Protocol
            responsible for producing this event type.
    """

    topic: str
    schema_version: str
    partition_key_fields: tuple[str, ...]
    producer_protocol: str


# ---------------------------------------------------------------------------
# Canonical registry
#
# Invariant enforced by test_event_registry_fingerprint.py:
#   entry.topic == event_type (the dict key)
# ---------------------------------------------------------------------------

EVENT_REGISTRY: dict[str, EventRegistryEntry] = {
    "onex.evt.github.pr-status.v1": EventRegistryEntry(
        topic="onex.evt.github.pr-status.v1",
        schema_version="1.0",
        partition_key_fields=("repo", "pr_number"),
        producer_protocol=(
            "omnibase_spi.protocols.effects.protocol_github_pr_poller_effect"
            ".ProtocolGitHubPRPollerEffect"
        ),
    ),
    "onex.evt.git.hook.v1": EventRegistryEntry(
        topic="onex.evt.git.hook.v1",
        schema_version="1.0",
        partition_key_fields=("repo", "branch"),
        producer_protocol=(
            "omnibase_spi.protocols.effects.protocol_git_hook_effect"
            ".ProtocolGitHookEffect"
        ),
    ),
    "onex.evt.linear.snapshot.v1": EventRegistryEntry(
        topic="onex.evt.linear.snapshot.v1",
        schema_version="1.0",
        partition_key_fields=("snapshot_id",),
        producer_protocol=(
            "omnibase_spi.protocols.effects.protocol_linear_snapshot_effect"
            ".ProtocolLinearSnapshotEffect"
        ),
    ),
}
