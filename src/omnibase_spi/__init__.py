"""
ONEX Service Provider Interface (omnibase-spi)

Pure protocol interfaces for the ONEX framework with zero implementation dependencies.
Provides protocols with Literal types for clean SPI boundaries - consumers use rich Enums
while the SPI maintains basic string literal contracts.

Key Features:
    - Zero implementation dependencies for clean architectural boundaries
    - Pure Protocol interfaces using typing.Protocol with @runtime_checkable
    - Comprehensive type safety with Literal types instead of Enums
    - Event sourcing patterns with sequence numbers and causation tracking
    - Workflow isolation using {workflowType, instanceId} pattern
    - Multi-subsystem MCP tool coordination and discovery
    - Distributed event bus with pluggable backend adapters
    - LAZY LOADING: "Protocols" loaded only when accessed for optimal performance

Usage Examples:
    # Import specific protocols from their domains (RECOMMENDED - fastest)
    from omnibase_spi.protocols.core import ProtocolLogger
    from omnibase_spi.protocols.container import ProtocolCacheService
    from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
    from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

    # Convenience imports from protocols module (all protocols)
    from omnibase_spi.protocols import (
        ProtocolLogger,
        ProtocolWorkflowEventBus,
        ProtocolMCPRegistry
    )

    # Type definitions (consolidated at types level)
    from omnibase_spi.protocols.types import (
        LogLevel,
        LiteralWorkflowState,
        MCPToolType,
        EventData
    )

    # Root-level convenience (LAZY LOADED - optimal performance)
    from omnibase_spi import (
        ProtocolLogger,              # Core logging
        ProtocolWorkflowEventBus,    # Workflow events
        ProtocolMCPRegistry,         # MCP coordination
        ProtocolEventBus,            # Event messaging
        ProtocolServiceRegistry,     # Service registry
    )

Performance Notes:
    - Root-level imports are now LAZY LOADED - protocols imported only when accessed
    - This reduces initial import time by 60-80% compared to eager loading
    - First access to each protocol may have ~1-2ms overhead
    - Subsequent accesses have no overhead (cached)
    - For maximum performance, use direct protocol imports when possible

Architecture:
    The SPI follows strict architectural purity:
    - protocols/: Pure Protocol definitions only, no implementations
    - protocols/types/: Type definitions using Literal types
    - No concrete classes, no business logic, no external dependencies
    - All protocols use @runtime_checkable for isinstance() support
    - Forward references with TYPE_CHECKING for data types
    - Zero runtime dependencies except typing-extensions and pydantic
"""

import importlib
from typing import TYPE_CHECKING, Any, cast

__version__ = "0.6.4"
__author__ = "OmniNode Team"
__email__ = "team@omninode.ai"

# Exception hierarchy - LAZY LOADED for import isolation
# Can also import from omnibase_spi.exceptions directly:
#   from omnibase_spi.exceptions import SPIError, ProtocolHandlerError, ...
# Exceptions are loaded on-demand via __getattr__ to prevent loading
# omnibase_spi.exceptions when importing from omnibase_spi.protocols.*

# Lazy loading configuration for exceptions
_LAZY_EXCEPTION_MAP = {
    "ContractCompilerError": "omnibase_spi.exceptions",
    "HandlerDiscoveryError": "omnibase_spi.exceptions",
    "HandlerInitializationError": "omnibase_spi.exceptions",
    "IdempotencyStoreError": "omnibase_spi.exceptions",
    "InvalidProtocolStateError": "omnibase_spi.exceptions",
    "ProjectionReadError": "omnibase_spi.exceptions",
    "ProjectorError": "omnibase_spi.exceptions",
    "ProtocolHandlerError": "omnibase_spi.exceptions",
    "ProtocolNotImplementedError": "omnibase_spi.exceptions",
    "RegistryError": "omnibase_spi.exceptions",
    "SPIError": "omnibase_spi.exceptions",
}

