"""
Core Protocol Interfaces

System-level contracts for serialization, schema loading, workflow processing,
logging, node registry, and other core functionality supporting the ONEX 
Messaging Design v0.3.
"""

from omnibase_spi.protocols.core.protocol_cache_service import (
    ProtocolCacheService,
    ProtocolCacheServiceProvider,
)
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger
from omnibase_spi.protocols.core.protocol_node_configuration import (
    ProtocolConfigurationError,
    ProtocolNodeConfiguration,
    ProtocolNodeConfigurationProvider,
)
from omnibase_spi.protocols.core.protocol_node_configuration_utils import (
    ProtocolUtilsNodeConfiguration,
)
from omnibase_spi.protocols.core.protocol_node_registry import (
    ProtocolNodeInfo,
    ProtocolNodeRegistry,
)
from omnibase_spi.protocols.core.protocol_workflow_reducer import (
    ProtocolWorkflowReducer,
)

__all__ = [
    # Advanced workflow protocols
    "ProtocolWorkflowReducer",
    # Node discovery and registry
    "ProtocolNodeInfo",
    "ProtocolNodeRegistry",
    # Configuration protocols
    "ProtocolNodeConfiguration",
    "ProtocolNodeConfigurationProvider",
    "ProtocolUtilsNodeConfiguration",
    "ProtocolConfigurationError",
    # Cache service protocols
    "ProtocolCacheService",
    "ProtocolCacheServiceProvider",
    # Logging protocols
    "ProtocolLogger",
]
