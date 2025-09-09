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

Usage Examples:
    # Import specific protocols from their domains
    from omnibase_spi.protocols.core import ProtocolLogger, ProtocolCacheService
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
        WorkflowState, 
        MCPToolType,
        EventData
    )
    
    # Root-level convenience for most common protocols
    from omnibase_spi import (
        ProtocolLogger,              # Core logging
        ProtocolWorkflowEventBus,    # Workflow events
        ProtocolMCPRegistry,         # MCP coordination
        ProtocolEventBus,            # Event messaging
        ProtocolServiceRegistry,     # Service registry
    )

Architecture:
    The SPI follows strict architectural purity:
    - protocols/: Pure Protocol definitions only, no implementations
    - protocols/types/: Type definitions using Literal types
    - No concrete classes, no business logic, no external dependencies
    - All protocols use @runtime_checkable for isinstance() support
    - Forward references with TYPE_CHECKING for data types
    - Zero runtime dependencies except typing-extensions and pydantic
"""

__version__ = "0.1.0"
__author__ = "OmniNode Team"
__email__ = "team@omninode.ai"

# Export most commonly used protocols at root level for convenience
# while maintaining backward compatibility with verbose imports

# Key container protocols
from omnibase_spi.protocols.container import (
    ProtocolArtifactContainer,  # Artifact management
)
from omnibase_spi.protocols.container import (
    ProtocolServiceRegistry,  # Service discovery and DI
)

# Most frequently used core protocols
from omnibase_spi.protocols.core import ProtocolCacheService  # Caching abstractions
from omnibase_spi.protocols.core import ProtocolLogger  # Structured logging
from omnibase_spi.protocols.core import (
    ProtocolNodeRegistry,  # Node discovery and management
)
from omnibase_spi.protocols.core import ProtocolWorkflowReducer  # FSM state reduction

# Essential event bus protocols
from omnibase_spi.protocols.event_bus import ProtocolEventBus  # Core event messaging
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusAdapter,  # Backend adapter interface
)

# Core MCP coordination protocols
from omnibase_spi.protocols.mcp import (
    ProtocolMCPRegistry,  # Multi-subsystem tool registry
)
from omnibase_spi.protocols.mcp import (
    ProtocolMCPSubsystemClient,  # Subsystem integration client
)
from omnibase_spi.protocols.mcp import ProtocolMCPToolProxy  # Tool execution proxy

# Common validation protocols
from omnibase_spi.protocols.validation import (
    ProtocolValidationResult,  # Validation result contracts
)
from omnibase_spi.protocols.validation import (
    ProtocolValidator,  # General validation interface
)

# Primary workflow orchestration protocols
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolEventStore,  # Event sourcing persistence
)
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolWorkflowEventBus,  # Event-driven workflow coordination
)
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolWorkflowNodeRegistry,  # Workflow node management
)

__all__ = [
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    # Root-level convenience exports (most commonly used protocols)
    # Core protocols
    "ProtocolNodeRegistry",
    "ProtocolWorkflowReducer",
    "ProtocolCacheService",
    "ProtocolLogger",
    # Workflow orchestration protocols
    "ProtocolWorkflowEventBus",
    "ProtocolWorkflowNodeRegistry",
    "ProtocolEventStore",
    # MCP protocols
    "ProtocolMCPRegistry",
    "ProtocolMCPSubsystemClient",
    "ProtocolMCPToolProxy",
    # Event bus protocols
    "ProtocolEventBus",
    "ProtocolEventBusAdapter",
    # Container protocols
    "ProtocolServiceRegistry",
    "ProtocolArtifactContainer",
    # Validation protocols
    "ProtocolValidator",
    "ProtocolValidationResult",
]
