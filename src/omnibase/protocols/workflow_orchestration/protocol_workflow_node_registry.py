"""
ONEX SPI workflow node registry protocols for orchestration.

These protocols extend the base node registry with workflow-specific
node discovery, capability management, and task scheduling support.
"""

from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.core.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocols.types.core_types import HealthStatus, NodeType
from omnibase.protocols.types.workflow_orchestration_types import (
    ProtocolTaskConfiguration,
    TaskPriority,
    TaskType,
)


@runtime_checkable
class ProtocolWorkflowNodeCapability(Protocol):
    """
    Protocol for workflow-specific node capabilities.

    Extends basic node capabilities with workflow orchestration
    features, task type support, and resource management.
    """

    capability_id: str
    capability_name: str
    capability_version: str
    supported_task_types: list[TaskType]
    supported_node_types: list[NodeType]
    resource_requirements: dict[str, Any]
    configuration_schema: dict[str, Any]
    performance_characteristics: dict[str, float]
    availability_constraints: dict[str, Any]


@runtime_checkable
class ProtocolWorkflowNodeInfo(Protocol):
    """
    Protocol for workflow-specific node information.

    Extends base node info with workflow orchestration capabilities,
    current workload, and task execution metrics.
    """

    # Base node information
    node_id: str
    node_type: NodeType
    node_name: str
    environment: str
    group: str
    version: str
    health_status: HealthStatus
    endpoint: str
    metadata: dict[str, Any]

    # Workflow-specific information
    workflow_capabilities: list[ProtocolWorkflowNodeCapability]
    current_workload: dict[str, Any]
    max_concurrent_tasks: int
    current_task_count: int
    supported_workflow_types: list[str]
    task_execution_history: dict[str, Any]
    resource_utilization: dict[str, float]
    scheduling_preferences: dict[str, Any]


@runtime_checkable
class ProtocolTaskSchedulingCriteria(Protocol):
    """
    Protocol for task scheduling criteria.

    Defines the requirements and preferences for scheduling tasks
    on workflow nodes based on capabilities and constraints.
    """

    task_type: TaskType
    node_type: NodeType
    required_capabilities: list[str]
    preferred_capabilities: list[str]
    resource_requirements: dict[str, Any]
    affinity_rules: dict[str, Any]
    anti_affinity_rules: dict[str, Any]
    geographic_constraints: Optional[dict[str, Any]]
    priority: TaskPriority
    timeout_tolerance: int


@runtime_checkable
class ProtocolNodeSchedulingResult(Protocol):
    """
    Protocol for node scheduling results.

    Contains the results of task scheduling decisions including
    selected nodes, scheduling rationale, and fallback options.
    """

    selected_nodes: list[ProtocolWorkflowNodeInfo]
    scheduling_score: float
    scheduling_rationale: str
    fallback_nodes: list[ProtocolWorkflowNodeInfo]
    resource_allocation: dict[str, Any]
    estimated_completion_time: Optional[float]
    constraints_satisfied: dict[str, bool]