# Lazy loading configuration - defines what protocols are available at root level
# This eliminates the need to import all protocols upfront, reducing startup time
_LAZY_PROTOCOL_MAP = {
    # Core protocols - most frequently used
    "ProtocolLogger": "omnibase_spi.protocols.core.protocol_logger",
    "ProtocolCacheService": "omnibase_spi.protocols.container.protocol_cache_service",
    "ProtocolNodeRegistry": "omnibase_spi.protocols.node.protocol_node_registry",
    "ProtocolWorkflowReducer": "omnibase_spi.protocols.workflow_orchestration.protocol_workflow_reducer",
    # Event bus protocols
    "ProtocolEventBusProvider": "omnibase_spi.protocols.event_bus.protocol_event_bus",
    "ProtocolEventBusAdapter": "omnibase_spi.protocols.event_bus.protocol_event_bus",
    # Workflow orchestration protocols
    "ProtocolWorkflowEventBus": "omnibase_spi.protocols.workflow_orchestration.protocol_workflow_event_bus",
    "ProtocolWorkflowNodeRegistry": "omnibase_spi.protocols.workflow_orchestration.protocol_workflow_node_registry",
    "ProtocolEventStore": "omnibase_spi.protocols.workflow_orchestration.protocol_workflow_persistence",
    # MCP protocols
    "ProtocolMCPRegistry": "omnibase_spi.protocols.mcp.protocol_mcp_registry",
    "ProtocolMCPSubsystemClient": "omnibase_spi.protocols.mcp.protocol_mcp_subsystem_client",
    "ProtocolMCPToolProxy": "omnibase_spi.protocols.mcp.protocol_mcp_tool_proxy",
    # Container protocols
    "ProtocolServiceRegistry": "omnibase_spi.protocols.container.protocol_service_registry",
    "ProtocolArtifactContainer": "omnibase_spi.protocols.container.protocol_artifact_container",
    # Factory protocols
    "ProtocolHandlerContractFactory": "omnibase_spi.protocols.factories.protocol_handler_contract_factory",
    # Validation protocols
    "ProtocolValidator": "omnibase_spi.protocols.validation.protocol_validation",
    "ProtocolValidationResult": "omnibase_spi.protocols.validation.protocol_validation",
}

# Cache for loaded protocols to avoid repeated imports
_protocol_cache: dict[str, type] = {}

# Cache for loaded exceptions to avoid repeated imports
_exception_cache: dict[str, type] = {}


def _get_protocol_count() -> int:
    """Dynamically count available protocols to avoid documentation drift."""
    return len(_LAZY_PROTOCOL_MAP)


def _clear_protocol_cache() -> None:
    """Clear protocol cache for testing or memory management."""
    _protocol_cache.clear()


def _clear_exception_cache() -> None:
    """Clear exception cache for testing or memory management."""
    _exception_cache.clear()


def _load_exception(exception_name: str) -> type:
    """
    Lazy load an exception on first access.

    Args:
        exception_name: Name of the exception to load (e.g., 'SPIError')

    Returns:
        The loaded exception class

    Raises:
        ImportError: If exception cannot be loaded
        AttributeError: If exception doesn't exist in the module
    """
    if exception_name in _exception_cache:
        return _exception_cache[exception_name]

    if exception_name not in _LAZY_EXCEPTION_MAP:
        raise AttributeError(
            f"Exception '{exception_name}' not available at root level"
        )

    module_path = _LAZY_EXCEPTION_MAP[exception_name]

    try:
        # Import the module containing the exception using importlib
        module = importlib.import_module(module_path)

        # Get the exception class from the module
        exception_class = getattr(module, exception_name)

        # Cache for future access
        _exception_cache[exception_name] = cast(type, exception_class)

        return cast(type, exception_class)

    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to load exception {exception_name}: {e}") from e


def _load_protocol(protocol_name: str) -> type:
    """
    Lazy load a protocol on first access.

    Args:
        protocol_name: Name of the protocol to load (e.g., 'ProtocolLogger')

    Returns:
        The loaded protocol class

    Raises:
        ImportError: If protocol cannot be loaded
        AttributeError: If protocol doesn't exist in the module
    """
    if protocol_name in _protocol_cache:
        return _protocol_cache[protocol_name]

    if protocol_name not in _LAZY_PROTOCOL_MAP:
        raise AttributeError(f"Protocol '{protocol_name}' not available at root level")

    module_path = _LAZY_PROTOCOL_MAP[protocol_name]

    try:
        # Import the module containing the protocol using importlib
        module = importlib.import_module(module_path)

        # Get the protocol class from the module
        protocol_class = getattr(module, protocol_name)

        # Cache for future access
        _protocol_cache[protocol_name] = cast(type, protocol_class)

        return cast(type, protocol_class)

    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to load protocol {protocol_name}: {e}") from e


