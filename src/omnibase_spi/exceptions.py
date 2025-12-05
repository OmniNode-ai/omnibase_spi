"""
SPI Exception Hierarchy for omnibase_spi v0.3.0.

This module defines the base exception types for all SPI-related errors.
These are abstract error types that implementations should use or subclass.
"""

from __future__ import annotations

from typing import Any


class SPIError(Exception):
    """
    Base exception for all SPI-related errors.

    All SPI exceptions inherit from this base class to enable
    broad exception handling when needed.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing additional debugging information
            such as node_id, protocol_type, operation, parameters, etc.

    Attributes:
        context: Dictionary containing exception context for debugging.
            Empty dict if no context was provided.

    Example:
        try:
            handler.execute(request, config)
        except SPIError as e:
            # Handle any SPI-related error
            logger.error(f"SPI error: {e}")
            if e.context:
                logger.debug(f"Context: {e.context}")

    Example with context:
        raise SPIError(
            "Handler execution failed",
            context={
                "handler_id": "http_handler_123",
                "protocol_type": "http",
                "operation": "execute",
                "request_id": "req-456"
            }
        )
    """

    def __init__(
        self, message: str = "", context: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize SPIError with message and optional context.

        Args:
            message: The error message.
            context: Optional dictionary of debugging context.
        """
        super().__init__(message)
        self.context: dict[str, Any] = context if context is not None else {}


class ProtocolHandlerError(SPIError):
    """
    Errors raised by ProtocolHandler implementations.

    Raised when a protocol handler encounters an error during
    execution of protocol-specific operations.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing handler-specific debugging info.

    Example:
        raise ProtocolHandlerError(
            f"HTTP request failed: {response.status_code}"
        )

    Example with context:
        raise ProtocolHandlerError(
            "HTTP request failed",
            context={
                "status_code": response.status_code,
                "url": request.url,
                "method": "POST",
                "handler_id": self.handler_id
            }
        )
    """

    pass


class HandlerInitializationError(ProtocolHandlerError):
    """
    Raised when a handler fails to initialize.

    Indicates that the handler could not establish connections,
    configure clients, or otherwise prepare for operation.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing initialization failure details.

    Example:
        raise HandlerInitializationError(
            f"Failed to connect to database: {connection_string}"
        )

    Example with context:
        raise HandlerInitializationError(
            "Failed to connect to database",
            context={
                "connection_string": connection_string,
                "timeout": 30,
                "retry_count": 3,
                "handler_id": self.handler_id
            }
        )
    """

    pass


class ContractCompilerError(SPIError):
    """
    Errors raised during contract compilation or validation.

    Raised when YAML contract files cannot be parsed, validated,
    or compiled into runtime contract objects.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing contract compilation details.

    Example:
        raise ContractCompilerError(
            f"Invalid contract at {path}: missing required field 'protocol'"
        )

    Example with context:
        raise ContractCompilerError(
            "Invalid contract: missing required field 'protocol'",
            context={
                "path": path,
                "line_number": 42,
                "missing_fields": ["protocol", "version"],
                "contract_type": "effect"
            }
        )
    """

    pass


class RegistryError(SPIError):
    """
    Errors raised by handler registry operations.

    Raised when registration fails or when looking up
    unregistered protocol types.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing registry operation details.

    Example:
        raise RegistryError(
            f"Protocol type '{protocol_type}' is not registered"
        )

    Example with context:
        raise RegistryError(
            f"Protocol type '{protocol_type}' is not registered",
            context={
                "protocol_type": protocol_type,
                "available_types": list(registry.keys()),
                "operation": "lookup",
                "registry_id": self.registry_id
            }
        )
    """

    pass


class ProtocolNotImplementedError(SPIError):
    """
    Raised when a required protocol implementation is missing.

    This exception signals that Core or Infra has not provided an
    implementation for a protocol that SPI defines. Use this to
    cleanly signal missing implementations during DI resolution.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing protocol implementation details.

    Example:
        raise ProtocolNotImplementedError(
            f"No implementation registered for {IEffectNode.__name__}"
        )

    Example with context:
        raise ProtocolNotImplementedError(
            "No implementation registered for protocol",
            context={
                "protocol_name": IEffectNode.__name__,
                "required_by": "WorkflowOrchestrator",
                "available_implementations": list(container.registry.keys()),
                "di_container_id": container.id
            }
        )

    Common Use Cases:
        - DI container cannot resolve a protocol to an implementation
        - Required handler type is not registered
        - Node type has no registered implementation
    """

    pass


class InvalidProtocolStateError(SPIError):
    """
    Raised when a protocol method is called in an invalid lifecycle state.

    This exception is used to enforce proper lifecycle management.
    For example, calling execute() before initialize() on an IEffectNode.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing state violation details.

    Example:
        raise InvalidProtocolStateError(
            f"Cannot call execute() before initialize() on {self.node_id}"
        )

    Example with context:
        raise InvalidProtocolStateError(
            "Cannot call execute() before initialize()",
            context={
                "node_id": self.node_id,
                "current_state": "uninitialized",
                "required_state": "initialized",
                "operation": "execute",
                "lifecycle_history": ["created", "configured"]
            }
        )

    Common Violations:
        - Calling execute() before initialize()
        - Calling execute() after shutdown()
        - Calling shutdown() before initialize()
        - Calling methods on a disposed/closed node
        - Using a handler after connection timeout
    """

    pass
