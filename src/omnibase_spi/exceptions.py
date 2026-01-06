"""
SPI Exception Hierarchy for omnibase_spi v0.3.0.

This module defines the base exception types for all SPI-related errors.
These are abstract error types that implementations should use or subclass.
"""

from __future__ import annotations

from copy import deepcopy
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
        self.context: dict[str, Any] = deepcopy(context) if context is not None else {}


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


class HandlerDiscoveryError(ProtocolHandlerError):
    """
    Raised when handler discovery fails.

    Indicates that a handler source could not discover or load handlers
    due to configuration errors, missing dependencies, invalid manifests,
    or other issues during the discovery process.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing discovery failure details.

    Example:
        raise HandlerDiscoveryError(
            f"Failed to discover handlers from source: {source_type}"
        )

    Example with context:
        raise HandlerDiscoveryError(
            "Handler discovery failed",
            context={
                "source_type": "CONTRACT",
                "search_paths": ["/etc/handlers/", "/opt/handlers/"],
                "handler_type": "http",
                "error": str(e)
            }
        )

    Related:
        - ProtocolHandlerSource.discover_handlers(): Method that raises this exception
        - HandlerInitializationError: For errors during handler initialization (after discovery)
    """

    pass


class IdempotencyStoreError(SPIError):
    """
    Errors raised by ProtocolIdempotencyStore implementations.

    Raised when idempotency store operations fail due to connection
    issues, constraint violations, or other storage errors.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing idempotency store operation details.

    Example:
        raise IdempotencyStoreError(
            f"Failed to record event: {event_id}"
        )

    Example with context:
        raise IdempotencyStoreError(
            "Failed to record event",
            context={
                "event_id": event_id,
                "idempotency_key": key,
                "operation": "record",
                "store_type": "redis"
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


class ProjectorError(SPIError):
    """
    Errors raised by ProtocolProjector implementations.

    Raised when projector operations fail due to connection issues,
    storage errors, or other persistence layer problems. Note that
    stale update rejections are NOT errors - they return a rejected
    status in the PersistResult.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing projector operation details.

    Example:
        raise ProjectorError(
            f"Failed to persist projection for entity: {entity_id}"
        )

    Example with context:
        raise ProjectorError(
            "Failed to persist projection",
            context={
                "entity_id": entity_id,
                "domain": "orders",
                "sequence": 42,
                "operation": "persist",
                "store_type": "postgres"
            }
        )

    Related:
        - OMN-940: Define ProtocolProjector in omnibase_spi
        - IdempotencyStoreError: For runtime-level deduplication errors
    """

    pass


class ProjectionReadError(SPIError):
    """
    Errors raised when reading projection state fails.

    Raised when projection reader operations fail due to connection issues,
    timeout, or other infrastructure errors during read operations.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing read operation details.

    Example:
        raise ProjectionReadError(
            f"Failed to query projection for entity: {entity_id}"
        )

    Example with context:
        raise ProjectionReadError(
            "Failed to query projection",
            context={
                "entity_id": entity_id,
                "domain": "orders",
                "operation": "get_entity_state"
            }
        )

    Related:
        - OMN-930: Define ProtocolProjectionReader in omnibase_spi
        - ProjectorError: For projection write/persistence errors
    """

    pass


class SchemaError(SPIError):
    """
    Errors raised during database schema operations.

    Raised when schema creation, validation, or migration fails. This
    includes table creation, index management, and schema compatibility
    checks during projector initialization.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing schema operation details.

    Example:
        raise SchemaError(
            f"Failed to create table: {table_name}"
        )

    Example with context:
        raise SchemaError(
            "Schema creation failed",
            context={
                "table_name": "order_projections",
                "operation": "create_table",
                "database": "postgres",
                "error": str(e),
                "contract_path": "/app/contracts/orders.yaml"
            }
        )

    Common Causes:
        - Database connection failure during schema creation
        - Insufficient permissions to create tables/indexes
        - Schema incompatibility (existing table doesn't match contract)
        - Invalid column type specifications in contract

    Related:
        - OMN-1167: Define ProtocolProjectorLoader in omnibase_spi
        - ContractCompilerError: For contract parsing/validation errors
        - ProjectorError: For runtime projection persistence errors
    """

    pass


class TemplateError(SPIError):
    """
    Base exception for template loading and processing errors.

    This is the parent class for all template-related errors in the factory
    system. Template errors occur during loading, parsing, or validation of
    YAML template files used for handler contract generation.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing template operation details.

    Example:
        raise TemplateError(
            "Template operation failed",
            context={
                "template_name": "default_compute_handler.yaml",
                "operation": "load"
            }
        )

    Related:
        - TemplateNotFoundError: For missing template files
        - TemplateParseError: For YAML syntax errors
        - HandlerContractFactory: Factory that uses templates
    """

    pass


class TemplateNotFoundError(TemplateError):
    """
    Raised when a template file cannot be found.

    This exception indicates that the requested template file does not exist
    in the expected location (omnibase_spi/contracts/defaults/). This typically
    occurs when an unsupported handler type is requested or when template files
    are missing from the package installation.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing template search details.

    Example:
        raise TemplateNotFoundError(
            f"Template not found: {template_name}"
        )

    Example with context:
        raise TemplateNotFoundError(
            "Template file not found",
            context={
                "template_name": "default_compute_handler.yaml",
                "search_paths": ["/path/to/templates/"],
                "handler_type": "COMPUTE"
            }
        )

    Related:
        - TemplateError: Parent exception class
        - HandlerContractFactory: Factory that loads templates
    """

    pass


class TemplateParseError(TemplateError):
    """
    Raised when a template file contains invalid YAML.

    This exception indicates that while the template file exists, its contents
    cannot be parsed as valid YAML. This typically indicates a syntax error
    in the template file or corrupted file contents.

    Args:
        message: The error message describing what went wrong.
        context: Optional dictionary containing parse error details.

    Example:
        raise TemplateParseError(
            f"Invalid YAML in template: {template_name}"
        )

    Example with context:
        raise TemplateParseError(
            "Failed to parse template YAML",
            context={
                "template_name": "default_effect_handler.yaml",
                "error_line": 42,
                "yaml_error": str(e),
                "handler_type": "EFFECT"
            }
        )

    Related:
        - TemplateError: Parent exception class
        - TemplateNotFoundError: For missing template files
        - HandlerContractFactory: Factory that parses templates
    """

    pass
