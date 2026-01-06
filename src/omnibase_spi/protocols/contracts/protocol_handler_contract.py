"""
Protocol for handler contracts - type-safe handler contract access.

Domain: Handler contract interface for declarative handler specification.

This module defines the main ProtocolHandlerContract interface that aggregates
handler identity, behavior characteristics, capability dependencies, and
execution constraints into a single, type-safe contract specification.

Handler contracts serve as the source of truth for:
    - Handler identification (id, name, version)
    - Behavior specification (idempotency, side effects, retry safety, timeouts)
    - Capability requirements (what the handler needs to run)
    - Execution constraints (ordering, parallelism, must-run flags)

The contract supports validation for ensuring contract correctness before
handler registration. Serialization is handled by the implementing model
(ModelHandlerContract in omnibase_core) using Pydantic's model_dump/model_validate.

See Also:
    - protocol_handler_contract_types.py: Supporting protocols (behavior, capabilities, constraints)
    - protocol_validation.py: Validation result protocol
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.contracts.protocol_handler_contract_types import (
        ProtocolCapabilityDependency,
        ProtocolExecutionConstraints,
        ProtocolHandlerBehaviorDescriptor,
    )
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )


# ==============================================================================
# Handler Contract Protocol
# ==============================================================================


@runtime_checkable
class ProtocolHandlerContract(Protocol):
    """
    Interface for handler contracts - can be mocked by dependent tickets.

    A handler contract defines the complete specification for a handler,
    including its identity, behavior characteristics, capability dependencies,
    and execution constraints. This protocol enables type-safe access to
    handler contract information.

    The contract serves as the source of truth for:
        - Handler identification (handler_id, name, version)
        - Behavior specification (idempotency, side effects, retry safety, timeouts)
        - Capability requirements (what the handler needs to run)
        - Execution constraints (ordering, parallelism, must-run flags)

    This protocol is useful for:
        - Handler registration validation
        - Runtime capability checking
        - Contract-driven handler discovery
        - Handler metadata introspection

    Attributes:
        handler_id: Unique identifier for this handler.
        name: Human-readable name for this handler.
        version: Semantic version of this handler contract.
        descriptor: Behavior descriptor for this handler.
        capability_inputs: List of capability dependencies required by this handler.
        execution_constraints: Execution constraints for this handler.

    Example:
        ```python
        async def inspect_contract() -> None:
            # Create a handler contract instance
            contract: ProtocolHandlerContract = get_handler_contract()

            # Access contract properties
            print(f"Handler: {contract.name} v{contract.version}")
            print(f"Idempotent: {contract.descriptor.idempotent}")

            # Check capability requirements
            for cap in contract.capability_inputs:
                if cap.strict:
                    print(f"Requires: {cap.capability}")

            # Validate the contract (async operation)
            result = await contract.validate()
            if not result.is_valid:
                for error in result.errors:
                    print(f"Error: {error.message}")

            # Note: Serialization (e.g., model_dump()) is provided by the
            # implementing class (ModelHandlerContract), not this protocol.
        ```

    Note:
        This protocol is intended to be implemented by ModelHandlerContract
        in omnibase_core (OMN-1117). The protocol enables loose coupling
        between SPI and Core while maintaining type safety. Serialization
        is handled by Pydantic's model_dump() and model_validate() methods
        on the implementing model class.

    See Also:
        ProtocolHandlerBehaviorDescriptor: Behavior characteristics
        ProtocolCapabilityDependency: Capability requirements
        ProtocolExecutionConstraints: Runtime constraints
        ProtocolValidationResult: Validation outcome
    """

    @property
    def handler_id(self) -> str:
        """
        Unique identifier for this handler.

        The handler ID provides a globally unique identifier for this handler
        contract. This ID is used for handler lookup, registration tracking,
        and audit logging.

        ID Format Recommendations:
            - UUID: "550e8400-e29b-41d4-a716-446655440000"
            - URN: "urn:onex:handler:http-rest:v1"
            - Hierarchical: "com.example.handlers.http_rest"

        Important:
            The handler_id MUST be unique across all registered handlers.
            Duplicate IDs will cause registration conflicts.

        Returns:
            A globally unique identifier string (typically UUID or URN).
        """
        ...

    @property
    def name(self) -> str:
        """
        Human-readable name for this handler.

        The handler name provides a descriptive identifier suitable for
        display in logs, monitoring dashboards, and administrative interfaces.
        Unlike handler_id, the name does not need to be globally unique but
        should be descriptive enough to identify the handler's purpose.

        Naming Recommendations:
            - Use lowercase with hyphens: "http-rest-handler"
            - Include handler type: "kafka-consumer-handler"
            - Be descriptive: "user-authentication-handler"

        Returns:
            Handler name suitable for display and logging.
        """
        ...

    @property
    def version(self) -> str:
        """
        Semantic version of this handler contract.

        The version follows semantic versioning (semver) conventions to
        communicate compatibility and changes:
            - MAJOR: Breaking changes to the contract interface
            - MINOR: New features, backward compatible
            - PATCH: Bug fixes, backward compatible

        Version Examples:
            - "1.0.0": Initial stable release
            - "1.2.3": Minor feature additions with patches
            - "2.0.0": Breaking changes from v1

        Important:
            Version changes should be coordinated with the handler
            implementation to ensure contract-implementation compatibility.

        Returns:
            Version string in semver format (e.g., "1.2.3").
        """
        ...

    @property
    def descriptor(self) -> ProtocolHandlerBehaviorDescriptor:
        """
        Behavior descriptor for this handler.

        The behavior descriptor provides semantic information about how
        the handler operates, enabling the runtime to make informed
        decisions about caching, retrying, and scheduling.

        Descriptor Properties:
            - idempotent: Can the operation be safely repeated?
            - deterministic: Will the same input produce the same output?
            - side_effects: What external effects does the handler produce?
            - retry_safe: Can the handler be safely retried on failure?

        Returns:
            Descriptor specifying behavioral characteristics.
        """
        ...

    @property
    def capability_inputs(self) -> list[ProtocolCapabilityDependency]:
        """
        List of capability dependencies required by this handler.

        Capability dependencies declare what external capabilities the
        handler needs to function. The runtime uses this information to:
            - Validate all required capabilities are available before registration
            - Inject capability instances at handler initialization
            - Enable graceful degradation when optional capabilities are missing

        Capability Examples:
            - "database.postgresql": PostgreSQL database connection
            - "cache.redis": Redis cache client
            - "messaging.kafka": Kafka producer/consumer

        Returns:
            List of capability dependencies. May be empty if handler
            has no external capability requirements.
        """
        ...

    @property
    def execution_constraints(self) -> ProtocolExecutionConstraints | None:
        """
        Execution constraints for this handler.

        Execution constraints specify ordering requirements and parallelism
        settings for handler execution. These constraints enable:
            - Explicit ordering dependencies between handlers
            - Parallel execution control
            - Mandatory execution flags for side-effect handlers
            - Nondeterminism tracking for replay/recovery

        Constraint Properties:
            - requires_before: Handlers that must complete before this one starts
            - requires_after: Handlers that must run after this one completes
            - must_run: Whether this handler must run even if not strictly needed
            - can_run_parallel: Whether this handler can run in parallel with others
            - nondeterministic_effect: Whether this handler has nondeterministic effects

        Note:
            Resource settings (such as timeout_ms and isolation_policy) are
            defined in the behavior descriptor (ProtocolHandlerBehaviorDescriptor),
            not here. Execution constraints focus on ordering and parallelism.

        Returns:
            Constraints if specified, None for default constraints.
            When None, the runtime should apply sensible defaults.
        """
        ...

    async def validate(self) -> ProtocolValidationResult:
        """
        Validate this contract for correctness.

        Performs validation of the contract structure and values,
        including checking for required fields and valid ranges.

        Validation Checks:
            - Required fields are present and non-empty
            - Version string follows semver format
            - Constraint values are within valid ranges (e.g., timeout > 0)
            - Capability names follow naming conventions
            - No conflicting configuration values

        Usage:
            ```python
            result = await contract.validate()
            if not result.is_valid:
                for error in result.errors:
                    logger.error(f"Contract error: {error.message}")
                raise InvalidContractError(result.errors)
            ```

        Returns:
            Validation result with is_valid status and any errors.

        Raises:
            RuntimeError: If validation cannot be completed due to
                internal errors (e.g., missing validator dependencies).
            TypeError: If contract fields have unexpected types that
                prevent validation from proceeding.
        """
        ...


# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "ProtocolHandlerContract",
]
