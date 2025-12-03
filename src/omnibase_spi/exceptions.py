"""
SPI Exception Hierarchy for omnibase_spi v0.3.0.

This module defines the base exception types for all SPI-related errors.
These are abstract error types that implementations should use or subclass.
"""
from __future__ import annotations


class SPIError(Exception):
    """
    Base exception for all SPI-related errors.

    All SPI exceptions inherit from this base class to enable
    broad exception handling when needed.

    Example:
        try:
            handler.execute(request, config)
        except SPIError as e:
            # Handle any SPI-related error
            logger.error(f"SPI error: {e}")
    """

    pass


class ProtocolHandlerError(SPIError):
    """
    Errors raised by ProtocolHandler implementations.

    Raised when a protocol handler encounters an error during
    execution of protocol-specific operations.

    Example:
        raise ProtocolHandlerError(
            f"HTTP request failed: {response.status_code}"
        )
    """

    pass


class HandlerInitializationError(ProtocolHandlerError):
    """
    Raised when a handler fails to initialize.

    Indicates that the handler could not establish connections,
    configure clients, or otherwise prepare for operation.

    Example:
        raise HandlerInitializationError(
            f"Failed to connect to database: {connection_string}"
        )
    """

    pass


class ContractCompilerError(SPIError):
    """
    Errors raised during contract compilation or validation.

    Raised when YAML contract files cannot be parsed, validated,
    or compiled into runtime contract objects.

    Example:
        raise ContractCompilerError(
            f"Invalid contract at {path}: missing required field 'protocol'"
        )
    """

    pass


class RegistryError(SPIError):
    """
    Errors raised by handler registry operations.

    Raised when registration fails or when looking up
    unregistered protocol types.

    Example:
        raise RegistryError(
            f"Protocol type '{protocol_type}' is not registered"
        )
    """

    pass


class ProtocolNotImplementedError(SPIError):
    """
    Raised when a required protocol implementation is missing.

    This exception signals that Core or Infra has not provided an
    implementation for a protocol that SPI defines. Use this to
    cleanly signal missing implementations during DI resolution.

    Example:
        raise ProtocolNotImplementedError(
            f"No implementation registered for {IEffectNode.__name__}"
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

    Example:
        raise InvalidProtocolStateError(
            f"Cannot call execute() before initialize() on {self.node_id}"
        )

    Common Violations:
        - Calling execute() before initialize()
        - Calling execute() after shutdown()
        - Calling shutdown() before initialize()
        - Calling methods on a disposed/closed node
        - Using a handler after connection timeout
    """

    pass
