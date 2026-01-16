"""Protocol for ONEX effect nodes (legacy).

.. deprecated:: 0.3.0
    This module contains the legacy ONEX effect node protocol.
    For new implementations, use the canonical v0.3.0 protocol at
    :class:`omnibase_spi.protocols.nodes.ProtocolEffectNode`.

    This legacy protocol will be removed in v0.5.0.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolOnexEffectNodeLegacy(Protocol):
    """
    Legacy protocol for ONEX effect node implementations.

    .. deprecated:: 0.3.0
        This protocol is deprecated. Use
        :class:`omnibase_spi.protocols.nodes.ProtocolEffectNode` instead.

        Migration path:
            - Replace imports from ``protocols.onex`` with ``protocols.nodes``
            - Update type hints to use ``ProtocolEffectNode``
            - Implement the new interface methods as needed

        This protocol will be removed in v0.5.0.

    Effect nodes perform side-effecting operations such as I/O, external API calls,
    database operations, file system access, and other interactions with external
    systems. They encapsulate all operations that have observable effects outside
    the workflow's computational context.

    Key Responsibilities:
        - External API and service integration
        - Database read/write operations
        - File system operations
        - Message queue publishing
        - Network requests and responses
        - Third-party service interactions

    Implementation Notes:
        Effect nodes should:
        - Implement proper retry logic with exponential backoff
        - Use circuit breakers for external service calls
        - Log all side effects for audit and debugging
        - Support idempotent operations where possible
        - Handle timeouts and partial failures gracefully
        - Clean up resources in error scenarios

    Type Safety:
        This protocol is runtime checkable, enabling isinstance() validation
        for dynamic node loading and dependency injection systems.

    Example Usage:
        ```python
        from omnibase_spi.protocols.onex import ProtocolOnexEffectNodeLegacy

        class MyEffect:
            async def execute_effect(self, contract: EffectContract) -> EffectResult:
                # Perform external I/O operation
                ...

            @property
            def node_id(self) -> str:
                return "effect-api-call-1"

            @property
            def node_type(self) -> str:
                return "effect"

        # Runtime validation
        effect = MyEffect()
        assert isinstance(effect, ProtocolOnexEffectNodeLegacy)
        ```

    Common Patterns:
        - API Gateway: External REST/GraphQL API calls
        - Database Operations: CRUD operations on persistent storage
        - File Processing: Read/write files, S3 operations
        - Message Publishing: Kafka, RabbitMQ, SQS interactions
        - Cache Operations: Redis, Memcached reads/writes
    """

    async def execute_effect(self, contract: object) -> object:
        """
        Execute effect workflow.

        Performs a side-effecting operation that interacts with external systems
        or produces observable changes outside the workflow's computational context.

        Args:
            contract: Effect contract containing operation configuration,
                     authentication credentials, input data, and retry policies.
                     Type is typically a ModelContract subclass specific
                     to the effect operation.

        Returns:
            Effect result containing the operation response, status information,
            and any data retrieved from external systems. Return type matches
            the contract's output specification.

        Raises:
            ExternalServiceError: When external service calls fail
            TimeoutError: When operations exceed configured timeouts
            AuthenticationError: When credentials are invalid or expired
            NetworkError: When network connectivity issues occur
            RetryExhaustedError: When retry attempts are exhausted

        Implementation Requirements:
            - Must implement retry logic with exponential backoff
            - Should use circuit breakers for external service protection
            - Must log all operations for audit trails
            - Should handle partial failures and timeouts gracefully
            - Must clean up resources (connections, files) on errors
            - Should emit metrics for operation duration and success rates
            - Must support idempotent operations where applicable
            - Should validate inputs before performing side effects
        """
        ...

    @property
    def node_id(self) -> str:
        """
        Get unique node identifier.

        Returns a globally unique identifier for this effect node instance.
        Used for node registration, discovery, and tracking in distributed systems.

        Returns:
            str: Unique node identifier, typically in format:
                 "effect-{operation-type}-{instance-id}"

        Implementation Notes:
            - Must be unique across all nodes in the system
            - Should be stable across restarts for workflow replay
            - Used as key in service registry and discovery systems
            - Included in all workflow events for tracing
            - Helpful for debugging and audit log correlation
        """
        ...

    @property
    def node_type(self) -> str:
        """
        Get node type identifier.

        Returns the node type classification for this effect node.
        Used for node routing, capability discovery, and workflow planning.

        Returns:
            str: Node type identifier, always "effect" for this protocol.
                 May include subtypes like "effect:http", "effect:database",
                 or "effect:file" for specialized implementations.

        Implementation Notes:
            - Must return "effect" or a subtype of effect
            - Used by node registry for capability-based routing
            - Enables workflow engine to select appropriate effect nodes
            - May be used for load balancing and rate limiting
            - Helps identify which nodes require external connectivity
        """
        ...
