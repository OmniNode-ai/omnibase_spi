# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.142263'
# description: Stamped by ToolPython
# entrypoint: python://protocol_schema_loader
# hash: 54d22bb99ec2490ef26d82ee55400b98fa3774a1cf59e9e600ee05023501e133
# last_modified_at: '2025-05-29T14:14:00.338636+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_schema_loader.py
# namespace: python://omnibase.protocol.protocol_schema_loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 5563978b-75f9-4c23-bca7-70ba09837d66
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
ProtocolSchemaLoader: Protocol for all ONEX schema loader implementations.
Defines the canonical loader interface for node metadata and JSON schema files.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolNodeMetadataBlock


@runtime_checkable
class ProtocolSchemaModel(Protocol):
    """
    Protocol for loaded schema model representation.

    Represents a fully loaded and parsed JSON Schema with validation
    capabilities, serialization support, and path tracking for
    schema-driven operations.

    Attributes:
        schema_id: Unique identifier for the schema
        schema_type: Classification of schema (json-schema, yaml, etc.)
        version: Schema version string
        definition: Raw schema definition dictionary

    Example:
        ```python
        loader: ProtocolSchemaLoader = get_schema_loader()
        schema = await loader.load_json_schema("/schemas/input.json")

        print(f"Schema: {schema.schema_id} v{schema.version}")
        print(f"Type: {schema.schema_type}")

        # Validate data against schema
        is_valid = schema.validate({"field": "value"})

        # Get schema path
        path = await schema.get_schema_path()

        # Serialize schema
        schema_dict = schema.to_dict()
        ```

    See Also:
        - ProtocolSchemaLoader: Schema loading interface
        - ProtocolNodeMetadataBlock: Node metadata with schema
    """

    schema_id: str
    schema_type: str
    version: str
    definition: dict[str, object]

    def validate(self, data: dict[str, object]) -> bool: ...

    def to_dict(self) -> dict[str, object]: ...

    async def get_schema_path(self) -> str: ...


@runtime_checkable
class ProtocolSchemaLoader(Protocol):
    """
    Protocol for ONEX schema loaders.
    All methods use str objects and return strongly-typed models as appropriate.
    """

    async def load_onex_yaml(self, path: str) -> ProtocolNodeMetadataBlock: ...

    async def load_json_schema(self, path: str) -> ProtocolSchemaModel: ...

    async def load_schema_for_node(
        self, node: ProtocolNodeMetadataBlock
    ) -> ProtocolSchemaModel: ...
