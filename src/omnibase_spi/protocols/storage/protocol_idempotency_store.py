"""
Protocol for idempotency storage implementations.

Defines the contract for idempotency stores that enable exactly-once message
processing through deduplication. This protocol supports multiple backend
implementations including PostgreSQL, Valkey/Redis, and in-memory for testing.

The idempotency store uses a composite key strategy (domain, message_id) to
enable domain-isolated deduplication, allowing different subsystems to maintain
independent idempotency guarantees.

Example implementations:
    - PostgresIdempotencyStore: PostgreSQL-based persistent storage (P1)
    - ValkeyIdempotencyStore: Valkey/Redis-based distributed storage (P2)
    - InMemoryIdempotencyStore: In-memory storage for testing

Related tickets:
    - OMN-991: Define ProtocolIdempotencyStore in omnibase_spi
    - OMN-945: Implement runtime idempotency guard (B3)
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class ProtocolIdempotencyStore(Protocol):
    """
    Contract for idempotency storage implementations.

    This protocol defines the interface for stores that track processed messages
    to prevent duplicate processing. Implementations enable exactly-once semantics
    in event-driven systems by recording which messages have been processed.

    Composite Key Strategy:
        The store uses (domain, message_id) as a composite key:
        - domain: Optional namespace for domain-isolated deduplication
        - message_id: Unique identifier for the message (typically UUID)

        This allows different subsystems (e.g., "registration", "billing") to
        maintain independent idempotency guarantees without key collisions.

    Concurrency Requirements:
        - check_and_record() MUST be atomic (check + insert in single operation)
        - Implementations MUST handle concurrent calls for the same message_id
        - The first caller to record wins; subsequent calls return False

    TTL and Cleanup:
        - Implementations SHOULD support TTL-based expiration
        - cleanup_expired() enables manual cleanup of old entries
        - Recommended TTL: 7-30 days depending on replay window requirements

    Example implementations:
        - PostgresIdempotencyStore: Uses INSERT ON CONFLICT for atomicity
        - ValkeyIdempotencyStore: Uses SETNX with TTL for atomic check-and-set
        - InMemoryIdempotencyStore: Uses dict with threading.Lock for testing

    Migration:
        This protocol is introduced in v0.4.1 as part of the runtime
        idempotency guard feature (B3). Future versions may add batch
        operations and partition-aware methods.
    """

    async def check_and_record(
        self,
        message_id: UUID,
        domain: str | None = None,
        correlation_id: UUID | None = None,
    ) -> bool:
        """
        Atomically check if message was processed and record if not.

        This is the primary method for idempotency checking. It MUST be atomic:
        the check and record operations must happen as a single indivisible
        operation to prevent race conditions.

        Args:
            message_id: Unique identifier for the message. Typically the
                message's UUID from the event envelope.
            domain: Optional domain namespace for isolated deduplication.
                Examples: "registration", "billing", "notifications".
                If None, uses a default global domain.
            correlation_id: Optional correlation ID for tracing and debugging.
                Stored with the record for observability.

        Returns:
            True if message is new (should be processed).
            False if message is duplicate (should be skipped).

        Raises:
            IdempotencyStoreError: If the atomic operation fails due to
                connection issues or other storage errors.

        Concurrency:
            When multiple callers invoke this method simultaneously with the
            same (domain, message_id), exactly ONE caller receives True.
            All other concurrent callers receive False.

        Example:
            ```python
            if await store.check_and_record(
                message_id=event.message_id,
                domain="registration",
                correlation_id=event.correlation_id,
            ):
                # Process the message
                await handle_event(event)
            else:
                # Skip duplicate
                logger.info(f"Skipping duplicate message: {event.message_id}")
            ```
        """
        ...

    async def is_processed(
        self,
        message_id: UUID,
        domain: str | None = None,
    ) -> bool:
        """
        Check if a message was already processed.

        This is a read-only check that does not modify the store. Useful for
        diagnostic queries and UI status displays.

        Args:
            message_id: Unique identifier for the message.
            domain: Optional domain namespace. Must match the domain used
                when the message was recorded.

        Returns:
            True if the message has been processed.
            False if the message has not been processed or has expired.

        Raises:
            IdempotencyStoreError: If the query fails due to connection
                issues or other storage errors.

        Note:
            For idempotency enforcement, prefer check_and_record() which
            is atomic. Use is_processed() only for non-critical queries.

        Example:
            ```python
            if await store.is_processed(message_id, domain="registration"):
                print(f"Message {message_id} was already processed")
            ```
        """
        ...

    async def mark_processed(
        self,
        message_id: UUID,
        domain: str | None = None,
        correlation_id: UUID | None = None,
        processed_at: datetime | None = None,
    ) -> None:
        """
        Mark a message as processed.

        Records a message as processed without checking if it already exists.
        This is useful for:
        - Manual recovery/replay scenarios
        - Importing historical processing records
        - Testing and fixture setup

        Args:
            message_id: Unique identifier for the message.
            domain: Optional domain namespace for isolated deduplication.
            correlation_id: Optional correlation ID for tracing.
            processed_at: Optional timestamp of when processing occurred.
                If None, implementations MUST use datetime.now(timezone.utc).
                This value MUST be timezone-aware (preferably UTC). Naive
                datetimes (without tzinfo) SHOULD be rejected by implementations
                or treated as UTC with a warning logged.

        Raises:
            IdempotencyStoreError: If the record operation fails.

        Idempotent:
            This method is idempotent. Calling it multiple times with the
            same (domain, message_id) has no additional effect beyond the
            first call (may update processed_at timestamp depending on
            implementation).

        Example:
            ```python
            from datetime import datetime, timezone

            # Mark as processed with explicit timestamp
            await store.mark_processed(
                message_id=event.message_id,
                domain="registration",
                processed_at=datetime.now(timezone.utc),
            )
            ```
        """
        ...

    async def cleanup_expired(
        self,
        ttl_seconds: int,
    ) -> int:
        """
        Remove entries older than TTL.

        Cleans up old idempotency records to prevent unbounded storage growth.
        Should be called periodically by a background job or scheduler.

        Args:
            ttl_seconds: Time-to-live in seconds. Records older than this
                value (based on processed_at timestamp) are removed.
                Recommended values:
                - 7 days (604800s) for high-volume, short replay windows
                - 30 days (2592000s) for audit/compliance requirements

        Returns:
            Number of entries removed.

        Raises:
            IdempotencyStoreError: If the cleanup operation fails.

        Performance:
            Implementations SHOULD batch deletions to avoid long-running
            transactions. For large tables, consider using indexed
            processed_at columns and batch sizes of 1000-10000.

        Example:
            ```python
            # Clean up records older than 7 days
            removed = await store.cleanup_expired(ttl_seconds=604800)
            logger.info(f"Cleaned up {removed} expired idempotency records")
            ```

        Scheduling:
            Recommended to run cleanup during low-traffic periods.
            Example cron: "0 3 * * *" (daily at 3 AM)
        """
        ...
