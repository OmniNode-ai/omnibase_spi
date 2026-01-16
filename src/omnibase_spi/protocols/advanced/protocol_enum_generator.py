"""
Protocol for Enum Generator functionality.

Defines the interface for discovering and generating enum classes
from contract definitions.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolContractDocument,
        ProtocolSchemaDefinition,
    )


@runtime_checkable
class ProtocolEnumInfo(Protocol):
    """
    Protocol for enum discovery and metadata information.

    Captures information about discovered enum definitions within
    contract schemas, including the generated name, enumeration values,
    and source location for code generation and deduplication.

    Attributes:
        name: Generated or explicit enum class name
        values: List of string values in the enumeration
        source_location: Path within contract where enum was discovered

    Example:
        ```python
        generator: ProtocolEnumGenerator = get_enum_generator()
        contract = await load_contract("path/to/contract.yaml")
        enum_infos = await generator.discover_enums_from_contract(contract)

        for info in enum_infos:
            print(f"Enum: {info.name}")
            print(f"  Values: {info.values}")
            print(f"  Found at: {info.source_location}")
        ```

    See Also:
        - ProtocolEnumGenerator: Enum discovery and generation
        - ProtocolContractDocument: Source contract structure
    """

    name: str
    values: list[str]
    source_location: str


@runtime_checkable
class ProtocolEnumGenerator(Protocol):
    """Protocol for automated enum discovery and generation from contract definitions.

    Defines the contract for discovering enum definitions within contract documents,
    schemas, and nested type definitions, then generating corresponding Python enum
    classes with proper naming conventions. Enables intelligent enum extraction
    during code generation workflows with deduplication and validation support.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolEnumGenerator
        from omnibase_spi.protocols.types import ProtocolContractDocument

        async def generate_enums_from_contract(
            generator: ProtocolEnumGenerator,
            contract: ProtocolContractDocument
        ) -> list[object]:
            # Discover all enum definitions in contract
            enum_infos = await generator.discover_enums_from_contract(contract)

            print(f"Found {len(enum_infos)} enum definitions")
            for enum_info in enum_infos:
                print(f"  - {enum_info.name}: {len(enum_info.values)} values")

            # Deduplicate enums with identical values
            unique_enums = generator.deduplicate_enums(enum_infos)
            print(f"After deduplication: {len(unique_enums)} unique enums")

            # Generate AST enum class definitions
            enum_classes = generator.generate_enum_classes(unique_enums)

            return enum_classes  # Returns list of AST ClassDef nodes
        ```

    Key Features:
        - Recursive enum discovery from contracts and schemas
        - Intelligent enum name generation from values
        - Duplicate enum detection and deduplication
        - Schema validation for enum definitions
        - Python identifier conversion for enum members
        - AST generation for enum classes

    See Also:
        - ProtocolASTBuilder: AST construction for generated enums
        - ProtocolContractAnalyzer: Contract document analysis
        - ProtocolSchemaDefinition: Schema type definitions
    """

    async def discover_enums_from_contract(
        self, contract_data: "ProtocolContractDocument"
    ) -> list["ProtocolEnumInfo"]:
        """Discover all enum definitions from a contract document.

        Args:
            contract_data: Contract data (ProtocolContractDocument or JsonType dict)

        Returns:
            List of discovered enum information
        """
        ...

    async def discover_enums_from_schema(
        self,
        schema: "ProtocolSchemaDefinition | JsonType",
        path: str | None = None,
    ) -> list["ProtocolEnumInfo"]:
        """Recursively discover enums from a schema definition.

        Args:
            schema: Schema to search (ProtocolSchemaDefinition or JsonType dict)
            path: Current path in schema for tracking

        Returns:
            List of discovered enums
        """
        ...

    def generate_enum_name_from_values(self, enum_values: list[str]) -> str: ...
    def generate_enum_name_from_schema(
        self, schema: "ProtocolSchemaDefinition | JsonType"
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
        self, enum_infos: list["ProtocolEnumInfo"]
    ) -> list["ProtocolEnumInfo"]:
        """Remove duplicate enums based on their values.

        Args:
            enum_infos: List of enum information

        Returns:
            Deduplicated list of enums
        """
        ...

    def generate_enum_classes(
        self, enum_infos: list["ProtocolEnumInfo"]
    ) -> list[object]:
        """Generate AST enum class definitions.

        Args:
            enum_infos: List of enum information

        Returns:
            List of AST ClassDef nodes for enums
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

    def is_enum_schema(self, schema: "ProtocolSchemaDefinition | JsonType") -> bool:
        """Check if a schema defines an enum.

        Args:
            schema: Schema to check

        Returns:
            ...
        """
        ...

    async def get_enum_values(
        self, schema: "ProtocolSchemaDefinition | JsonType"
    ) -> list[str] | None:
        """Extract enum values from a schema.

        Args:
            schema: Schema to extract from

        Returns:
            ...
        """
        ...