def __getattr__(name: str) -> Any:
    """
    Module-level __getattr__ for lazy loading protocols and exceptions.

    This function is called when an attribute is not found in the module's namespace.
    It enables lazy loading of protocols and exceptions, loading them only when first accessed.

    Args:
        name: Name of the attribute being accessed

    Returns:
        The lazy-loaded protocol/exception or raises AttributeError

    Raises:
        AttributeError: If the requested attribute is not a valid protocol or exception
    """
    # Check if this is a protocol that should be lazy loaded
    if name in _LAZY_PROTOCOL_MAP:
        return _load_protocol(name)

    # Check if this is an exception that should be lazy loaded
    if name in _LAZY_EXCEPTION_MAP:
        return _load_exception(name)

    # Handle special attributes that should be dynamic
    if name == "__protocol_count__":
        return _get_protocol_count()

    # Not a lazy-loadable protocol or exception
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    """
    Module-level __dir__ to support introspection and IDE completion.

    Returns all available attributes including lazy-loaded protocols.
    """
    # Get standard module attributes
    standard_attrs = ["__version__", "__author__", "__email__", "__all__"]

    # Add exceptions
    exception_attrs = [
        "ContractCompilerError",
        "HandlerDiscoveryError",
        "HandlerInitializationError",
        "IdempotencyStoreError",
        "InvalidProtocolStateError",
        "ProjectionReadError",
        "ProjectorError",
        "ProtocolHandlerError",
        "ProtocolNotImplementedError",
        "RegistryError",
        "SPIError",
    ]

    # Add lazy-loaded protocols
    protocol_attrs = list(_LAZY_PROTOCOL_MAP.keys())

    # Add special dynamic attributes
    special_attrs = ["__protocol_count__"]

    return sorted(standard_attrs + exception_attrs + protocol_attrs + special_attrs)


# Define __all__ dynamically to include all lazy-loaded protocols
__all__ = [
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    # Dynamic protocol count for documentation
    "__protocol_count__",
    # Exceptions (alphabetically ordered)
    "ContractCompilerError",
    "HandlerDiscoveryError",
    "HandlerInitializationError",
    "IdempotencyStoreError",
    "InvalidProtocolStateError",
    "ProjectionReadError",
    "ProjectorError",
    "ProtocolHandlerError",
    "ProtocolNotImplementedError",
    "RegistryError",
    "SPIError",
    # All lazy-loaded protocols (dynamically generated)
    *sorted(_LAZY_PROTOCOL_MAP.keys()),
]

# Performance monitoring for development
if TYPE_CHECKING:
    # During type checking or testing, provide the actual imports
    # This ensures type checkers and tests work correctly while maintaining lazy loading at runtime

    from omnibase_spi.protocols.container import (
        ProtocolArtifactContainer as ProtocolArtifactContainer,
        ProtocolCacheService as ProtocolCacheService,
        ProtocolServiceRegistry as ProtocolServiceRegistry,
    )
    from omnibase_spi.protocols.core import ProtocolLogger as ProtocolLogger
    from omnibase_spi.protocols.event_bus import (
        ProtocolEventBusProvider as ProtocolEventBusProvider,
    )
    from omnibase_spi.protocols.factories import (
        ProtocolHandlerContractFactory as ProtocolHandlerContractFactory,
    )
    from omnibase_spi.protocols.mcp import (
        ProtocolMCPRegistry as ProtocolMCPRegistry,
        ProtocolMCPSubsystemClient as ProtocolMCPSubsystemClient,
        ProtocolMCPToolProxy as ProtocolMCPToolProxy,
    )
    from omnibase_spi.protocols.node import ProtocolNodeRegistry as ProtocolNodeRegistry
    from omnibase_spi.protocols.validation import (
        ProtocolValidationResult as ProtocolValidationResult,
        ProtocolValidator as ProtocolValidator,
    )
    from omnibase_spi.protocols.workflow_orchestration import (
        ProtocolEventStore as ProtocolEventStore,
        ProtocolWorkflowEventBus as ProtocolWorkflowEventBus,
        ProtocolWorkflowNodeRegistry as ProtocolWorkflowNodeRegistry,
        ProtocolWorkflowReducer as ProtocolWorkflowReducer,
    )
