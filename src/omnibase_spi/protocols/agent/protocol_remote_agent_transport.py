# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Remote-agent transport protocol seam for A2A, MCP, and HTTP handlers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_core.models.common.model_schema_value import ModelSchemaValue
from omnibase_core.models.delegation.model_agent_task_lifecycle_event import (
    ModelAgentTaskLifecycleEvent,
)
from omnibase_core.models.delegation.model_target_agent import ModelTargetAgent


@runtime_checkable
class ProtocolRemoteAgentTransport(Protocol):
    """Contract every remote-agent transport implementation satisfies."""

    async def submit(
        self,
        target: ModelTargetAgent,
        payload: dict[str, ModelSchemaValue],
        correlation_id: UUID,
    ) -> str:
        """Submit a task and return the remote peer's opaque task handle."""
        ...

    async def watch(
        self,
        remote_task_handle: str,
        correlation_id: UUID,
    ) -> AsyncIterator[ModelAgentTaskLifecycleEvent]:
        """Yield lifecycle events until a terminal state is reached."""
        ...
