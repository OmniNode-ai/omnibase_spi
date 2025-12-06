"""
Composable protocol interfaces for OmniMemory operations.

Splits large protocols into smaller, focused, composable interfaces
that can be implemented independently or combined for comprehensive
memory management capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryMetadata,
    )
    from omnibase_spi.protocols.memory.protocol_memory_requests import (
        ProtocolAgentCoordinationRequest,
        ProtocolWorkflowExecutionRequest,
    )
    from omnibase_spi.protocols.memory.protocol_memory_responses import (
        ProtocolAgentCoordinationResponse,
        ProtocolMemoryResponse,
        ProtocolWorkflowExecutionResponse,
    )
    from omnibase_spi.protocols.memory.protocol_memory_security import (
        ProtocolMemorySecurityContext,
    )


@runtime_checkable
class ProtocolWorkflowManager(Protocol):
    """
    Focused interface for workflow management operations.

    Handles workflow execution, monitoring, and lifecycle management
    without agent coordination complexity.
    """

    async def execute_workflow(
        self,
        request: ProtocolWorkflowExecutionRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolWorkflowExecutionResponse: ...

    async def pause_workflow(
        self,
        workflow_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def resume_workflow(
        self,
        workflow_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def cancel_workflow(
        self,
        workflow_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def get_workflow_status(
        self,
        workflow_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolAgentCoordinator(Protocol):
    """
    Focused interface for agent coordination operations.

    Handles agent management, coordination, and communication
    without workflow execution complexity.
    """

    async def coordinate_agents(
        self,
        request: ProtocolAgentCoordinationRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolAgentCoordinationResponse: ...

    async def register_agent(
        self,
        agent_id: UUID,
        agent_capabilities: list[str],
        agent_metadata: ProtocolMemoryMetadata,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def unregister_agent(
        self,
        agent_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def get_agent_status(
        self,
        agent_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def list_available_agents(
        self,
        capability_filter: list[str] | None = None,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolClusterCoordinator(Protocol):
    """
    Focused interface for cluster-wide coordination operations.

    Handles distributed memory operations, synchronization, and
    cluster state management.
    """

    async def broadcast_update(
        self,
        update_type: str,
        update_data: ProtocolMemoryMetadata,
        target_nodes: list[UUID] | None = None,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def synchronize_state(
        self,
        node_ids: list[UUID],
        synchronization_scope: ProtocolMemoryMetadata,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def get_cluster_status(
        self,
        include_node_details: bool | None = None,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def perform_cluster_maintenance(
        self,
        maintenance_type: str,
        maintenance_parameters: ProtocolMemoryMetadata,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolLifecycleManager(Protocol):
    """
    Focused interface for memory lifecycle management operations.

    Handles memory retention policies, archival, and cleanup
    without orchestration complexity.
    """

    async def apply_retention_policies(
        self,
        policy_scope: ProtocolMemoryMetadata,
        dry_run: bool | None = None,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def archive_memories(
        self,
        memory_ids: list[UUID],
        archive_destination: str,
        archive_format: str,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def cleanup_expired_memories(
        self,
        cleanup_scope: ProtocolMemoryMetadata,
        safety_threshold_hours: int,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def restore_archived_memories(
        self,
        archive_reference: str,
        restore_destination: str | None = None,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolMemoryOrchestrator(Protocol):
    """
    Composite interface combining all orchestration capabilities.

    This interface can be implemented by combining the smaller focused
    interfaces above, or implemented directly for comprehensive orchestration.
    """

    workflow_manager: ProtocolWorkflowManager
    agent_coordinator: ProtocolAgentCoordinator
    cluster_coordinator: ProtocolClusterCoordinator
    lifecycle_manager: ProtocolLifecycleManager

    async def health_check(
        self,
        check_scope: str,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolComputeNodeComposite(Protocol):
    """
    Composite interface that can split compute operations into focused areas.

    Allows implementation as separate semantic processing, pattern analysis,
    and embedding generation services that can be coordinated independently.
    """

    async def process_semantics(
        self,
        content: str,
        processing_options: ProtocolMemoryMetadata,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def analyze_patterns(
        self,
        data_source: ProtocolMemoryMetadata,
        analysis_type: str,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def generate_embeddings(
        self,
        content_items: list[str],
        embedding_model: str | None = None,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...
