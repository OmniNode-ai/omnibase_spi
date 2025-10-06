"""
Protocol for Enum Generator functionality.

Defines the interface for discovering and generating enum classes
from contract definitions.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolContractDocument,
        ProtocolSchemaDefinition,
    )


@runtime_checkable
class ProtocolProtocolEnumInfo(Protocol):
    """Protocol for enum information."""

    name: str
    values: list[str]
    source_location: str


@runtime_checkable
class ProtocolEnumGenerator(Protocol):
    """Protocol for enum generation functionality.

    This protocol defines the interface for discovering enums
    from contracts and generating corresponding enum classes.
    """

    async def discover_enums_from_contract(
        self, contract_data: "ProtocolContractDocument"
    ) -> list["ProtocolProtocolEnumInfo"]:
        """Discover all enum definitions from a contract document.

        Args:
            contract_data: Contract data (ProtocolContractDocument or dict[str, Any])

        Returns:
            List of discovered enum information
        """
        ...

    async def discover_enums_from_schema(
        self,
        schema: "ProtocolSchemaDefinition" | dict[str, Any],
        path: str = "root",
    ) -> list["ProtocolProtocolEnumInfo"]:
        """Recursively discover enums from a schema definition.

        Args:
            schema: Schema to search (ProtocolSchemaDefinition or dict[str, Any])
            path: Current path in schema for tracking

        Returns:
            List of discovered enums
        """
        ...

    def generate_enum_name_from_values(self, enum_values: list[str]) -> str: ...
    def generate_enum_name_from_schema(
        self, schema: "ProtocolSchemaDefinition" | dict[str, Any]
    ) -> str:
        """Generate enum name from a schema with enum values.

        Args:
            schema: Schema containing enum values

        Returns:
            Generated enum class name
                ...
        """
        ...

    def deduplicate_enums(
        self, enum_infos: list["ProtocolProtocolEnumInfo"]
    ) -> list["ProtocolProtocolEnumInfo"]:
        """Remove duplicate enums based on their values.

        Args:
            enum_infos: List of enum information

        Returns:
            Deduplicated list[Any]of enums
        """
        ...

    def generate_enum_classes(
        self, enum_infos: list["ProtocolProtocolEnumInfo"]
    ) -> list["Any"]:
        """Generate AST enum class definitions.

        Args:
            enum_infos: List of enum information

        Returns:
            List of AST ClassDef nodes for enums
                ...
        """
        ...

    async def get_enum_member_name(self, value: str) -> str:
        """Convert enum value to valid Python enum member name.

        Args:
            value: Enum value string

        Returns:
            ...
        """
        ...

    def is_enum_schema(
        self, schema: "ProtocolSchemaDefinition" | dict[str, Any]
    ) -> bool:
        """Check if a schema defines an enum.

        Args:
            schema: Schema to check

        Returns:
            ...
        """
        ...

    async def get_enum_values(
        self, schema: "ProtocolSchemaDefinition" | dict[str, Any]
    ) -> list[str] | None:
        """Extract enum values from a schema.

        Args:
            schema: Schema to extract from

        Returns:
            ...
        """
        ...
