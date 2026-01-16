"""ProtocolSchemaLoader: Protocol for all ONEX schema loader implementations.

Defines the canonical loader interface for node metadata and JSON schema files.
"""

from __future__ import annotations

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

    def validate(self, data: dict[str, object]) -> bool:
        """Validate data against this schema.

        Args:
            data: Dictionary of data to validate against the schema.

        Returns:
            True if data conforms to the schema, False otherwise.
        """
        ...

    def to_dict(self) -> dict[str, object]:
        """Serialize the schema model to a dictionary.

        Returns:
            Dictionary representation of the schema including id, type,
            version, and definition.
        """
        ...

    async def get_schema_path(self) -> str:
        """Get the filesystem path where this schema was loaded from.

        Returns:
            Absolute path to the schema file.
        """
        ...


@runtime_checkable
class ProtocolSchemaLoader(Protocol):
    """
    Protocol for ONEX schema loaders.
    All methods use str objects and return strongly-typed models as appropriate.
    """

    async def load_onex_yaml(self, path: str) -> ProtocolNodeMetadataBlock:
        """Load and parse an ONEX YAML metadata file.

        Args:
            path: Filesystem path to the .onex.yaml file.

        Returns:
            Parsed node metadata block with all ONEX properties.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            ValueError: If the YAML content is malformed or invalid.
        """
        ...

    async def load_json_schema(self, path: str) -> ProtocolSchemaModel:
        """Load and parse a JSON Schema file.

        Args:
            path: Filesystem path to the JSON schema file.

        Returns:
            Loaded schema model with validation capabilities.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            ValueError: If the JSON schema is malformed or invalid.
        """
        ...

    async def load_schema_for_node(
        self, node: ProtocolNodeMetadataBlock
    ) -> ProtocolSchemaModel:
        """Load the JSON schema associated with a node's metadata.

        Args:
            node: Node metadata block containing schema reference.

        Returns:
            Loaded schema model for the node's input/output validation.

        Raises:
            FileNotFoundError: If the referenced schema does not exist.
            ValueError: If the node has no schema reference or schema is invalid.
        """
        ...
