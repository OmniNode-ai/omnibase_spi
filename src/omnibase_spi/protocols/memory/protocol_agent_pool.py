"""
Protocol for Agent Pool Management.

This protocol defines the interface for managing pools of Claude Code agents,
including dynamic scaling, load balancing, and resource optimization.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Literal

    from omnibase_core.types import JsonType

    PoolScalingPolicy = Literal["manual", "auto_scale", "predictive", "reactive"]
    PoolHealthStatus = Literal["healthy", "degraded", "critical", "failing"]


@runtime_checkable
class ProtocolMemoryOperation(Protocol):
    """
    Protocol for memory operations in the ONEX memory subsystem.

    Defines the interface for memory operations that can be tracked,
    audited, and replayed. Each operation captures the type, data
    payload, and timestamp for complete operation traceability.

    Attributes:
        operation_type: Type of memory operation (e.g., "read", "write", "delete").
        data: Operation payload containing operation-specific data.
        timestamp: ISO 8601 timestamp when the operation was initiated.

    Example:
        ```python
        class WriteOperation:
            operation_type: str = "write"
            data: dict[str, object] = {"key": "user_123", "value": {"name": "Alice"}}
            timestamp: str = "2024-01-15T10:30:00Z"

        op = WriteOperation()
        assert isinstance(op, ProtocolMemoryOperation)
        assert op.operation_type == "write"
        ```
    """

    @property
    def operation_type(self) -> str:
        """Type of memory operation."""
        ...

    @property
    def data(self) -> "JsonType":
        """Operation data."""
        ...

    @property
    def timestamp(self) -> str:
        """Operation timestamp."""
        ...


@runtime_checkable
class ProtocolMemoryResponseV2(Protocol):
    """
    Protocol for memory responses (version 2) with enhanced error handling.

    Provides a standardized response structure for memory operations,
    including success/failure indication, response data, and detailed
    error messages. Version 2 improves upon the original with better
    error context and nullable data support.

    Attributes:
        success: Boolean indicating whether the operation completed successfully.
        data: Response payload; may be None for operations without return data.
        error: Detailed error message if the operation failed; None on success.

    Example:
        ```python
        class SuccessResponse:
            success: bool = True
            data: object = {"user_id": "123", "status": "active"}
            error: str | None = None

        class ErrorResponse:
            success: bool = False
            data: object | None = None
            error: str | None = "Key not found: user_456"

        resp = SuccessResponse()
        assert isinstance(resp, ProtocolMemoryResponseV2)
        assert resp.success and resp.error is None
        ```
    """

    @property
    def success(self) -> bool:
        """Whether operation succeeded."""
        ...

    @property
    def data(self) -> "JsonType":
        """Response data."""
        ...

    @property
    def error(self) -> str | None:
        """Error message if operation failed."""
        ...


@runtime_checkable
class ProtocolMemoryStreamingResponse(Protocol):
    """
    Protocol for streaming memory responses supporting chunked data transfer.

    Enables efficient streaming of large data sets from memory operations
    by breaking responses into manageable chunks. Each chunk is uniquely
    identified and indicates whether it is the final chunk in the stream.

    Attributes:
        chunk_id: Unique identifier for this chunk within the stream.
        data: Payload data for this chunk; type depends on operation.
        is_last: Boolean flag indicating the final chunk in the stream.

    Example:
        ```python
        class StreamChunk:
            chunk_id: str = "chunk_003"
            data: object = {"records": [{"id": 1}, {"id": 2}]}
            is_last: bool = False

        class FinalChunk:
            chunk_id: str = "chunk_004"
            data: object = {"records": [{"id": 3}]}
            is_last: bool = True

        chunk = StreamChunk()
        assert isinstance(chunk, ProtocolMemoryStreamingResponse)
        assert not chunk.is_last
        ```
    """

    @property
    def chunk_id(self) -> str:
        """Chunk identifier."""
        ...

    @property
    def data(self) -> "JsonType":
        """Chunk data."""
        ...

    @property
    def is_last(self) -> bool:
        """Whether this is the last chunk."""
        ...


@runtime_checkable
class ProtocolMemoryStreamingRequest(Protocol):
    """
    Protocol for streaming memory requests enabling chunked data operations.

    Initiates a streaming operation for large-scale memory access, allowing
    clients to receive data in chunks rather than waiting for complete
    response. Supports configurable streaming parameters for flow control.

    Attributes:
        stream_id: Unique identifier for correlating stream chunks.
        operation: Type of streaming operation (e.g., "scan", "export", "subscribe").
        parameters: Operation-specific parameters including batch size and filters.

    Example:
        ```python
        class ScanStreamRequest:
            stream_id: str = "stream_abc123"
            operation: str = "scan"
            parameters: dict[str, object] = {
                "prefix": "user_",
                "batch_size": 100,
                "timeout_ms": 30000
            }

        req = ScanStreamRequest()
        assert isinstance(req, ProtocolMemoryStreamingRequest)
        assert req.operation == "scan"
        ```
    """

    @property
    def stream_id(self) -> str:
        """Stream identifier."""
        ...

    @property
    def operation(self) -> str:
        """Stream operation."""
        ...

    @property
    def parameters(self) -> "JsonType":
        """Stream parameters."""
        ...


@runtime_checkable
class ProtocolMemorySecurityPolicy(Protocol):
    """
    Protocol for memory security policies controlling access and operations.

    Defines security policies for memory access including rule-based
    access control, operation restrictions, and default deny/allow
    behavior. Policies are evaluated against security contexts to
    authorize or reject memory operations.

    Attributes:
        policy_id: Unique identifier for this security policy.
        rules: List of rule definitions with conditions and actions.
        default_action: Action when no rules match ("allow" or "deny").

    Example:
        ```python
        class RestrictivePolicy:
            policy_id: str = "policy_prod_001"
            rules: list[dict[str, object]] = [
                {"pattern": "secret_*", "action": "deny", "principals": ["*"]},
                {"pattern": "user_*", "action": "allow", "principals": ["admin"]}
            ]
            default_action: str = "deny"

        policy = RestrictivePolicy()
        assert isinstance(policy, ProtocolMemorySecurityPolicy)
        assert policy.default_action == "deny"
        ```
    """

    @property
    def policy_id(self) -> str:
        """Policy identifier."""
        ...

    @property
    def rules(self) -> "list[JsonType]":
        """Policy rules."""
        ...

    @property
    def default_action(self) -> str:
        """Default policy action."""
        ...


@runtime_checkable
class ProtocolMemoryComposable(Protocol):
    """
    Protocol for composable memory operations supporting operation chaining.

    Enables composition of multiple memory operations into atomic units,
    allowing complex workflows to be built from simpler components.
    Supports transactional semantics and operation dependency tracking.

    Attributes:
        components: List of component identifiers participating in composition.
        operations: Ordered list of operations to execute in the composition.
        metadata: Additional metadata for composition tracking and debugging.

    Example:
        ```python
        class TransactionalUpdate:
            components: list[str] = ["cache_layer", "persistent_store"]
            operations: list[str] = ["validate", "write_cache", "write_store", "commit"]
            metadata: dict[str, object] = {
                "transaction_id": "tx_789",
                "isolation_level": "serializable"
            }

        comp = TransactionalUpdate()
        assert isinstance(comp, ProtocolMemoryComposable)
        assert len(comp.operations) == 4
        ```
    """

    @property
    def components(self) -> list[str]:
        """Operation components."""
        ...

    @property
    def operations(self) -> list[str]:
        """Composable operations."""
        ...

    @property
    def metadata(self) -> "JsonType":
        """Operation metadata."""
        ...


@runtime_checkable
class ProtocolMemoryErrorHandling(Protocol):
    """
    Protocol for memory error handling with recovery strategy specification.

    Provides structured error information for memory operations including
    error classification, severity levels, and recommended recovery
    strategies. Enables intelligent error handling and automated recovery
    in distributed memory systems.

    Attributes:
        error_type: Classification of the error (e.g., "timeout", "corruption", "quota").
        severity: Severity level ("critical", "high", "medium", "low").
        recovery_strategy: Recommended recovery approach (e.g., "retry", "failover", "abort").
        context: Additional context for debugging and recovery decisions.

    Example:
        ```python
        class TimeoutError:
            error_type: str = "timeout"
            severity: str = "medium"
            recovery_strategy: str = "retry_with_backoff"
            context: dict[str, object] = {
                "operation": "read",
                "key": "user_123",
                "elapsed_ms": 5000,
                "retry_count": 2
            }

        err = TimeoutError()
        assert isinstance(err, ProtocolMemoryErrorHandling)
        assert err.recovery_strategy == "retry_with_backoff"
        ```
    """

    @property
    def error_type(self) -> str:
        """Type of error."""
        ...

    @property
    def severity(self) -> str:
        """Error severity level."""
        ...

    @property
    def recovery_strategy(self) -> str:
        """Recovery strategy."""
        ...

    @property
    def context(self) -> "JsonType":
        """Error context."""
        ...


@runtime_checkable
class ProtocolAgentPool(Protocol):
    """Protocol for agent pool management and optimization."""

    async def create_pool(
        self,
        pool_name: str,
        initial_size: int,
        max_size: int,
        agent_template: str,
        scaling_policy: "PoolScalingPolicy" = "auto_scale",
    ) -> bool:
        """
        Create a new agent pool with specified configuration.

        Args:
            pool_name: Unique name for the pool
            initial_size: Initial number of agents to spawn
            max_size: Maximum number of agents allowed in pool
            agent_template: Configuration template for agents
            scaling_policy: Scaling policy for the pool

        Returns:
            True if pool was created successfully

        Raises:
            PoolCreationError: If pool creation fails
            DuplicatePoolError: If pool already exists
        """
        ...

    async def delete_pool(self, pool_name: str, force: bool | None = None) -> bool:
        """
        Delete an existing agent pool.

        Args:
            pool_name: Name of pool to delete
            force: Whether to force deletion even with active agents

        Returns:
            True if pool was deleted successfully

        Raises:
            PoolNotFoundError: If pool doesn't exist
            PoolDeletionError: If deletion fails
            ActiveAgentsError: If pool has active agents and force=False
        """
        ...

    async def scale_pool(self, pool_name: str, target_size: int) -> bool:
        """
        Scale pool to target size.

        Args:
            pool_name: Name of pool to scale
            target_size: Desired number of agents

        Returns:
            True if scaling was initiated successfully

        Raises:
            PoolNotFoundError: If pool doesn't exist
            ScalingError: If scaling fails
            CapacityExceededError: If target exceeds max size
        """
        ...

    async def get_pool_status(self, pool_name: str) -> "JsonType":
        """
        Get current status of a pool.

        Args:
            pool_name: Name of pool to check

        Returns:
            Dictionary containing pool status information

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def list_pools(self) -> list[str]:
        """
        List all available pools.

        Returns:
            List of pool names
        """
        ...

    async def get_pool_agents(self, pool_name: str) -> list[str]:
        """
        Get list of agent IDs in a pool.

        Args:
            pool_name: Name of pool

        Returns:
            List of agent IDs in the pool

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def assign_agent_from_pool(
        self,
        pool_name: str,
        requirements: dict[str, str] | None = None,
    ) -> str | None:
        """
        Assign an available agent from the pool.

        Args:
            pool_name: Name of pool to assign from
            requirements: Optional requirements for agent selection

        Returns:
            Agent ID if assignment successful, None if no agents available

        Raises:
            PoolNotFoundError: If pool doesn't exist
            AssignmentError: If assignment fails
        """
        ...

    async def release_agent_to_pool(self, pool_name: str, agent_id: str) -> bool:
        """
        Release an agent back to the pool.

        Args:
            pool_name: Name of pool to release to
            agent_id: ID of agent to release

        Returns:
            True if release was successful

        Raises:
            PoolNotFoundError: If pool doesn't exist
            AgentNotFoundError: If agent doesn't exist
            ReleaseError: If release fails
        """
        ...

    async def monitor_pool_health(self, pool_name: str) -> "PoolHealthStatus":
        """
        Monitor health status of a pool.

        Args:
            pool_name: Name of pool to monitor

        Returns:
            Current health status of the pool

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def rebalance_pools(self) -> dict[str, int]:
        """
        Rebalance agents across all pools based on demand.

        Returns:
            Dictionary mapping pool names to new agent counts

        Raises:
            RebalancingError: If rebalancing fails
        """
        ...

    async def enable_auto_scaling(
        self,
        pool_name: str,
        min_size: int,
        max_size: int,
    ) -> bool:
        """
        Enable auto-scaling for a pool.

        Args:
            pool_name: Name of pool
            min_size: Minimum number of agents
            max_size: Maximum number of agents

        Returns:
            True if auto-scaling was enabled

        Raises:
            PoolNotFoundError: If pool doesn't exist
            ConfigurationError: If configuration is invalid
        """
        ...

    async def disable_auto_scaling(self, pool_name: str) -> bool:
        """
        Disable auto-scaling for a pool.

        Args:
            pool_name: Name of pool

        Returns:
            True if auto-scaling was disabled

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def get_pool_metrics(self, pool_name: str) -> "JsonType":
        """
        Get performance metrics for a pool.

        Args:
            pool_name: Name of pool

        Returns:
            Dictionary of pool metrics

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def set_pool_priority(self, pool_name: str, priority: int) -> bool:
        """
        Set priority level for a pool.

        Args:
            pool_name: Name of pool
            priority: Priority level (higher = more important)

        Returns:
            True if priority was set

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def drain_pool(
        self, pool_name: str, timeout_seconds: int | None = None
    ) -> bool:
        """
        Drain a pool by waiting for agents to complete work and not assigning new work.

        Args:
            pool_name: Name of pool to drain
            timeout_seconds: Maximum time to wait for drain completion

        Returns:
            True if pool was drained successfully

        Raises:
            PoolNotFoundError: If pool doesn't exist
            DrainTimeoutError: If drain times out
        """
        ...

    async def warm_pool(self, pool_name: str, target_ready_agents: int) -> bool:
        """
        Warm up a pool by pre-spawning agents to target ready count.

        Args:
            pool_name: Name of pool to warm
            target_ready_agents: Number of ready agents to maintain

        Returns:
            True if warming was initiated

        Raises:
            PoolNotFoundError: If pool doesn't exist
            WarmingError: If warming fails
        """
        ...

    async def get_pool_utilization(self, pool_name: str) -> float:
        """
        Get current utilization percentage of a pool.

        Args:
            pool_name: Name of pool

        Returns:
            Utilization percentage (0.0 to 100.0)

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def configure_pool_limits(
        self,
        pool_name: str,
        cpu_limit: float | None = None,
        memory_limit: int | None = None,
        concurrent_tasks_limit: int | None = None,
    ) -> bool:
        """
        Configure resource limits for a pool.

        Args:
            pool_name: Name of pool
            cpu_limit: CPU limit percentage
            memory_limit: Memory limit in MB
            concurrent_tasks_limit: Maximum concurrent tasks per agent

        Returns:
            True if limits were configured

        Raises:
            PoolNotFoundError: If pool doesn't exist
            ConfigurationError: If configuration is invalid
        """
        ...

    async def get_pool_allocation_strategy(self, pool_name: str) -> str:
        """
        Get current allocation strategy for a pool.

        Args:
            pool_name: Name of pool

        Returns:
            Current allocation strategy name

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def set_pool_allocation_strategy(self, pool_name: str, strategy: str) -> bool:
        """
        Set allocation strategy for a pool.

        Args:
            pool_name: Name of pool
            strategy: Allocation strategy (round_robin, least_loaded, random, etc.)

        Returns:
            True if strategy was set

        Raises:
            PoolNotFoundError: If pool doesn't exist
            InvalidStrategyError: If strategy is not supported
        """
        ...

    async def backup_pool_configuration(self, pool_name: str) -> str:
        """
        Create a backup of pool configuration.

        Args:
            pool_name: Name of pool to backup

        Returns:
            Backup identifier for restoration

        Raises:
            PoolNotFoundError: If pool doesn't exist
            BackupError: If backup creation fails
        """
        ...

    async def restore_pool_configuration(self, pool_name: str, backup_id: str) -> bool:
        """
        Restore pool configuration from backup.

        Args:
            pool_name: Name of pool to restore
            backup_id: Backup identifier

        Returns:
            True if restoration was successful

        Raises:
            PoolNotFoundError: If pool doesn't exist
            BackupNotFoundError: If backup doesn't exist
            RestoreError: If restoration fails
        """
        ...

    async def get_pool_cost_estimate(
        self,
        pool_name: str,
        duration_hours: float,
    ) -> float:
        """
        Get estimated cost for running a pool for specified duration.

        Args:
            pool_name: Name of pool
            duration_hours: Duration in hours

        Returns:
            Estimated cost in dollars

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...

    async def optimize_pool_placement(self) -> dict[str, list[str]]:
        """
        Optimize agent placement across available resources.

        Returns:
            Dictionary mapping resource locations to agent IDs

        Raises:
            OptimizationError: If optimization fails
        """
        ...

    async def create_pool_snapshot(self, pool_name: str, snapshot_name: str) -> bool:
        """
        Create a snapshot of current pool state.

        Args:
            pool_name: Name of pool
            snapshot_name: Name for the snapshot

        Returns:
            True if snapshot was created

        Raises:
            PoolNotFoundError: If pool doesn't exist
            SnapshotError: If snapshot creation fails
        """
        ...

    async def list_pool_snapshots(self, pool_name: str) -> list[str]:
        """
        List all snapshots for a pool.

        Args:
            pool_name: Name of pool

        Returns:
            List of snapshot names

        Raises:
            PoolNotFoundError: If pool doesn't exist
        """
        ...
