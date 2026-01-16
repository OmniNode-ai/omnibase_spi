"""
Handler contract supporting types and protocols for ONEX SPI interfaces.

Domain: Handler contract type definitions for behavior, capabilities, and constraints.

This module defines the foundational protocols for describing handler contracts,
including behavior characteristics, capability dependencies, and execution constraints.
These protocols are used by ProtocolHandlerContract to provide a complete specification
of handler requirements and guarantees.

Protocol Categories:
    - ProtocolHandlerBehaviorDescriptor: Describes behavioral characteristics
      (handler kind, purity, idempotency, retry policy, concurrency)
    - ProtocolCapabilityDependency: Represents required or optional capabilities
      with version constraints and selection policies
    - ProtocolExecutionConstraints: Defines execution ordering and parallelism
      (requires_before, requires_after, can_run_parallel)

See Also:
    - protocol_handler_contract.py: The main ProtocolHandlerContract interface
    - types.py: Handler descriptor and source type definitions
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md

Note:
    Property names in these protocols match corresponding field names in
    omnibase_core models (ModelHandlerBehavior, ModelCapabilityDependency,
    ModelExecutionConstraints) to ensure type compatibility.
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from omnibase_core.types import JsonType

# ==============================================================================
# Supporting Protocol Types
# ==============================================================================


@runtime_checkable
class ProtocolDescriptorRetryPolicy(Protocol):
    """
    Protocol for retry policy descriptor configuration.

    Defines how failed handler executions should be retried, including
    backoff strategies and limits. This is a descriptor protocol used
    in handler behavior specifications.

    Matches ModelDescriptorRetryPolicy in omnibase_core.

    Note:
        This differs from ProtocolRetryPolicy in types/protocol_retry_types.py,
        which defines a comprehensive retry policy with error-specific configs.
        This protocol is specifically for handler behavior descriptors.

    Attributes:
        enabled: Whether retry is enabled.
        max_retries: Maximum number of retry attempts.
        backoff_strategy: Strategy for increasing delay between retries.
        base_delay_ms: Initial delay before first retry.
        max_delay_ms: Maximum delay between retries.
        jitter_factor: Random jitter factor to prevent thundering herd.
    """

    @property
    def enabled(self) -> bool:
        """Whether retry is enabled.

        Returns:
            True if retry is enabled, False otherwise.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid boolean value.
        """
        ...

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts.

        Returns:
            Non-negative integer specifying the maximum retry count.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid non-negative integer.
        """
        ...

    @property
    def backoff_strategy(self) -> Literal["fixed", "exponential", "linear"]:
        """Strategy for increasing delay between retries.

        Backoff Strategies:
            - fixed: Same delay between each retry attempt
            - exponential: Delay doubles after each attempt
            - linear: Delay increases linearly with each attempt

        Returns:
            One of "fixed", "exponential", or "linear".

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid backoff strategy literal.
        """
        ...

    @property
    def base_delay_ms(self) -> int:
        """Initial delay in milliseconds before first retry.

        Returns:
            Positive integer specifying the base delay in milliseconds.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid positive integer.
        """
        ...

    @property
    def max_delay_ms(self) -> int:
        """Maximum delay in milliseconds between retries.

        Returns:
            Positive integer specifying the maximum delay cap in milliseconds.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid positive integer.
        """
        ...

    @property
    def jitter_factor(self) -> float:
        """Random jitter factor to prevent thundering herd.

        Jitter adds randomness to retry delays to prevent multiple clients
        from retrying simultaneously after a shared failure.

        Returns:
            Float between 0.0 and 1.0 representing the jitter percentage.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid float value.
        """
        ...