@runtime_checkable
class ProtocolWorkflowNodeRegistry(Protocol):
    """
    Protocol for workflow-specific node discovery and management.

    Extends the base node registry with workflow orchestration features:
    - Capability-based node discovery
    - Task scheduling and load balancing
    - Workflow-aware node selection
    - Resource utilization tracking
    - Performance-based routing

    """

    # Base registry access
    @property
    def base_registry(self) -> ProtocolNodeRegistry:
        """Get underlying node registry."""
        ...

    # Workflow node discovery
    async def discover_nodes_for_task(
        self,
        task_config: ProtocolTaskConfiguration,
        scheduling_criteria: ProtocolTaskSchedulingCriteria,
    ) -> ProtocolNodeSchedulingResult:
        """
        Discover and rank nodes suitable for task execution.

        Args:
            task_config: Task configuration requirements
            scheduling_criteria: Scheduling preferences and constraints

        Returns:
            Scheduling result with ranked node options
        """
        ...

    async def discover_nodes_by_capability(
        self,
        capability_name: str,
        capability_version: Optional[str],
        min_availability: Optional[float],
    ) -> list[ProtocolWorkflowNodeInfo]:
        """
        Discover nodes by workflow capability.

        Args:
            capability_name: Required capability name
            capability_version: Optional capability version filter
            min_availability: Minimum availability threshold (0.0-1.0)

        Returns:
            List of nodes with the capability
        """
        ...

    async def discover_nodes_for_workflow_type(
        self, workflow_type: str, required_node_types: Optional[list[NodeType]]
    ) -> list[ProtocolWorkflowNodeInfo]:
        """
        Discover nodes that can execute specific workflow type.

        Args:
            workflow_type: Workflow type identifier
            required_node_types: Optional node type filter

        Returns:
            List of compatible nodes
        """
        ...

    # Node information and capabilities
    async def get_workflow_node_info(
        self, node_id: str
    ) -> Optional[ProtocolWorkflowNodeInfo]:
        """
        Get workflow-specific node information.

        Args:
            node_id: Node identifier

        Returns:
            Workflow node info or None if not found
        """
        ...

    async def register_workflow_capability(
        self, node_id: str, capability: ProtocolWorkflowNodeCapability
    ) -> bool:
        """
        Register workflow capability for node.

        Args:
            node_id: Node identifier
            capability: Workflow capability to register

        Returns:
            True if registration successful
        """
        ...

    async def unregister_workflow_capability(
        self, node_id: str, capability_id: str
    ) -> bool:
        """
        Unregister workflow capability from node.

        Args:
            node_id: Node identifier
            capability_id: Capability identifier to remove

        Returns:
            True if unregistration successful
        """
        ...

    async def get_node_capabilities(
        self, node_id: str
    ) -> list[ProtocolWorkflowNodeCapability]:
        """
        Get all workflow capabilities for node.

        Args:
            node_id: Node identifier

        Returns:
            List of node capabilities
        """
        ...

    # Workload and resource management
    async def update_node_workload(
        self, node_id: str, task_id: UUID, workload_change: str
    ) -> None:
        """
        Update node workload tracking.

        Args:
            node_id: Node identifier
            task_id: Task identifier
            workload_change: Change type (add, remove, update)
        """
        ...

    async def get_node_workload(self, node_id: str) -> dict[str, Any]:
        """
        Get current node workload information.

        Args:
            node_id: Node identifier

        Returns:
            Current workload metrics and task list
        """
        ...

    async def get_resource_utilization(self, node_id: str) -> dict[str, float]:
        """
        Get current resource utilization for node.

        Args:
            node_id: Node identifier

        Returns:
            Resource utilization metrics (CPU, memory, etc.)
        """
        ...

    # Scheduling and load balancing
    async def calculate_scheduling_score(
        self,
        node_info: ProtocolWorkflowNodeInfo,
        task_config: ProtocolTaskConfiguration,
        criteria: ProtocolTaskSchedulingCriteria,
    ) -> float:
        """
        Calculate scheduling score for node and task.

        Args:
            node_info: Node information
            task_config: Task configuration
            criteria: Scheduling criteria

        Returns:
            Scheduling score (0.0-1.0, higher is better)
        """
        ...

    async def reserve_resources(
        self,
        node_id: str,
        task_id: UUID,
        resource_requirements: dict[str, Any],
        timeout_seconds: int,
    ) -> bool:
        """
        Reserve resources on node for task execution.

        Args:
            node_id: Node identifier
            task_id: Task identifier
            resource_requirements: Required resources
            timeout_seconds: Reservation timeout

        Returns:
            True if reservation successful
        """
        ...

    async def release_resources(self, node_id: str, task_id: UUID) -> bool:
        """
        Release reserved resources for completed task.

        Args:
            node_id: Node identifier
            task_id: Task identifier

        Returns:
            True if release successful
        """
        ...

    # Performance and metrics
    async def record_task_execution_metrics(
        self, node_id: str, task_id: UUID, execution_metrics: dict[str, Any]
    ) -> None:
        """
        Record task execution performance metrics.

        Args:
            node_id: Node identifier
            task_id: Task identifier
            execution_metrics: Performance metrics
        """
        ...

    async def get_node_performance_history(
        self,
        node_id: str,
        task_type: Optional[TaskType],
        time_window_seconds: int,
    ) -> dict[str, Any]:
        """
        Get historical performance data for node.

        Args:
            node_id: Node identifier
            task_type: Optional task type filter
            time_window_seconds: Time window for metrics

        Returns:
            Performance history and statistics
        """
        ...

    # Health and availability
    async def update_node_availability(
        self,
        node_id: str,
        availability_status: str,
        metadata: Optional[dict[str, Any]],
    ) -> bool:
        """
        Update node availability status.

        Args:
            node_id: Node identifier
            availability_status: Availability status
            metadata: Additional metadata

        Returns:
            True if update successful
        """
        ...

    async def get_cluster_health_summary(
        self, workflow_type: Optional[str], node_group: Optional[str]
    ) -> dict[str, Any]:
        """
        Get cluster health summary for workflow execution.

        Args:
            workflow_type: Optional workflow type filter
            node_group: Optional node group filter

        Returns:
            Cluster health and capacity metrics
        """
        ...
