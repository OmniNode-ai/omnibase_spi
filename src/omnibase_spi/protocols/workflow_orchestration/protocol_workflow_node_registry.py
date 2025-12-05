"""
ONEX SPI workflow node registry protocols for orchestration.

These protocols extend the base node registry with workflow-specific
node discovery, capability management, and task scheduling support.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralNodeType,
)
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    LiteralTaskPriority,
    LiteralTaskType,
    ProtocolTaskConfiguration,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.node.protocol_node_registry import ProtocolNodeRegistry


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
    supported_task_types: list[LiteralTaskType]
    supported_node_types: list[LiteralNodeType]
    resource_requirements: dict[str, ContextValue]
    configuration_schema: dict[str, ContextValue]
    performance_characteristics: dict[str, float]
    availability_constraints: dict[str, ContextValue]


@runtime_checkable
class ProtocolWorkflowNodeInfo(Protocol):
    """
    Protocol for workflow-specific node information.

    Extends base node info with workflow orchestration capabilities,
    current workload, and task execution metrics.
    """

    node_id: str
    node_type: LiteralNodeType
    node_name: str
    environment: str
    group: str
    version: str
    health_status: "LiteralHealthStatus"
    endpoint: str
    metadata: dict[str, ContextValue]
    workflow_capabilities: list["ProtocolWorkflowNodeCapability"]
    current_workload: dict[str, ContextValue]
    max_concurrent_tasks: int
    current_task_count: int
    supported_workflow_types: list[str]
    task_execution_history: dict[str, ContextValue]
    resource_utilization: dict[str, float]
    scheduling_preferences: dict[str, ContextValue]


@runtime_checkable
class ProtocolTaskSchedulingCriteria(Protocol):
    """
    Protocol for task scheduling criteria.

    Defines the requirements and preferences for scheduling tasks
    on workflow nodes based on capabilities and constraints.
    """

    task_type: LiteralTaskType
    node_type: LiteralNodeType
    required_capabilities: list[str]
    preferred_capabilities: list[str]
    resource_requirements: dict[str, ContextValue]
    affinity_rules: dict[str, ContextValue]
    anti_affinity_rules: dict[str, ContextValue]
    geographic_constraints: dict[str, ContextValue] | None
    priority: LiteralTaskPriority
    timeout_tolerance: int


@runtime_checkable
class ProtocolNodeSchedulingResult(Protocol):
    """
    Protocol for node scheduling results.

    Contains the results of task scheduling decisions including
    selected nodes, scheduling rationale, and fallback options.
    """

    selected_nodes: list["ProtocolWorkflowNodeInfo"]
    scheduling_score: float
    scheduling_rationale: str
    fallback_nodes: list["ProtocolWorkflowNodeInfo"]
    resource_allocation: dict[str, ContextValue]
    estimated_completion_time: float | None
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

    @property
    def base_registry(self) -> "ProtocolNodeRegistry": ...

    async def discover_nodes_for_task(
        self,
        task_config: "ProtocolTaskConfiguration",
        scheduling_criteria: "ProtocolTaskSchedulingCriteria",
    ) -> ProtocolNodeSchedulingResult: ...

    async def discover_nodes_by_capability(
        self,
        capability_name: str,
        capability_version: str | None,
        min_availability: float | None,
    ) -> list["ProtocolWorkflowNodeInfo"]: ...

    async def discover_nodes_for_workflow_type(
        self,
        workflow_type: str,
        required_node_types: list[LiteralNodeType] | None,
    ) -> list["ProtocolWorkflowNodeInfo"]: ...

    async def get_workflow_node_info(
        self, node_id: str
    ) -> ProtocolWorkflowNodeInfo | None: ...

    async def register_workflow_capability(
        self, node_id: str, capability: "ProtocolWorkflowNodeCapability"
    ) -> bool: ...

    async def unregister_workflow_capability(
        self, node_id: str, capability_id: str
    ) -> bool: ...

    async def get_node_capabilities(
        self, node_id: str
    ) -> list["ProtocolWorkflowNodeCapability"]: ...

    async def update_node_workload(
        self, node_id: str, task_id: UUID, workload_change: str
    ) -> None: ...

    async def get_node_workload(self, node_id: str) -> dict[str, ContextValue]: ...

    async def get_resource_utilization(self, node_id: str) -> dict[str, float]: ...

    async def calculate_scheduling_score(
        self,
        node_info: "ProtocolWorkflowNodeInfo",
        task_config: "ProtocolTaskConfiguration",
        criteria: "ProtocolTaskSchedulingCriteria",
    ) -> float: ...

    async def reserve_resources(
        self,
        node_id: str,
        task_id: UUID,
        resource_requirements: dict[str, ContextValue],
        timeout_seconds: int,
    ) -> bool: ...

    async def release_resources(self, node_id: str, task_id: UUID) -> bool: ...

    async def record_task_execution_metrics(
        self, node_id: str, task_id: UUID, execution_metrics: dict[str, ContextValue]
    ) -> None: ...

    async def get_node_performance_history(
        self,
        node_id: str,
        task_type: "LiteralTaskType | None",
        time_window_seconds: int,
    ) -> dict[str, ContextValue]: ...

    async def update_node_availability(
        self,
        node_id: str,
        availability_status: str,
        metadata: dict[str, ContextValue] | None,
    ) -> bool: ...

    async def get_cluster_health_summary(
        self, workflow_type: str | None, node_group: str | None
    ) -> dict[str, ContextValue]: ...
