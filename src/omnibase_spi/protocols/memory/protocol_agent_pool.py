from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward references for agent configuration and model types
    class ModelAgentConfig:
        """Protocol for agent configuration."""

        agent_id: str
        agent_type: str
        configuration: dict[str, Any]
        security_context: dict[str, Any]

    class ModelAgentInstance:
        """Protocol for agent instance."""

        instance_id: str
        agent_id: str
        status: str
        health_status: str
        configuration: "ModelAgentConfig"

    class ModelAgentHealthStatus:
        """Protocol for agent health status."""

        status: str
        last_check: str
        metrics: dict[str, Any]

    class ModelAgentStatus:
        """Protocol for agent status."""

        state: str
        error_message: str | None
        last_activity: str

    class ModelValidationResult:
        """Protocol for validation results."""

        is_valid: bool
        errors: list[str]
        warnings: list[str]

    class ModelMemoryOperation:
        """Protocol for memory operations."""

        operation_type: str
        data: dict[str, Any]
        timestamp: str

    class ModelMemoryResponse:
        """Protocol for memory responses."""

        success: bool
        data: Any
        error_message: str | None

    class ModelMemoryMetadata:
        """Protocol for memory metadata."""

        size: int
        created_at: str
        modified_at: str
        access_count: int

    class ModelMemoryError:
        """Protocol for memory errors."""

        error_type: str
        message: str
        details: dict[str, Any]

    class ModelMemoryRequest:
        """Protocol for memory requests."""

        operation: str
        key: str
        data: Any
        options: dict[str, Any]

    class ModelMemoryResponseV2:
        """Protocol for memory responses (version 2)."""

        success: bool
        data: Any
        error: str | None

    class ModelMemorySecurityContext:
        """Protocol for memory security context."""

        user_id: str
        permissions: list[str]
        session_id: str

    class ModelMemoryStreamingResponse:
        """Protocol for streaming memory responses."""

        chunk_id: str
        data: Any
        is_last: bool

    class ModelMemoryStreamingRequest:
        """Protocol for streaming memory requests."""

        stream_id: str
        operation: str
        parameters: dict[str, Any]

    class ModelMemorySecurityPolicy:
        """Protocol for memory security policies."""

        policy_id: str
        rules: list[dict[str, Any]]
        default_action: str

    class ModelMemoryComposable:
        """Protocol for composable memory operations."""

        components: list[str]
        operations: list[str]
        metadata: dict[str, Any]

    class ModelMemoryErrorHandling:
        """Protocol for memory error handling."""

        error_type: str
        severity: str
        recovery_strategy: str
        context: dict[str, Any]


"""
Protocol for Agent Pool Management.

This protocol defines the interface for managing pools of Claude Code agents,
including dynamic scaling, load balancing, and resource optimization.
"""

if TYPE_CHECKING:
    from typing import Literal

    PoolScalingPolicy = Literal["manual", "auto_scale", "predictive", "reactive"]
    PoolHealthStatus = Literal["healthy", "degraded", "critical", "failing"]


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

    async def delete_pool(self, pool_name: str, force: bool = False) -> bool:
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

    async def get_pool_status(self, pool_name: str) -> dict[str, Any]:
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

    async def get_pool_metrics(self, pool_name: str) -> dict[str, Any]:
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

    async def drain_pool(self, pool_name: str, timeout_seconds: int = 300) -> bool:
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