@runtime_checkable
class ProtocolDescriptorCircuitBreaker(Protocol):
    """
    Protocol for circuit breaker descriptor configuration.

    Defines circuit breaker behavior to prevent cascading failures.
    This is a descriptor protocol used in handler behavior specifications.

    Matches ModelDescriptorCircuitBreaker in omnibase_core.

    Note:
        This differs from ProtocolCircuitBreaker in networking/protocol_circuit_breaker.py,
        which defines a runtime circuit breaker with methods like get_state() and call().
        This protocol is specifically for handler behavior descriptors.

    Attributes:
        enabled: Whether circuit breaker is enabled.
        failure_threshold: Number of failures before opening circuit.
        success_threshold: Successes needed to close circuit from half-open.
        timeout_ms: Time in milliseconds before attempting recovery.
        half_open_requests: Number of requests allowed in half-open state.
    """

    @property
    def enabled(self) -> bool:
        """Whether circuit breaker is enabled.

        Returns:
            True if circuit breaker protection is enabled, False otherwise.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid boolean value.
        """
        ...

    @property
    def failure_threshold(self) -> int:
        """Number of consecutive failures before opening the circuit.

        When the failure count reaches this threshold, the circuit opens
        and subsequent requests fail immediately without attempting execution.

        Returns:
            Positive integer specifying the failure threshold count.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid positive integer.
        """
        ...

    @property
    def success_threshold(self) -> int:
        """Number of successes needed to close circuit from half-open state.

        When the circuit is half-open, this many consecutive successes
        are required before the circuit fully closes and normal operation
        resumes.

        Returns:
            Positive integer specifying the success threshold count.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid positive integer.
        """
        ...

    @property
    def timeout_ms(self) -> int:
        """Time in milliseconds before attempting to close the circuit.

        After the circuit opens, it remains open for this duration before
        transitioning to half-open state where test requests are allowed.

        Returns:
            Positive integer specifying the timeout duration in milliseconds.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid positive integer.
        """
        ...

    @property
    def half_open_requests(self) -> int:
        """Number of test requests allowed when circuit is half-open.

        In the half-open state, this many requests are allowed through
        to test if the underlying service has recovered.

        Returns:
            Positive integer specifying the number of test requests allowed.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid positive integer.
        """
        ...


