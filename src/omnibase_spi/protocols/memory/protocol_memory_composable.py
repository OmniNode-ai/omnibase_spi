"""
Composable protocol interfaces for OmniMemory operations.

Splits large protocols into smaller, focused, composable interfaces
that can be implemented independently or combined for comprehensive
memory management capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from .protocol_memory_base import ProtocolMemoryMetadata
    from .protocol_memory_requests import (
        ProtocolAgentCoordinationRequest,
        ProtocolWorkflowExecutionRequest,
    )
    from .protocol_memory_responses import (
        ProtocolAgentCoordinationResponse,
        ProtocolMemoryResponse,
        ProtocolWorkflowExecutionResponse,
    )
    from .protocol_memory_security import ProtocolMemorySecurityContext


@runtime_checkable
class ProtocolWorkflowManager(Protocol):
    """
    Focused interface for workflow management operations.

    Handles workflow execution, monitoring, and lifecycle management
    without agent coordination complexity.
    """

    async def execute_workflow(
        self,
        request: "ProtocolWorkflowExecutionRequest",
        security_context: "ProtocolMemorySecurityContext | None" = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolWorkflowExecutionResponse":
        """
        Execute a memory workflow with specified configuration.

        Args:
            request: Workflow execution request with type and config
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for workflow execution

        Returns:
            Execution response with workflow ID and status

        Raises:
            SecurityError: If user not authorized to execute workflows
            WorkflowError: If workflow execution fails
            TimeoutError: If execution exceeds timeout
        """
        ...

    async def pause_workflow(
        self,
        workflow_id: UUID,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Pause a running workflow.

        Args:
            workflow_id: ID of workflow to pause
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with workflow pause status

        Raises:
            SecurityError: If user not authorized to control workflow
            WorkflowError: If workflow cannot be paused
        """
        ...

    async def resume_workflow(
        self,
        workflow_id: UUID,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Resume a paused workflow.

        Args:
            workflow_id: ID of workflow to resume
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with workflow resume status

        Raises:
            SecurityError: If user not authorized to control workflow
            WorkflowError: If workflow cannot be resumed
        """
        ...

    async def cancel_workflow(
        self,
        workflow_id: UUID,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Cancel a running or paused workflow.

        Args:
            workflow_id: ID of workflow to cancel
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with workflow cancellation status

        Raises:
            SecurityError: If user not authorized to control workflow
            WorkflowError: If workflow cannot be cancelled
        """
        ...

    async def get_workflow_status(
        self,
        workflow_id: UUID,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Get current status of a workflow.

        Args:
            workflow_id: ID of workflow to check
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with detailed workflow status

        Raises:
            SecurityError: If user not authorized to view workflow
            WorkflowError: If workflow status cannot be retrieved
        """
        ...


@runtime_checkable
class ProtocolAgentCoordinator(Protocol):
    """
    Focused interface for agent coordination operations.

    Handles agent management, coordination, and communication
    without workflow execution complexity.
    """

    async def coordinate_agents(
        self,
        request: "ProtocolAgentCoordinationRequest",
        security_context: "ProtocolMemorySecurityContext | None" = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolAgentCoordinationResponse":
        """
        Coordinate multiple agents for distributed operations.

        Args:
            request: Agent coordination request with IDs and task
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for coordination

        Returns:
            Coordination response with status and agent responses

        Raises:
            SecurityError: If user not authorized to coordinate agents
            CoordinationError: If agent coordination fails
            TimeoutError: If coordination exceeds timeout
        """
        ...

    async def register_agent(
        self,
        agent_id: UUID,
        agent_capabilities: list[str],
        agent_metadata: "ProtocolMemoryMetadata",
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Register a new agent with the coordinator.

        Args:
            agent_id: Unique identifier for the agent
            agent_capabilities: List of agent capabilities
            agent_metadata: Additional agent metadata
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with agent registration status

        Raises:
            SecurityError: If user not authorized to register agents
            RegistrationError: If agent registration fails
        """
        ...

    async def unregister_agent(
        self,
        agent_id: UUID,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Unregister an agent from the coordinator.

        Args:
            agent_id: ID of agent to unregister
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with agent unregistration status

        Raises:
            SecurityError: If user not authorized to unregister agents
            RegistrationError: If agent unregistration fails
        """
        ...

    async def get_agent_status(
        self,
        agent_id: UUID,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Get current status of a registered agent.

        Args:
            agent_id: ID of agent to check
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with detailed agent status

        Raises:
            SecurityError: If user not authorized to view agent status
            AgentError: If agent status cannot be retrieved
        """
        ...

    async def list_available_agents(
        self,
        capability_filter: list[str] | None = None,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        List all available agents with optional capability filtering.

        Args:
            capability_filter: Optional filter by agent capabilities
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with list of available agents

        Raises:
            SecurityError: If user not authorized to list agents
            CoordinationError: If agent listing fails
        """
        ...


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
        update_data: "ProtocolMemoryMetadata",
        target_nodes: list[UUID] | None = None,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Broadcast update across cluster nodes.

        Args:
            update_type: Type of update to broadcast
            update_data: Data to broadcast
            target_nodes: Specific nodes to notify (None = all)
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with broadcast results

        Raises:
            SecurityError: If user not authorized to broadcast updates
            ClusterError: If broadcast operation fails
        """
        ...

    async def synchronize_state(
        self,
        node_ids: list[UUID],
        synchronization_scope: "ProtocolMemoryMetadata",
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Synchronize state across specified cluster nodes.

        Args:
            node_ids: Nodes to synchronize
            synchronization_scope: Scope of synchronization
            security_context: Security context for authorization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for synchronization

        Returns:
            Response with synchronization results

        Raises:
            SecurityError: If user not authorized to synchronize nodes
            SynchronizationError: If synchronization fails
            TimeoutError: If synchronization exceeds timeout
        """
        ...

    async def get_cluster_status(
        self,
        include_node_details: bool = False,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Get current cluster status and health.

        Args:
            include_node_details: Include detailed node information
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with cluster status and health information

        Raises:
            SecurityError: If user not authorized to view cluster status
            ClusterError: If status retrieval fails
        """
        ...

    async def perform_cluster_maintenance(
        self,
        maintenance_type: str,
        maintenance_parameters: "ProtocolMemoryMetadata",
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Perform cluster maintenance operations.

        Args:
            maintenance_type: Type of maintenance to perform
            maintenance_parameters: Parameters for maintenance operation
            security_context: Security context for authorization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for maintenance

        Returns:
            Response with maintenance results

        Raises:
            SecurityError: If user not authorized to perform maintenance
            MaintenanceError: If maintenance operation fails
            TimeoutError: If maintenance exceeds timeout
        """
        ...


@runtime_checkable
class ProtocolLifecycleManager(Protocol):
    """
    Focused interface for memory lifecycle management operations.

    Handles memory retention policies, archival, and cleanup
    without orchestration complexity.
    """

    async def apply_retention_policies(
        self,
        policy_scope: "ProtocolMemoryMetadata",
        dry_run: bool = False,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Apply memory retention policies to specified scope.

        Args:
            policy_scope: Scope for policy application
            dry_run: Whether to perform dry run without actual changes
            security_context: Security context for authorization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for policy application

        Returns:
            Response with policy application results

        Raises:
            SecurityError: If user not authorized to apply policies
            PolicyError: If policy application fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def archive_memories(
        self,
        memory_ids: list[UUID],
        archive_destination: str,
        archive_format: str,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Archive specified memories to long-term storage.

        Args:
            memory_ids: List of memory IDs to archive
            archive_destination: Destination for archived memories
            archive_format: Format for archived data
            security_context: Security context for authorization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for archival

        Returns:
            Response with archival results

        Raises:
            SecurityError: If user not authorized to archive memories
            ArchivalError: If archival operation fails
            TimeoutError: If archival exceeds timeout
        """
        ...

    async def cleanup_expired_memories(
        self,
        cleanup_scope: "ProtocolMemoryMetadata",
        safety_threshold_hours: int,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Clean up expired memories based on retention policies.

        Args:
            cleanup_scope: Scope for cleanup operation
            safety_threshold_hours: Safety threshold before cleanup
            security_context: Security context for authorization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for cleanup

        Returns:
            Response with cleanup results

        Raises:
            SecurityError: If user not authorized to perform cleanup
            CleanupError: If cleanup operation fails
            TimeoutError: If cleanup exceeds timeout
        """
        ...

    async def restore_archived_memories(
        self,
        archive_reference: str,
        restore_destination: str | None = None,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Restore memories from archive storage.

        Args:
            archive_reference: Reference to archived memories
            restore_destination: Optional destination for restored memories
            security_context: Security context for authorization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for restoration

        Returns:
            Response with restoration results

        Raises:
            SecurityError: If user not authorized to restore memories
            RestorationError: If restoration operation fails
            TimeoutError: If restoration exceeds timeout
        """
        ...


@runtime_checkable
class ProtocolMemoryOrchestrator(Protocol):
    """
    Composite interface combining all orchestration capabilities.

    This interface can be implemented by combining the smaller focused
    interfaces above, or implemented directly for comprehensive orchestration.
    """

    workflow_manager: "ProtocolWorkflowManager"
    agent_coordinator: "ProtocolAgentCoordinator"
    cluster_coordinator: "ProtocolClusterCoordinator"
    lifecycle_manager: "ProtocolLifecycleManager"

    async def health_check(
        self,
        check_scope: str,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Perform comprehensive health check across all orchestration components.

        Args:
            check_scope: Scope of health check (workflow, agents, cluster, lifecycle, all)
            security_context: Security context for authorization
            correlation_id: Request correlation ID

        Returns:
            Response with comprehensive health status

        Raises:
            SecurityError: If user not authorized to perform health checks
            HealthCheckError: If health check operation fails
        """
        ...


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
        processing_options: "ProtocolMemoryMetadata",
        security_context: "ProtocolMemorySecurityContext | None" = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Process semantic information from content.

        Args:
            content: Content to process semantically
            processing_options: Options for semantic processing
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for processing

        Returns:
            Response with semantic processing results

        Raises:
            SecurityError: If user not authorized to process semantics
            ProcessingError: If semantic processing fails
            TimeoutError: If processing exceeds timeout
        """
        ...

    async def analyze_patterns(
        self,
        data_source: "ProtocolMemoryMetadata",
        analysis_type: str,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Analyze patterns in memory data.

        Args:
            data_source: Source data for pattern analysis
            analysis_type: Type of pattern analysis to perform
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for analysis

        Returns:
            Response with pattern analysis results

        Raises:
            SecurityError: If user not authorized to analyze patterns
            AnalysisError: If pattern analysis fails
            TimeoutError: If analysis exceeds timeout
        """
        ...

    async def generate_embeddings(
        self,
        content_items: list[str],
        embedding_model: str | None = None,
        security_context: "ProtocolMemorySecurityContext | None" = None,
        timeout_seconds: float | None = None,
    ) -> "ProtocolMemoryResponse":
        """
        Generate embeddings for multiple content items.

        Args:
            content_items: List of content to generate embeddings for
            embedding_model: Optional specific embedding model
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for generation

        Returns:
            Response with generated embeddings

        Raises:
            SecurityError: If user not authorized to generate embeddings
            EmbeddingError: If embedding generation fails
            TimeoutError: If generation exceeds timeout
        """
        ...
