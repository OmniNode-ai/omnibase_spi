"""
Container Protocols - SPI Interface Exports.

Artifact container and utility protocols.
Note: Core dependency injection protocols are now in omnibase_core.
"""

from .protocol_artifact_container import (
    LiteralContainerArtifactType,
    LiteralOnexStatus,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
)
from .protocol_cache_service import ProtocolCacheService
from .protocol_client_config import ProtocolClientConfigProvider
from .protocol_schema_exclusion_registry import ProtocolSchemaExclusionRegistry
from .protocol_testable_registry import ProtocolTestableRegistry

__all__ = [
    "LiteralContainerArtifactType",
    "LiteralOnexStatus",
    "ProtocolArtifactContainer",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactInfo",
    "ProtocolArtifactMetadata",
    "ProtocolCacheService",
    "ProtocolClientConfigProvider",
    "ProtocolSchemaExclusionRegistry",
    "ProtocolTestableRegistry",
]
