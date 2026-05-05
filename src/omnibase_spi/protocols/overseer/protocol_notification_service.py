# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Overseer notification service protocol.

Defines the contract for routing overseer status updates, alerts, and
summaries to external channels such as Slack, email, or webhook endpoints.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNotificationService(Protocol):
    """Notification delivery contract for overseer events.

    Implementors translate structured overseer events into human-readable
    notifications and deliver them via a channel-specific adapter (e.g.
    AdapterNotificationSlack). Channels are identified by string handles
    and are resolved by each concrete adapter.

    Example:
        ```python
        notifier: ProtocolNotificationService = get_notification_service()

        await notifier.connect()
        await notifier.send(
            channel="#onex-overseer",
            title="OMN-1234 merged",
            body="PR #42 merged successfully at 14:32 UTC.",
            level="info",
        )
        await notifier.close()
        ```
    """

    # -- Lifecycle --

    async def connect(self) -> bool:
        """Establish a connection to the notification backend.

        Returns:
            True if connection was established successfully.
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
        """
        ...

    # -- Delivery --

    async def send(
        self,
        channel: str,
        title: str,
        body: str,
        level: str = "info",
        metadata: dict[str, str] | None = None,
    ) -> bool:
        """Send a notification to the specified channel.

        Args:
            channel: Destination channel identifier (e.g. ``"#onex-overseer"``).
            title: Short summary line shown in notification previews.
            body: Full notification body (plain text or markdown).
            level: Severity level — ``"info"``, ``"warning"``, or ``"error"``.
            metadata: Optional key-value annotations forwarded to the adapter.

        Returns:
            True if the notification was delivered successfully.

        Raises:
            ValueError: If ``level`` is not one of the supported values.
        """
        ...

    async def send_batch(
        self,
        channel: str,
        notifications: list[dict[str, str]],
    ) -> int:
        """Send multiple notifications to the specified channel in one call.

        Each item in ``notifications`` must include at minimum ``title`` and
        ``body`` keys. Optional ``level`` and ``metadata`` keys follow the
        same semantics as ``send``.

        Args:
            channel: Destination channel identifier.
            notifications: List of notification payloads.

        Returns:
            Number of notifications delivered successfully.
        """
        ...

    # -- Health --

    async def health_check(self) -> bool:
        """Verify that the notification backend is reachable.

        Returns:
            True if the service is reachable and ready to deliver notifications.
        """
        ...
