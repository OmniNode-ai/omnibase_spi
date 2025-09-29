"""
ProtocolSchemaLoader: "Protocol" for all ONEX schema loader implementations.
Defines the canonical loader interface for node metadata and JSON schema files.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolNodeMetadataBlock,
    ProtocolSchemaObject,
)


@runtime_checkable
class ProtocolSchemaLoader(Protocol):
    """
    Protocol for ONEX schema loaders.
    All methods use path strings and return strongly-typed models as appropriate.
    """

    async def load_onex_yaml(self, path: str) -> "ProtocolNodeMetadataBlock": ...

    async def load_json_schema(self, path: str) -> ProtocolSchemaObject: ...

    async def load_schema_for_node(
        self, node: "ProtocolNodeMetadataBlock"
    ) -> ProtocolSchemaObject: ...
