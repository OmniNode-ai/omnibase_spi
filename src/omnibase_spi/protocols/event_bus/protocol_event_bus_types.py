# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocols for event bus topic configuration."""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolTopicConfig(Protocol):
    """
    Protocol for topic-specific configuration parameters.

    Defines configuration settings for event bus topics such as retention policies,
    compression settings, cleanup policies, and other backend-specific tuning
    parameters. Used when creating or modifying topics via administrative APIs.

    This protocol is backend-agnostic; implementations may map these settings
    to provider-specific configurations (e.g., Kafka topic configs, RabbitMQ
    queue arguments, etc.).

    Attributes:
        retention_ms: Message retention time in milliseconds (None for broker default).
        cleanup_policy: Cleanup policy ("delete", "compact", or "compact,delete").
        compression_type: Compression algorithm ("none", "gzip", "snappy", "lz4", "zstd").
        max_message_bytes: Maximum message size in bytes (None for broker default).
        min_in_sync_replicas: Minimum ISR for acknowledgment (None for broker default).

    Example:
        ```python
        # Create topic with custom retention
        await client.create_topic(
            topic_name="events",
            partitions=3,
            replication_factor=2,
            config=TopicConfig(
                retention_ms=86400000,  # 24 hours
                cleanup_policy="delete",
                compression_type="gzip"
            )
        )
        ```

    See Also:
        - ProtocolEventBusExtendedClient: Uses this for create_topic operations
        - ProtocolKafkaConfig: Kafka client-level configuration
    """

    @property
    def retention_ms(self) -> int | None:
        """Message retention time in milliseconds.

        Returns:
            Retention time or None to use broker default.
        """
        ...

    @property
    def cleanup_policy(self) -> str | None:
        """Topic cleanup policy.

        Returns:
            One of "delete", "compact", or "compact,delete". None for broker default.
        """
        ...

    @property
    def compression_type(self) -> str | None:
        """Compression algorithm for messages.

        Returns:
            One of "none", "gzip", "snappy", "lz4", "zstd". None for producer setting.
        """
        ...

    @property
    def max_message_bytes(self) -> int | None:
        """Maximum message size in bytes.

        Returns:
            Maximum bytes per message or None for broker default.
        """
        ...

    @property
    def min_in_sync_replicas(self) -> int | None:
        """Minimum in-sync replicas for acknowledgment.

        Returns:
            Minimum ISR count or None for broker default.
        """
        ...

    def to_backend_config(self) -> dict[str, ContextValue]:
        """Convert to backend-specific configuration dictionary.

        Returns:
            Dictionary suitable for passing to the event bus backend API.
        """
        ...