@runtime_checkable
class ProtocolCapabilityRequirementSet(Protocol):
    """
    Protocol for capability requirement specifications.

    Defines a structured set of requirements for capability matching.
    Used in ProtocolCapabilityDependency to specify matching criteria.

    Matches ModelRequirementSet in omnibase_core.

    Attributes:
        must: Requirements that must be satisfied.
        prefer: Requirements that are preferred but not mandatory.
        forbid: Requirements that must not be present.
        hints: Additional hints for capability selection.
    """

    @property
    def must(self) -> JsonType:
        """Requirements that must be satisfied for capability matching.

        Returns:
            JSON-compatible dictionary of mandatory requirements.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid JSON-compatible value.
        """
        ...

    @property
    def prefer(self) -> JsonType:
        """Requirements that are preferred but not mandatory.

        Returns:
            JSON-compatible dictionary of preferred requirements.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid JSON-compatible value.
        """
        ...

    @property
    def forbid(self) -> JsonType:
        """Requirements that must not be present.

        Returns:
            JSON-compatible dictionary of forbidden requirements.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid JSON-compatible value.
        """
        ...

    @property
    def hints(self) -> JsonType:
        """Additional hints for capability selection.

        Returns:
            JSON-compatible dictionary of selection hints.

        Raises:
            This property should not raise exceptions. Implementations must
            return a valid JSON-compatible value.
        """
        ...


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

    This protocol matches the fields of ModelHandlerBehavior in omnibase_core.

    Attributes:
        handler_kind: The type of handler (compute, effect, reducer, orchestrator).
        purity: Whether the handler is pure or has side effects.
        idempotent: Whether calling the handler multiple times with the same
            input produces the same result without additional side effects.
        timeout_ms: Optional timeout in milliseconds for handler execution.
        retry_policy: Optional retry policy configuration.
        circuit_breaker: Optional circuit breaker configuration.
        concurrency_policy: How concurrent executions should be handled.
        isolation_policy: Resource isolation level for execution.
        observability_level: Level of observability/tracing to apply.
        capability_inputs: List of capability names this handler consumes.
        capability_outputs: List of capability names this handler produces.

    Example:
        ```python
        class ComputeHandlerBehavior:
            '''Behavior descriptor for a pure compute handler.'''

            @property
            def handler_kind(self) -> Literal["compute", "effect", "reducer", "orchestrator"]:
                return "compute"

            @property
            def purity(self) -> Literal["pure", "side_effecting"]:
                return "pure"

            @property
            def idempotent(self) -> bool:
                return True

            @property
            def timeout_ms(self) -> int | None:
                return 5000  # 5 second timeout

            @property
            def concurrency_policy(self) -> Literal["parallel_ok", "serialized", "singleflight"]:
                return "parallel_ok"

            @property
            def isolation_policy(self) -> Literal["none", "process", "container", "vm"]:
                return "none"

            @property
            def observability_level(self) -> Literal["minimal", "standard", "verbose"]:
                return "standard"

            @property
            def capability_inputs(self) -> list[str]:
                return ["text_input"]

            @property
            def capability_outputs(self) -> list[str]:
                return ["text_output"]

        behavior = ComputeHandlerBehavior()
        assert isinstance(behavior, ProtocolHandlerBehaviorDescriptor)
        ```

    See Also:
        ProtocolHandlerContract: Uses behavior descriptors for contract specs.
        ProtocolExecutionConstraints: Defines execution ordering.
        ModelHandlerBehavior: The corresponding Pydantic model in omnibase_core.
    """

    @property
    def handler_kind(self) -> Literal["compute", "effect", "reducer", "orchestrator"]:
        """
        The type of handler.

        Handler kinds determine the fundamental behavior and guarantees:
            - compute: Pure transformations without side effects
            - effect: Operations that interact with external systems
            - reducer: Aggregation operations that combine multiple inputs
            - orchestrator: Workflow coordination that manages other handlers

        Returns:
            One of "compute", "effect", "reducer", or "orchestrator".
        """
        ...

    @property
    def purity(self) -> Literal["pure", "side_effecting"]:
        """
        Whether the handler is pure or has side effects.

        Purity Implications:
            - pure: No side effects, safe to cache, memoize, or parallelize
            - side_effecting: May have observable effects beyond return value

        Returns:
            "pure" for handlers without side effects, "side_effecting" otherwise.
        """
        ...

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

        Examples of Non-Idempotent Operations:
            - HTTP POST (creates new resource each time)
            - Incrementing a counter
            - Sending an email or notification

        Returns:
            True if the operation is idempotent, False otherwise.
        """
        ...

    @property
    def timeout_ms(self) -> int | None:
        """
        Optional execution timeout in milliseconds.

        Specifies the maximum duration a single handler execution may run
        before being forcibly terminated. This prevents runaway operations
        and ensures bounded execution time.

        Common Timeout Values:
            - 1000-5000: Fast operations, cache lookups
            - 10000-30000: Standard API calls, database queries
            - 60000-300000: Batch operations, file processing
            - None: No timeout limit (use with caution)

        Returns:
            Positive integer specifying timeout in milliseconds,
            or None if no timeout should be enforced.
        """
        ...

    @property
    def retry_policy(self) -> ProtocolDescriptorRetryPolicy | None:
        """
        Optional retry policy configuration.

        Defines how failed handler executions should be retried,
        including backoff strategy and limits.

        Returns:
            Retry policy configuration, or None if no retry policy.
        """
        ...

    @property
    def circuit_breaker(self) -> ProtocolDescriptorCircuitBreaker | None:
        """
        Optional circuit breaker configuration.

        Defines circuit breaker behavior to prevent cascading failures
        when a handler repeatedly fails.

        Returns:
            Circuit breaker configuration, or None if not enabled.
        """
        ...

    @property
    def concurrency_policy(
        self,
    ) -> Literal["parallel_ok", "serialized", "singleflight"]:
        """
        How concurrent executions should be handled.

        Concurrency Policies:
            - parallel_ok: Multiple executions can run simultaneously
            - serialized: Executions are queued and run one at a time
            - singleflight: Duplicate requests share a single execution

        Returns:
            The concurrency policy for this handler.
        """
        ...

    @property
    def isolation_policy(self) -> Literal["none", "process", "container", "vm"]:
        """
        Resource isolation level for handler execution.

        Isolation Levels:
            - none: Runs in the same process (default, fastest)
            - process: Runs in a separate process
            - container: Runs in an isolated container
            - vm: Runs in a virtual machine (maximum isolation)

        Returns:
            The isolation policy for this handler.
        """
        ...

    @property
    def observability_level(self) -> Literal["minimal", "standard", "verbose"]:
        """
        Level of observability/tracing to apply.

        Observability Levels:
            - minimal: Basic metrics only (errors, latency)
            - standard: Standard tracing with key events
            - verbose: Full tracing with all intermediate states

        Returns:
            The observability level for this handler.
        """
        ...

    @property
    def capability_inputs(self) -> list[str]:
        """
        List of capability names this handler consumes.

        Capability inputs declare what capabilities the handler requires
        to function. These are used for dependency validation and
        capability-based routing.

        Returns:
            List of capability name strings that this handler consumes.
        """
        ...

    @property
    def capability_outputs(self) -> list[str]:
        """
        List of capability names this handler produces.

        Capability outputs declare what capabilities the handler provides
        after execution. These are used for capability chaining and
        workflow composition.

        Returns:
            List of capability name strings that this handler produces.
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

    This protocol matches the fields of ModelCapabilityDependency in omnibase_core.

    Attributes:
        alias: Local name used to reference this capability in the handler.
        capability: The capability identifier being required.
        requirements: Structured requirement set for capability matching.
        selection_policy: Policy for selecting among multiple providers.
        strict: Whether the capability must be present (True) or is optional (False).
        version_range: Optional semantic version constraint string.
        vendor_hints: Optional vendor-specific configuration hints.
        description: Optional human-readable description of this dependency.

    Example:
        ```python
        class DatabaseCapabilityDep:
            '''Dependency on PostgreSQL database capability.'''

            @property
            def alias(self) -> str:
                return "db"  # Local reference name

            @property
            def capability(self) -> str:
                return "database.postgresql"

            @property
            def strict(self) -> bool:
                return True  # Handler cannot function without database

            @property
            def version_range(self) -> str | None:
                return ">=14.0.0"  # Requires PostgreSQL 14+

            @property
            def selection_policy(self) -> Literal["auto_if_unique", "best_score", "require_explicit"]:
                return "auto_if_unique"

            @property
            def vendor_hints(self) -> "JsonType":
                return {"prefer_read_replica": True}

            @property
            def description(self) -> str | None:
                return "Primary database connection for user data"

        db_dep = DatabaseCapabilityDep()
        assert isinstance(db_dep, ProtocolCapabilityDependency)
        ```

    Note:
        Property names match ModelCapabilityDependency in omnibase_core:
        - `capability` (not `capability_name`)
        - `strict` (not `required`)
        - `version_range` (not `version_constraint`)

    See Also:
        ProtocolHandlerContract: Aggregates capability dependencies.
        ProtocolServiceRegistry: Provides capability discovery.
        ModelCapabilityDependency: The corresponding Pydantic model in omnibase_core.
    """

    @property
    def alias(self) -> str:
        """
        Local name used to reference this capability in the handler.

        The alias provides a stable local reference that the handler code
        uses to access the capability, independent of the actual capability
        name which may vary across environments.

        Example:
            - alias="db" for capability="database.postgresql"
            - alias="cache" for capability="cache.redis"

        Returns:
            String identifier used locally within the handler.
        """
        ...

    @property
    def capability(self) -> str:
        """
        The capability identifier being required.

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

        Returns:
            String identifier for the capability (e.g., "database.postgresql").
        """
        ...

    @property
    def requirements(self) -> ProtocolCapabilityRequirementSet:
        """
        Structured requirement set for capability matching.

        Defines must-have, preferred, forbidden, and hint requirements
        that guide capability provider selection.

        Returns:
            Requirement set for capability matching.
        """
        ...

    @property
    def selection_policy(
        self,
    ) -> Literal["auto_if_unique", "best_score", "require_explicit"]:
        """
        Policy for selecting among multiple capability providers.

        When multiple providers can satisfy a capability requirement,
        this policy determines how the runtime selects one.

        Selection Policies:
            - auto_if_unique: Auto-select if exactly one provider matches
            - best_score: Select the provider with the highest score
            - require_explicit: Require explicit provider specification

        Returns:
            The selection policy for this capability dependency.
        """
        ...

    @property
    def strict(self) -> bool:
        """
        Whether this capability is strictly required (vs optional).

        Strict capabilities must be available for the handler to function.
        Non-strict (optional) capabilities enhance handler functionality but
        the handler can operate without them, possibly with reduced functionality.

        Behavior by Setting:
            - True (strict): Handler registration fails if capability missing
            - False (optional): Handler proceeds, may use fallback behavior

        Returns:
            True if the capability is required, False if optional.
        """
        ...

    @property
    def version_range(self) -> str | None:
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

    @property
    def vendor_hints(self) -> JsonType:
        """
        Optional vendor-specific configuration hints.

        Vendor hints provide implementation-specific configuration that
        may be used by capability providers. These are passed through
        to the provider without interpretation by the runtime.

        Example:
            - {"prefer_read_replica": True} for database capabilities
            - {"region": "us-east-1"} for cloud service capabilities

        Returns:
            Dictionary of vendor-specific hints. May be empty.
        """
        ...

    @property
    def description(self) -> str | None:
        """
        Optional human-readable description of this dependency.

        Provides documentation about why this capability is needed
        and how it is used by the handler.

        Returns:
            Description string, or None if not provided.
        """
        ...


