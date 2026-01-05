"""
Handler contract supporting types and protocols for ONEX SPI interfaces.

Domain: Handler contract type definitions for behavior, capabilities, and constraints.

This module defines the foundational protocols for describing handler contracts,
including behavior characteristics, capability dependencies, and execution constraints.
These protocols are used by ProtocolHandlerContract to provide a complete specification
of handler requirements and guarantees.

Protocol Categories:
    - ProtocolHandlerBehaviorDescriptor: Describes behavioral characteristics
      (idempotency, determinism, side effects, retry safety)
    - ProtocolCapabilityDependency: Represents required or optional capabilities
      with version constraints
    - ProtocolExecutionConstraints: Defines resource limits and execution boundaries
      (timeouts, retries, memory, CPU, concurrency)

See Also:
    - protocol_handler_contract.py: The main ProtocolHandlerContract interface
    - types.py: Handler descriptor and source type definitions
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

# ==============================================================================
# Handler Behavior Descriptor Protocol
# ==============================================================================


@runtime_checkable
class ProtocolHandlerBehaviorDescriptor(Protocol):
    """
    Protocol for describing handler behavior characteristics.

    A behavior descriptor provides semantic information about how a handler
    operates, enabling the runtime to make informed decisions about caching,
    retrying, and scheduling. This information is critical for building
    reliable distributed systems where handler behavior must be predictable.

    Behavior descriptors answer key questions about a handler:
        - Can the operation be safely retried?
        - Will the same input always produce the same output?
        - Does the operation have external effects?
        - Is the operation safe to cache?

    This protocol is useful for:
        - Retry logic implementation in orchestrators
        - Cache invalidation strategies
        - Idempotency key generation
        - Side effect tracking and auditing
        - Distributed transaction coordination

    Attributes:
        idempotent: Whether calling the handler multiple times with the same
            input produces the same result without additional side effects.
        deterministic: Whether the handler produces consistent output for
            identical input, independent of when or where it runs.
        side_effects: Categories of side effects the handler may produce,
            enabling effect tracking and rollback planning.
        retry_safe: Whether the handler can be safely retried on failure
            without causing data corruption or duplicate effects.

    Example:
        ```python
        class HttpGetBehavior:
            '''Behavior descriptor for idempotent HTTP GET operations.'''

            @property
            def idempotent(self) -> bool:
                return True  # GET requests are idempotent

            @property
            def deterministic(self) -> bool:
                return False  # Response may change over time

            @property
            def side_effects(self) -> list[str]:
                return ["network"]  # Makes network calls

            @property
            def retry_safe(self) -> bool:
                return True  # Safe to retry GET requests

        behavior = HttpGetBehavior()
        assert isinstance(behavior, ProtocolHandlerBehaviorDescriptor)

        if behavior.retry_safe and behavior.idempotent:
            print("Handler is safe for automatic retry with caching")
        ```

    Note:
        The relationship between properties is important:
        - An idempotent handler is typically retry_safe
        - A deterministic handler with no side effects is cacheable
        - Side effects should be exhaustively listed for audit purposes

    See Also:
        ProtocolHandlerContract: Uses behavior descriptors for contract specs.
        ProtocolExecutionConstraints: Defines retry limits when retry_safe is True.
    """

    @property
    def idempotent(self) -> bool:
        """
        Whether the handler operation is idempotent.

        An idempotent operation can be called multiple times with the same
        input and will produce the same result without causing additional
        side effects beyond the first call.

        Idempotency Implications:
            - True: Safe to cache results, safe to retry without idempotency keys
            - False: May require idempotency keys, careful retry handling needed

        Examples of Idempotent Operations:
            - HTTP GET, PUT, DELETE (by specification)
            - Database SELECT queries
            - Setting a value (not incrementing)
            - Reading from a message queue (with acknowledgment)

        Examples of Non-Idempotent Operations:
            - HTTP POST (creates new resource each time)
            - Incrementing a counter
            - Sending an email or notification
            - Appending to a log

        Returns:
            True if the operation is idempotent, False otherwise.
        """
        ...

    @property
    def deterministic(self) -> bool:
        """
        Whether the handler produces deterministic output.

        A deterministic handler will always produce the same output given
        the same input, regardless of when or where it runs. This property
        is independent of side effects - a handler can be deterministic
        but still have side effects.

        Determinism Implications:
            - True: Results can be cached, replays produce same results
            - False: Each execution may produce different results

        Factors that Break Determinism:
            - Current time/date usage
            - Random number generation
            - External service calls with variable responses
            - System state dependencies (environment variables, etc.)

        Returns:
            True if the handler produces deterministic output, False otherwise.
        """
        ...

    @property
    def side_effects(self) -> list[str]:
        """
        List of side effect categories the handler may produce.

        Side effects represent observable interactions with the external
        world beyond returning a value. Tracking side effects enables
        proper rollback planning, audit logging, and transaction coordination.

        Common Side Effect Categories:
            - "network": Makes HTTP/TCP/UDP calls to external services
            - "filesystem": Reads or writes files
            - "database": Queries or modifies database state
            - "message_queue": Publishes or consumes messages
            - "cache": Reads or writes cache entries
            - "metrics": Emits metrics or telemetry
            - "logging": Writes to external log systems
            - "email": Sends email notifications
            - "webhook": Triggers external webhooks

        Returns:
            List of side effect category strings. An empty list indicates
            a pure computation with no external effects. The list should
            be exhaustive - omitting a side effect category may lead to
            incorrect assumptions by the runtime.
        """
        ...

    @property
    def retry_safe(self) -> bool:
        """
        Whether the handler is safe to retry on failure.

        A retry-safe handler can be re-executed after a failure without
        causing data corruption, duplicate effects, or inconsistent state.
        This property is related to but distinct from idempotency.

        Retry Safety vs Idempotency:
            - Idempotent + Retry Safe: Can retry freely (most desirable)
            - Not Idempotent + Retry Safe: May create duplicates but no corruption
            - Idempotent + Not Retry Safe: Unusual, may indicate partial failures
            - Not Idempotent + Not Retry Safe: Requires careful error handling

        Factors Affecting Retry Safety:
            - Atomic operations are generally retry safe
            - Operations with multiple steps may not be retry safe
            - External service idempotency affects retry safety

        Returns:
            True if the handler can be safely retried, False otherwise.
        """
        ...


# ==============================================================================
# Capability Dependency Protocol
# ==============================================================================


@runtime_checkable
class ProtocolCapabilityDependency(Protocol):
    """
    Protocol for representing a capability dependency for a handler.

    A capability dependency declares that a handler requires or optionally
    uses a specific capability provided by the runtime environment. This
    enables dependency injection, capability checking at registration time,
    and graceful degradation when optional capabilities are unavailable.

    Capability dependencies support:
        - Required vs optional capabilities
        - Semantic version constraints for compatibility
        - Runtime capability discovery and injection
        - Handler validation before execution

    This protocol is useful for:
        - Handler registration validation
        - Dependency injection configuration
        - Feature flag integration
        - Graceful degradation strategies
        - Capability-based security models

    Attributes:
        capability_name: Identifier for the required capability.
        required: Whether the capability must be present for the handler to work.
        version_constraint: Optional semantic version constraint string.

    Example:
        ```python
        class DatabaseCapabilityDep:
            '''Dependency on PostgreSQL database capability.'''

            @property
            def capability_name(self) -> str:
                return "database.postgresql"

            @property
            def required(self) -> bool:
                return True  # Handler cannot function without database

            @property
            def version_constraint(self) -> str | None:
                return ">=14.0.0"  # Requires PostgreSQL 14+

        class CacheCapabilityDep:
            '''Optional dependency on Redis cache.'''

            @property
            def capability_name(self) -> str:
                return "cache.redis"

            @property
            def required(self) -> bool:
                return False  # Handler works without cache, just slower

            @property
            def version_constraint(self) -> str | None:
                return None  # Any version acceptable

        db_dep = DatabaseCapabilityDep()
        cache_dep = CacheCapabilityDep()

        assert isinstance(db_dep, ProtocolCapabilityDependency)

        # Runtime checks capabilities before handler execution
        if db_dep.required and not runtime.has_capability(db_dep.capability_name):
            raise MissingCapabilityError(db_dep.capability_name)
        ```

    Note:
        Capability names should follow a hierarchical naming convention
        (e.g., "database.postgresql", "cache.redis", "messaging.kafka")
        to enable namespace-based capability discovery and grouping.

    See Also:
        ProtocolHandlerContract: Aggregates capability dependencies.
        ProtocolServiceRegistry: Provides capability discovery.
    """

    @property
    def capability_name(self) -> str:
        """
        Name of the required capability.

        The capability name serves as a unique identifier for the capability
        within the runtime environment. Names should follow a hierarchical
        dotted notation for organization and discovery.

        Naming Convention:
            - Format: "{category}.{specific}" or "{category}.{subcategory}.{specific}"
            - Examples: "database.postgresql", "cache.redis", "auth.oauth2.google"
            - Case: lowercase with dots as separators

        Common Capability Categories:
            - "database.*": Database connections (postgresql, mysql, mongodb)
            - "cache.*": Caching systems (redis, memcached)
            - "messaging.*": Message brokers (kafka, rabbitmq)
            - "storage.*": Object storage (s3, gcs, azure)
            - "auth.*": Authentication providers
            - "metrics.*": Metrics and monitoring systems

        Returns:
            String identifier for the capability (e.g., "database.postgresql").
        """
        ...

    @property
    def required(self) -> bool:
        """
        Whether this capability is required (vs optional).

        Required capabilities must be available for the handler to function.
        Optional capabilities enhance handler functionality but the handler
        can operate without them, possibly with reduced functionality.

        Behavior by Setting:
            - True (required): Handler registration fails if capability missing
            - False (optional): Handler proceeds, may use fallback behavior

        Returns:
            True if the capability is required, False if optional.
        """
        ...

    @property
    def version_constraint(self) -> str | None:
        """
        Optional semantic version constraint for the capability.

        Version constraints follow semantic versioning (semver) syntax to
        specify compatible capability versions. This enables handlers to
        declare minimum versions, exact versions, or version ranges.

        Supported Constraint Syntax:
            - ">=1.0.0": Version 1.0.0 or higher
            - ">=1.0.0,<2.0.0": Version 1.x only
            - "==1.2.3": Exact version match
            - "^1.0.0": Compatible with 1.0.0 (same as >=1.0.0,<2.0.0)
            - "~1.2.0": Approximately 1.2.0 (same as >=1.2.0,<1.3.0)

        Examples:
            - ">=14.0.0" for PostgreSQL 14+
            - ">=6.0.0,<8.0.0" for Redis 6.x or 7.x
            - None for any version acceptable

        Returns:
            Semantic version constraint string, or None if any version
            is acceptable. Constraint syntax follows Python packaging
            version specifier conventions (PEP 440).
        """
        ...


# ==============================================================================
# Execution Constraints Protocol
# ==============================================================================


@runtime_checkable
class ProtocolExecutionConstraints(Protocol):
    """
    Protocol for defining execution constraints for a handler.

    Execution constraints specify resource limits and operational boundaries
    for handler execution. These constraints enable the runtime to enforce
    resource governance, prevent runaway operations, and ensure fair
    resource allocation in multi-tenant environments.

    Execution constraints cover:
        - Retry behavior (max attempts before giving up)
        - Timeout limits (maximum execution duration)
        - Resource limits (memory, CPU allocation)
        - Concurrency limits (parallel execution cap)

    This protocol is useful for:
        - Resource governance and quota enforcement
        - SLA compliance and timeout management
        - Retry policy configuration
        - Container/serverless resource allocation
        - Rate limiting and backpressure

    Attributes:
        max_retries: Maximum retry attempts before failure.
        timeout_seconds: Maximum execution time allowed.
        memory_limit_mb: Optional memory allocation limit.
        cpu_limit: Optional CPU allocation limit.
        concurrency_limit: Optional maximum concurrent executions.

    Example:
        ```python
        class DefaultExecutionConstraints:
            '''Standard execution constraints for production handlers.'''

            @property
            def max_retries(self) -> int:
                return 3  # Try up to 3 times

            @property
            def timeout_seconds(self) -> float:
                return 30.0  # 30 second timeout

            @property
            def memory_limit_mb(self) -> int | None:
                return 512  # 512MB memory limit

            @property
            def cpu_limit(self) -> float | None:
                return 1.0  # One full CPU core

            @property
            def concurrency_limit(self) -> int | None:
                return 10  # Max 10 concurrent executions

        class HighThroughputConstraints:
            '''Constraints for high-throughput, low-latency handlers.'''

            @property
            def max_retries(self) -> int:
                return 1  # Fail fast, no retries

            @property
            def timeout_seconds(self) -> float:
                return 5.0  # Strict 5 second timeout

            @property
            def memory_limit_mb(self) -> int | None:
                return None  # No memory limit

            @property
            def cpu_limit(self) -> float | None:
                return None  # No CPU limit

            @property
            def concurrency_limit(self) -> int | None:
                return 100  # High concurrency allowed

        constraints = DefaultExecutionConstraints()
        assert isinstance(constraints, ProtocolExecutionConstraints)

        # Runtime uses constraints for execution governance
        async with timeout(constraints.timeout_seconds):
            for attempt in range(constraints.max_retries + 1):
                try:
                    result = await handler.execute(input_data)
                    break
                except RetryableError:
                    if attempt == constraints.max_retries:
                        raise MaxRetriesExceededError()
        ```

    Note:
        Constraints with None values indicate no limit for that resource.
        The runtime should have sensible defaults for None values to
        prevent resource exhaustion.

    See Also:
        ProtocolHandlerBehaviorDescriptor: Determines if retries are safe.
        ProtocolHandlerContract: Aggregates constraints with other specs.
    """

    @property
    def max_retries(self) -> int:
        """
        Maximum number of retry attempts.

        Specifies how many times the runtime should retry a failed handler
        execution before giving up and propagating the error. The total
        number of execution attempts is max_retries + 1 (initial + retries).

        Retry Behavior:
            - 0: No retries, fail immediately on first error
            - 1-3: Standard retry count for transient failures
            - 5+: High retry count for unreliable external services

        Important:
            Only retry if the handler's behavior descriptor indicates
            retry_safe is True. Retrying non-retry-safe handlers may
            cause data corruption or duplicate effects.

        Returns:
            Non-negative integer specifying maximum retry attempts.
            A value of 0 means no retries (single attempt only).
        """
        ...

    @property
    def timeout_seconds(self) -> float:
        """
        Execution timeout in seconds.

        Specifies the maximum duration a single handler execution may run
        before being forcibly terminated. This prevents runaway operations
        and ensures bounded execution time.

        Timeout Considerations:
            - Include network latency for external service calls
            - Account for retry delays if retries are configured
            - Consider downstream timeout chains (avoid timeout < downstream)

        Common Timeout Values:
            - 1-5 seconds: Fast operations, cache lookups
            - 10-30 seconds: Standard API calls, database queries
            - 60-300 seconds: Batch operations, file processing
            - 300+ seconds: Long-running jobs (use async patterns instead)

        Returns:
            Positive float specifying timeout in seconds. Must be > 0.
        """
        ...

    @property
    def memory_limit_mb(self) -> int | None:
        """
        Optional memory limit in megabytes.

        Specifies the maximum memory allocation for handler execution.
        Used for container resource allocation and preventing memory
        exhaustion in shared environments.

        Memory Limit Usage:
            - Container environments: Sets container memory limit
            - Serverless: Configures function memory allocation
            - Process isolation: Enforces memory quota

        Common Memory Limits:
            - 128-256 MB: Simple handlers, stateless operations
            - 512-1024 MB: Standard handlers with moderate data
            - 2048+ MB: Data-intensive handlers, large payloads

        Returns:
            Positive integer specifying memory limit in megabytes,
            or None if no limit should be enforced. A value of None
            means the runtime default applies.
        """
        ...

    @property
    def cpu_limit(self) -> float | None:
        """
        Optional CPU limit as a fraction of cores.

        Specifies the maximum CPU allocation for handler execution.
        Values are expressed as fractions of CPU cores.

        CPU Limit Values:
            - 0.1: 10% of one CPU core
            - 0.5: Half of one CPU core
            - 1.0: One full CPU core
            - 2.0: Two CPU cores
            - None: No limit (use all available)

        Usage Contexts:
            - Kubernetes: Maps to resources.limits.cpu
            - Docker: Maps to --cpus flag
            - Serverless: May affect pricing tier

        Returns:
            Positive float specifying CPU limit as core fraction,
            or None if no limit should be enforced. A value of None
            means the runtime default applies.
        """
        ...

    @property
    def concurrency_limit(self) -> int | None:
        """
        Optional maximum concurrent executions.

        Specifies the maximum number of simultaneous executions of this
        handler. Used for rate limiting, preventing resource exhaustion,
        and protecting downstream services.

        Concurrency Considerations:
            - Database handlers: Limit by connection pool size
            - External API handlers: Limit by rate limit quota
            - CPU-intensive handlers: Limit by available cores
            - Memory-intensive handlers: Limit by available memory

        Common Concurrency Limits:
            - 1: Serialize all executions (mutex behavior)
            - 5-10: Conservative limit for shared resources
            - 50-100: Standard limit for scalable handlers
            - None: No limit (bounded only by system resources)

        Returns:
            Positive integer specifying maximum concurrent executions,
            or None if no limit should be enforced. A value of None
            means unlimited concurrency (bounded only by system capacity).
        """
        ...


# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "ProtocolCapabilityDependency",
    "ProtocolExecutionConstraints",
    "ProtocolHandlerBehaviorDescriptor",
]
