"""
Protocol for Contract Analyzer functionality.

Defines the interface for analyzing, validating, and processing
contract documents for code generation.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolSchemaDefinition,
    )


@runtime_checkable
class ProtocolContractInfo(Protocol):
    """Protocol for contract information."""

    node_name: str
    node_version: str
    has_input_state: bool
    has_output_state: bool
    has_definitions: bool
    definition_count: int
    field_count: int
    reference_count: int
    enum_count: int


@runtime_checkable
class ProtocolReferenceInfo(Protocol):
    """Protocol for reference information."""

    ref_string: str
    ref_type: str  # "internal", "external", "subcontract"
    resolved_type: str
    source_location: str
    target_file: str | None


@runtime_checkable
class ProtocolContractValidationResult(Protocol):
    """Protocol for contract validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]


@runtime_checkable
class ProtocolContractModelSchema(Protocol):
    """Protocol for contract schema models."""

    type: str
    properties: dict[str, Any]
    required: list[str]
    additional_properties: bool

    async def validate(self, data: dict[str, Any]) -> bool: ...

    async def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolModelContractDocument(Protocol):
    """Protocol for contract document models."""

    node_name: str
    node_version: str
    node_type: str
    description: str
    input_state: dict[str, Any] | None
    output_state: dict[str, Any] | None
    definitions: dict[str, Any]

    async def validate(self) -> bool: ...

    async def get_schema(
        self, schema_name: str
    ) -> "ProtocolContractModelSchema | None": ...

    async def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolContractAnalyzer(Protocol):
    """Protocol for contract analysis functionality.

    This protocol defines the interface for loading, validating,
    and analyzing contract documents for code generation.
    """

    async def load_contract(
        self, contract_path: str
    ) -> "ProtocolModelContractDocument":
        """Load and parse a contract.yaml file into a validated model.

        Args:
            contract_path: Path to contract.yaml file

        Returns:
            Validated ProtocolModelContractDocument

        Raises:
            Exception: If contract cannot be loaded or validated
        """
        ...

    async def validate_contract(
        self, contract_path: str
    ) -> "ProtocolContractValidationResult":
        """Validate a contract for correctness and completeness.

        Args:
            contract_path: Path to contract.yaml file

        Returns:
            ContractValidationResult with validation details
        """
        ...

    async def analyze_contract(self, contract_path: str) -> "ProtocolContractInfo":
        """Analyze contract structure and gather statistics.

        Args:
            contract_path: Path to contract.yaml file

        Returns:
            ContractInfo with analysis results
        """
        ...

    async def discover_all_references(
        self,
        contract: "ProtocolModelContractDocument",
    ) -> list["ProtocolReferenceInfo"]:
        """Discover all $ref references in a contract.

        Args:
            contract: Contract document to analyze

        Returns:
            List of discovered references with metadata
        """
        ...

    async def get_external_dependencies(
        self, contract: "ProtocolModelContractDocument"
    ) -> set[str]:
        """Get all external file dependencies of a contract.

        Args:
            contract: Contract document to analyze

        Returns:
            Set of external file paths referenced
        """
        ...

    async def get_dependency_graph(self, contract_path: str) -> dict[str, set[str]]: ...

    def check_circular_references(
        self,
        contract: "ProtocolModelContractDocument",
    ) -> list[list[str]]:
        """Check for circular references in the contract.

        Args:
            contract: Contract to check

        Returns:
            List of circular reference paths found
        """
        ...

    def count_fields_in_schema(self, schema: "ProtocolContractModelSchema") -> int:
        """Count total fields in a schema including nested objects.

        Args:
            schema: Schema to count fields in

        Returns:
            Total field count
        """
        ...

    def validate_schema(
        self,
        schema: "ProtocolContractModelSchema",
        location: str,
    ) -> dict[str, list[str]]:
        """Validate a schema object and return issues.

        Args:
            schema: Schema to validate
            location: Location path for error messages

        Returns:
            Dict with 'errors', 'warnings', and 'info' lists
        """
        ...
