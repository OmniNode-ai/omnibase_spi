# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""PrimitiveEffectExecutor SPI protocol for the ONEX kernel.

This module defines the stable, typed interface that the L1 kernel uses to
invoke side-effectful HTTP and Kafka operations without importing any L2 node
library or handler implementation code.

Stability: Stable
    This protocol is part of the stable kernel SPI contract. Breaking changes
    require a major version bump and a migration guide.

Architecture Context:
    The L1 kernel must not import HandlerHttp or HandlerKafka directly from
    L2 libraries — doing so creates a circular dependency risk and couples
    kernel evolution to handler implementation details.

    ProtocolPrimitiveEffectExecutorV2 is the architectural anchor that breaks
    this coupling:

    * The kernel depends only on omnibase_spi (zero upstream runtime deps).
    * Concrete handlers in omnibase_infra implement the protocol via structural
      subtyping — no explicit ``implements`` declaration is needed.
    * Future handler-as-nodes decomposition can introduce new implementations
      without touching the kernel.

    Monolithic handlers (HandlerHttp, HandlerKafka) are PRESERVED for MVP.
    This protocol does NOT refactor them.

Naming:
    ``ProtocolPrimitiveEffectExecutorV2`` is the typed successor to
    ``ProtocolPrimitiveEffectExecutor`` (the legacy bytes-in/bytes-out
    variant in omnibase_spi.protocols.effects). The V2 suffix is used to
    avoid a name collision within the SPI namespace.

See Also:
    - ProtocolPrimitiveEffectExecutor: legacy bytes-in/bytes-out variant
      (omnibase_spi.protocols.effects.protocol_primitive_effect_executor)
    - Phase 2: HandlerResourceManager stub in omnibase_infra (internal issue)
    - Phase 3: handler-as-nodes decomposition (omnibase_infra)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# HTTP contract types
# ---------------------------------------------------------------------------


@runtime_checkable
class ProtocolHttpRequestContract(Protocol):
    """Minimal HTTP request contract for kernel-level dispatch.

    Implementations must provide these attributes. No omnibase_core or
    omnibase_infra imports are permitted in this module — the contract
    is expressed entirely via typing.Protocol structural subtyping.

    Attributes:
        method: HTTP method string (e.g. "GET", "POST").
        url: Full target URL string.
        headers: Optional mapping of header name to header value.
        body: Optional raw request body bytes.
        timeout_seconds: Optional per-request timeout override in seconds.
    """

    @property
    def method(self) -> str:
        """HTTP method string (e.g. ``"GET"``, ``"POST"``, ``"PUT"``)."""
        ...

    @property
    def url(self) -> str:
        """Fully-qualified target URL including scheme, host, and path."""
        ...

    @property
    def headers(self) -> dict[str, str] | None:
        """Optional HTTP request headers as a flat string-to-string mapping."""
        ...

    @property
    def body(self) -> bytes | None:
        """Optional serialized request body."""
        ...

    @property
    def timeout_seconds(self) -> float | None:
        """Optional per-request timeout override in seconds.

        When ``None`` the executor uses its own default timeout.
        """
        ...


@runtime_checkable
class ProtocolHttpResponseContract(Protocol):
    """Minimal HTTP response contract returned by the kernel-level executor.

    Attributes:
        status_code: HTTP status code (e.g. 200, 404, 500).
        headers: Response headers as a flat string-to-string mapping.
        body: Raw response body bytes.
    """

    @property
    def status_code(self) -> int:
        """HTTP response status code."""
        ...

    @property
    def headers(self) -> dict[str, str]:
        """HTTP response headers as a flat string-to-string mapping."""
        ...

    @property
    def body(self) -> bytes:
        """Raw response body bytes."""
        ...


# ---------------------------------------------------------------------------
# ProtocolPrimitiveEffectExecutorV2
# ---------------------------------------------------------------------------


@runtime_checkable
class ProtocolPrimitiveEffectExecutorV2(Protocol):
    """Typed kernel-level interface for primitive HTTP and Kafka side effects.

    This is the V2 typed successor to ``ProtocolPrimitiveEffectExecutor``
    (the legacy bytes-in/bytes-out variant). The V2 suffix distinguishes
    the typed interface from the existing legacy protocol in the SPI
    namespace.

    The ONEX kernel depends only on this SPI for executing the two primary
    transport-level effects: outbound HTTP requests and Kafka message
    production. Concrete implementations live in omnibase_infra and are
    injected at runtime.

    Design Principles:
        - Typed contracts: request/response types are expressed as Protocols,
          not raw bytes, so callers benefit from static type checking.
        - Zero upstream deps: this module imports only from the Python
          standard library (``typing``). No omnibase_core, omnibase_infra,
          or any node library may be imported at module scope.
        - Structural subtyping: ``HandlerHttp`` and ``HandlerKafka`` satisfy
          this protocol via duck typing — no explicit inheritance needed.
        - Minimal surface: only the two methods the kernel actually needs.

    Example — conforming implementation (lives in omnibase_infra)::

        class HttpKafkaEffectExecutor:
            async def execute_http(
                self,
                request: ProtocolHttpRequestContract,
            ) -> ProtocolHttpResponseContract:
                response = await self._http_client.request(
                    method=request.method,
                    url=request.url,
                    headers=request.headers,
                    content=request.body,
                    timeout=request.timeout_seconds,
                )
                return _adapt_response(response)

            async def execute_kafka_produce(
                self,
                topic: str,
                payload: bytes,
                headers: dict[str, str] | None = None,
            ) -> None:
                await self._producer.send(topic, value=payload, headers=headers)

    See Also:
        - ProtocolHttpRequestContract: typed HTTP request contract (this module)
        - ProtocolHttpResponseContract: typed HTTP response contract (this module)
        - ProtocolPrimitiveEffectExecutor: legacy bytes-in/bytes-out variant
    """

    async def execute_http(
        self,
        request: ProtocolHttpRequestContract,
    ) -> ProtocolHttpResponseContract:
        """Execute an outbound HTTP request.

        The kernel calls this method when a node needs to perform an HTTP
        side effect. The executor is responsible for managing connection
        pooling, timeouts, retries, and error mapping.

        Args:
            request: Typed HTTP request contract carrying method, URL,
                optional headers, optional body, and optional timeout.

        Returns:
            Typed HTTP response carrying status code, headers, and body
            bytes. The caller is responsible for deserialising the body.

        Raises:
            RuntimeError: If the request fails due to a network error,
                timeout, or other infrastructure issue. Implementations
                must wrap transport-specific exceptions in RuntimeError
                so the kernel is not coupled to any specific HTTP library.
        """
        ...

    async def execute_kafka_produce(
        self,
        topic: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Produce a message onto a Kafka topic.

        The kernel calls this method when a node needs to publish an event
        to the event bus. The executor handles broker connection management,
        serialisation framing, and delivery guarantees.

        Args:
            topic: Target Kafka topic name. Must be a non-empty string that
                matches an existing topic on the configured broker.
            payload: Serialised message payload bytes. Serialisation format
                (JSON, MessagePack, Avro, etc.) is the caller's responsibility.
            headers: Optional Kafka message headers as a flat string-to-string
                mapping. Passed through to the broker without modification.
                ``None`` is treated as an empty header set.

        Raises:
            RuntimeError: If message production fails due to a broker error,
                timeout, or serialisation issue. Implementations must wrap
                transport-specific exceptions so the kernel is not coupled
                to any specific Kafka client library.
        """
        ...


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    "ProtocolHttpRequestContract",
    "ProtocolHttpResponseContract",
    "ProtocolPrimitiveEffectExecutorV2",
]