# ==============================================================================
# Execution Constraints Protocol
# ==============================================================================


@runtime_checkable
class ProtocolExecutionConstraints(Protocol):
    """
    Protocol for defining execution constraints for a handler.

    Execution constraints specify ordering requirements and parallelism
    settings for handler execution. These constraints enable the runtime
    to correctly order handler executions and determine which handlers
    can run concurrently.

    This protocol matches the fields of ModelExecutionConstraints in omnibase_core.

    Attributes:
        requires_before: Handlers that must complete before this one starts.
        requires_after: Handlers that must run after this one completes.
        must_run: Whether this handler must run even if not strictly needed.
        can_run_parallel: Whether this handler can run in parallel with others.
        nondeterministic_effect: Whether this handler has nondeterministic effects.

    Example:
        ```python
        class ValidateBeforeSaveConstraints:
            '''Constraints for a handler that must run after validation.'''

            @property
            def requires_before(self) -> list[str]:
                return ["validate_input"]  # Validation must complete first

            @property
            def requires_after(self) -> list[str]:
                return ["notify_completion"]  # Notification runs after

            @property
            def must_run(self) -> bool:
                return True  # Always run this handler

            @property
            def can_run_parallel(self) -> bool:
                return False  # Must run sequentially

            @property
            def nondeterministic_effect(self) -> bool:
                return True  # Has side effects

        constraints = ValidateBeforeSaveConstraints()
        assert isinstance(constraints, ProtocolExecutionConstraints)
        ```

    Note:
        This protocol defines execution ORDERING constraints, not resource
        limits. Resource limits (timeout, memory, CPU) are defined in
        ProtocolHandlerBehaviorDescriptor.

    See Also:
        ProtocolHandlerBehaviorDescriptor: Defines resource limits and policies.
        ProtocolHandlerContract: Aggregates constraints with other specs.
        ModelExecutionConstraints: The corresponding Pydantic model in omnibase_core.
    """

    @property
    def requires_before(self) -> list[str]:
        """
        Handlers that must complete before this one starts.

        Specifies a list of handler identifiers that must successfully
        complete before this handler can begin execution. This creates
        explicit ordering dependencies in the execution graph.

        Example:
            - ["validate_input", "check_permissions"] means both must
              complete before this handler starts

        Returns:
            List of handler identifiers that must run first.
            Empty list means no ordering dependencies.
        """
        ...

    @property
    def requires_after(self) -> list[str]:
        """
        Handlers that must run after this one completes.

        Specifies a list of handler identifiers that should be scheduled
        to run after this handler completes. This is the inverse of
        requires_before and helps with workflow construction.

        Example:
            - ["send_notification", "update_cache"] will be scheduled
              after this handler completes

        Returns:
            List of handler identifiers that should run after.
            Empty list means no subsequent handlers are required.
        """
        ...

    @property
    def must_run(self) -> bool:
        """
        Whether this handler must run even if not strictly needed.

        When True, the handler will be included in the execution plan
        even if its output is not required by other handlers. This is
        useful for handlers with important side effects.

        Use Cases:
            - Audit logging handlers
            - Metrics collection handlers
            - Notification handlers

        Returns:
            True if handler must always run, False if optional.
        """
        ...

    @property
    def can_run_parallel(self) -> bool:
        """
        Whether this handler can run in parallel with others.

        When True, the runtime may execute this handler concurrently
        with other handlers that also allow parallel execution,
        provided there are no ordering conflicts.

        Parallel Execution Considerations:
            - True: Handler is thread-safe and has no shared mutable state
            - False: Handler requires exclusive access to resources

        Returns:
            True if parallel execution is safe, False otherwise.
        """
        ...

    @property
    def nondeterministic_effect(self) -> bool:
        """
        Whether this handler has nondeterministic effects.

        A handler with nondeterministic effects may produce different
        observable side effects on each execution, even with the same
        input. This affects replay and recovery strategies.

        Examples of Nondeterministic Effects:
            - Sending notifications (each send is unique)
            - Writing timestamps
            - Generating random IDs

        Examples of Deterministic Effects:
            - Idempotent database updates
            - Cache writes with consistent keys

        Returns:
            True if effects are nondeterministic, False otherwise.
        """
        ...


# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "ProtocolCapabilityDependency",
    "ProtocolCapabilityRequirementSet",
    "ProtocolDescriptorCircuitBreaker",
    "ProtocolDescriptorRetryPolicy",
    "ProtocolExecutionConstraints",
    "ProtocolHandlerBehaviorDescriptor",
]
