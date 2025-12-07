"""Protocol for primitive effect execution in ONEX kernel.

This module defines the stable interface for effect execution that enables
the ONEX kernel to execute effects without depending on handler implementations.

Stability: Stable
    This protocol is part of the stable SPI contract. Changes require
    careful versioning and migration planning.

Architecture Context:
    This is Phase 1 of the Handler-as-Nodes Architecture roadmap:
    - Phase 1: Stabilize kernel with Primitive Effect SPI (this protocol)
    - Phase 2: Introduce Resource Manager (omnibase_infra)
    - Phase 3: Implement handler-as-nodes (omnibase_infra)
    - Phase 4: Evaluate and expand
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

# Effect categories for grouping related effects
LiteralEffectCategory = Literal[
    "http",  # HTTP/REST API operations
    "db",  # Database operations (SQL, NoSQL)
    "messaging",  # Message queue operations (Kafka, Redis pub/sub)
    "storage",  # File/object storage operations
    "cache",  # Caching operations (Redis, Memcached)
    "secrets",  # Secret management (Vault, etc.)
    "discovery",  # Service discovery (Consul, etc.)
]

# Primitive effect identifiers
# Format: "{category}.{operation}"
LiteralEffectId = Literal[
    # HTTP effects
    "http.request",
    "http.get",
    "http.post",
    "http.put",
    "http.patch",
    "http.delete",
    # Database effects
    "db.query",
    "db.execute",
    "db.transaction",
    # Messaging effects
    "messaging.publish",
    "messaging.consume",
    "messaging.acknowledge",
    # Storage effects
    "storage.read",
    "storage.write",
    "storage.delete",
    "storage.list",
    # Cache effects
    "cache.get",
    "cache.set",
    "cache.delete",
    "cache.invalidate",
    # Secrets effects
    "secrets.get",
    "secrets.set",
    "secrets.delete",
    # Discovery effects
    "discovery.register",
    "discovery.deregister",
    "discovery.lookup",
    "discovery.health",
]


@runtime_checkable
class ProtocolPrimitiveEffectExecutor(Protocol):
    """
    Minimal stable interface for primitive effect execution.

    The ONEX kernel depends only on this SPI for executing side effects.
    Concrete implementations live in omnibase_infra and are injected at runtime.
    Declarative effect nodes compile their operations into these primitives.

    Stability: Stable
        This protocol is part of the stable kernel contract. Breaking changes
        require major version bumps and migration guides.

    Design Principles:
        - Bytes in, bytes out: Serialization is the caller's responsibility
        - Effect IDs are typed: Use LiteralEffectId for type safety
        - Minimal interface: Only what the kernel needs
        - No handler coupling: Implementation details stay in omnibase_infra

    Example:
        ```python
        class HttpEffectExecutor:
            '''Implementation in omnibase_infra.'''

            async def execute(
                self,
                effect_id: str,
                input_data: bytes,
            ) -> bytes:
                if effect_id == "http.request":
                    request = deserialize_http_request(input_data)
                    response = await self._http_client.request(...)
                    return serialize_http_response(response)
                raise ValueError(f"Unknown effect: {effect_id}")

            def get_supported_effects(self) -> list[str]:
                return ["http.request", "http.get", "http.post", ...]
        ```

    See Also:
        - ProtocolHandler: Higher-level handler interface for complex operations
        - ProtocolEventBus: Asynchronous event-driven communication
    """

    async def execute(
        self,
        effect_id: str,
        input_data: bytes,
    ) -> bytes:
        """
        Execute a primitive effect.

        This is the core method that the ONEX kernel calls to perform
        side effects. Implementations should dispatch based on effect_id
        and handle serialization/deserialization of input/output data.

        Args:
            effect_id: Unique effect type identifier following the
                "{category}.{operation}" format (e.g., "http.request",
                "db.query"). Use LiteralEffectId values for type safety.
            input_data: Serialized input data. The serialization format
                (JSON, MessagePack, etc.) is determined by the caller
                and must be consistent within a deployment.

        Returns:
            Serialized output data in the same format as input_data.

        Raises:
            ValueError: If effect_id is not supported by this executor.
            RuntimeError: If effect execution fails.

        Note:
            Implementations should handle their own error mapping and
            ensure that infrastructure-specific exceptions are wrapped
            in appropriate error types.
        """
        ...

    def get_supported_effects(self) -> list[str]:
        """
        Return list of effect IDs supported by this executor.

        Used for runtime validation and capability discovery.
        The kernel can use this to verify that required effects
        are available before executing a workflow.

        Returns:
            List of supported effect IDs (e.g., ["http.request", "http.get"]).

        Example:
            ```python
            executor = get_effect_executor()
            if "db.query" not in executor.get_supported_effects():
                raise ConfigurationError("Database effects not available")
            ```
        """
        ...

    @property
    def executor_id(self) -> str:
        """
        Unique identifier for this executor instance.

        Used for logging, metrics, and debugging. Should be stable
        across restarts but unique per executor instance.

        Returns:
            String identifier (e.g., "http-executor-prod-1").
        """
        ...
