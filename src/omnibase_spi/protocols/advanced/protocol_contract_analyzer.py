"""
Protocol for Contract Analyzer functionality.

Defines the interface for analyzing, validating, and processing
contract documents for code generation.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolContractInfo(Protocol):
    """Protocol for contract information and metadata.

    Provides detailed information about a contract document including
    structural metadata, versioning, and statistical data about
    its contents (fields, definitions, references, enums).

    Attributes:
        node_name: The name of the contract node
        node_version: The semantic version of the contract
        has_input_state: Whether the contract defines an input state schema
        has_output_state: Whether the contract defines an output state schema
        has_definitions: Whether the contract contains schema definitions
        definition_count: Number of schema definitions in the contract
        field_count: Total number of fields across all schemas
        reference_count: Number of $ref references in the contract
        enum_count: Number of enum definitions in the contract

    Example:
        ```python
        analyzer: ProtocolContractAnalyzer = get_contract_analyzer()
        contract_info = await analyzer.analyze_contract("path/to/contract.yaml")

        assert isinstance(contract_info, ProtocolContractInfo)
        print(f"Contract {contract_info.node_name} v{contract_info.node_version}")
        print(f"  Fields: {contract_info.field_count}")
        print(f"  References: {contract_info.reference_count}")
        ```

    See Also:
        - ProtocolContractAnalyzer: Main analyzer protocol
    """

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
    """
    Protocol for reference information in contract document analysis.

    Captures detailed metadata about $ref references discovered within
    contract documents, enabling dependency tracking, circular reference
    detection, and external file resolution for code generation workflows.

    Attributes:
        ref_string: The raw $ref string as found in the contract
        ref_type: Reference classification (internal, external, subcontract)
        resolved_type: The Python type name after reference resolution
        source_location: Path to where the reference was discovered
        target_file: External file path if reference points outside contract

    Example:
        ```python
        analyzer: ProtocolContractAnalyzer = get_contract_analyzer()
        contract = await analyzer.load_contract("path/to/contract.yaml")
        references = await analyzer.discover_all_references(contract)

        for ref in references:
            if ref.ref_type == "external":
                print(f"External ref: {ref.ref_string} -> {ref.target_file}")
            elif ref.ref_type == "internal":
                print(f"Internal ref: {ref.ref_string} resolves to {ref.resolved_type}")
        ```

    See Also:
        - ProtocolContractAnalyzer: Main analyzer protocol
        - ProtocolModelContractDocument: Contract document structure
    """

    ref_string: str
    ref_type: str  # "internal", "external", "subcontract"
    resolved_type: str
    source_location: str
    target_file: str | None


@runtime_checkable
class ProtocolContractValidationResult(Protocol):
    """
    Protocol for contract validation result reporting.

    Provides structured validation outcome including validity status,
    categorized messages (errors, warnings, informational), and enables
    progressive validation workflows with detailed issue tracking.

    Attributes:
        is_valid: Whether the contract passed validation
        errors: Critical issues preventing valid contract status
        warnings: Non-critical issues that should be addressed
        info: Informational messages about contract analysis

    Example:
        ```python
        analyzer: ProtocolContractAnalyzer = get_contract_analyzer()
        result = await analyzer.validate_contract("path/to/contract.yaml")

        if not result.is_valid:
            print("Contract validation failed:")
            for error in result.errors:
                print(f"  ERROR: {error}")
            for warning in result.warnings:
                print(f"  WARNING: {warning}")
        else:
            print(f"Contract valid with {len(result.info)} notes")
        ```

    See Also:
        - ProtocolContractAnalyzer.validate_contract: Validation method
        - ProtocolContractInfo: Contract statistics after validation
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]


@runtime_checkable
class ProtocolContractModelSchema(Protocol):
    """
    Protocol for contract schema model representation.

    Defines the structure of JSON Schema-compliant schema definitions
    found within ONEX contracts, providing validation and serialization
    capabilities for schema-driven code generation and data validation.

    Attributes:
        type: JSON Schema type (object, array, string, etc.)
        properties: Dictionary of property definitions
        required: List of required property names
        additional_properties: Whether additional properties are allowed

    Example:
        ```python
        document: ProtocolModelContractDocument = await analyzer.load_contract(path)
        schema = await document.get_schema("InputState")

        if schema is not None:
            print(f"Schema type: {schema.type}")
            print(f"Required fields: {schema.required}")

            # Validate data against schema
            is_valid = await schema.validate({"field1": "value"})
            if is_valid:
                schema_dict = await schema.to_dict()
        ```

    See Also:
        - ProtocolModelContractDocument: Container for schemas
        - ProtocolContractAnalyzer: Schema analysis methods
    """

    type: str
    properties: "JsonType"
    required: list[str]
    additional_properties: bool

    async def validate(self, data: "JsonType") -> bool:
        """Validate data against this schema.

        Checks that the provided data conforms to this schema's type,
        properties, and required field constraints.

        Args:
            data: JSON-compatible data to validate against the schema.

        Returns:
            True if the data is valid according to this schema, False otherwise.

        Raises:
            May raise implementation-specific exceptions for validation errors.
        """
        ...

    async def to_dict(self) -> "JsonType":
        """Convert the schema to a dictionary representation.

        Serializes the schema definition including type, properties,
        required fields, and additional properties settings.

        Returns:
            JSON-compatible dictionary containing the complete schema definition.

        Raises:
            May raise implementation-specific exceptions for serialization errors.
        """
        ...


@runtime_checkable
class ProtocolModelContractDocument(Protocol):
    """
    Protocol for ONEX contract document representation.

    Represents a fully parsed and validated contract.yaml document with
    access to node metadata, input/output state schemas, type definitions,
    and validation capabilities for code generation workflows.

    Attributes:
        node_name: Unique identifier for the node this contract defines
        node_version: Semantic version of the contract specification
        node_type: ONEX node type (compute, effect, orchestrator, reducer)
        description: Human-readable description of the node purpose
        input_state: JSON Schema for node input data structure
        output_state: JSON Schema for node output data structure
        definitions: Shared schema definitions used via $ref

    Example:
        ```python
        analyzer: ProtocolContractAnalyzer = get_contract_analyzer()
        contract = await analyzer.load_contract("node_processor/contract.yaml")

        print(f"Node: {contract.node_name} v{contract.node_version}")
        print(f"Type: {contract.node_type}")
        print(f"Description: {contract.description}")

        # Get input schema
        if contract.input_state:
            input_schema = await contract.get_schema("InputState")
            if input_schema and await input_schema.validate(data):
                print("Input data valid")

        # Serialize contract
        contract_dict = await contract.to_dict()
        ```

    See Also:
        - ProtocolContractAnalyzer: Contract loading and analysis
        - ProtocolContractModelSchema: Schema representation
        - ProtocolReferenceInfo: Reference tracking
    """

    node_name: str
    node_version: str
    node_type: str
    description: str
    input_state: "JsonType | None"
    output_state: "JsonType | None"
    definitions: "JsonType"

    async def validate(self) -> bool:
        """Validate the contract document structure.

        Checks that the contract has valid metadata, properly formed
        schemas, and internally consistent references.

        Returns:
            True if the contract is valid, False otherwise.

        Raises:
            May raise implementation-specific exceptions for validation errors.
        """
        ...

    async def get_schema(
        self, schema_name: str
    ) -> "ProtocolContractModelSchema | None":
        """Retrieve a named schema from this contract document.

        Looks up a schema definition by name from the contract's
        input/output states or shared definitions.

        Args:
            schema_name: Name of the schema to retrieve (e.g., 'InputState').

        Returns:
            The schema if found, None if no schema with that name exists.

        Raises:
            May raise implementation-specific exceptions for schema retrieval errors.
        """
        ...

    async def to_dict(self) -> "JsonType":
        """Convert the contract document to a dictionary representation.

        Serializes the complete contract including node metadata, schemas,
        and definitions for persistence or transmission.

        Returns:
            JSON-compatible dictionary containing the full contract specification.

        Raises:
            May raise implementation-specific exceptions for serialization errors.
        """
        ...


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
            contract_path: Path to contract.yaml file.

        Returns:
            ContractValidationResult with validation details.

        Raises:
            FileNotFoundError: If contract file cannot be found.
            ValueError: If contract contains invalid YAML or schema.
        """
        ...

    async def analyze_contract(self, contract_path: str) -> "ProtocolContractInfo":
        """Analyze contract structure and gather statistics.

        Args:
            contract_path: Path to contract.yaml file.

        Returns:
            ContractInfo with analysis results.

        Raises:
            FileNotFoundError: If contract file cannot be found.
            ValueError: If contract contains invalid YAML or schema.
        """
        ...

    async def discover_all_references(
        self,
        contract: "ProtocolModelContractDocument",
    ) -> list["ProtocolReferenceInfo"]:
        """Discover all $ref references in a contract.

        Args:
            contract: Contract document to analyze.

        Returns:
            List of discovered references with metadata.

        Raises:
            ValueError: If contract contains malformed references.
        """
        ...

    async def get_external_dependencies(
        self, contract: "ProtocolModelContractDocument"
    ) -> set[str]:
        """Get all external file dependencies of a contract.

        Args:
            contract: Contract document to analyze.

        Returns:
            Set of external file paths referenced.

        Raises:
            ValueError: If contract contains malformed external references.
        """
        ...

    async def get_dependency_graph(self, contract_path: str) -> dict[str, set[str]]:
        """Build a dependency graph for a contract and its references.

        Constructs a directed graph representing all dependencies between
        contracts, including transitive dependencies from external files.

        Args:
            contract_path: Path to the root contract.yaml file

        Returns:
            Dictionary mapping contract paths to sets of their dependencies

        Raises:
            FileNotFoundError: If contract file cannot be found
            ValueError: If contract contains invalid references
        """
        ...

    def check_circular_references(
        self,
        contract: "ProtocolModelContractDocument",
    ) -> list[list[str]]:
        """Check for circular references in the contract.

        Args:
            contract: Contract to check.

        Returns:
            List of circular reference paths found.

        Raises:
            ValueError: If contract contains malformed references.
        """
        ...

    def count_fields_in_schema(self, schema: "ProtocolContractModelSchema") -> int:
        """Count total fields in a schema including nested objects.

        Args:
            schema: Schema to count fields in.

        Returns:
            Total field count.

        Raises:
            ValueError: If schema structure is invalid or malformed.
        """
        ...

    def validate_schema(
        self,
        schema: "ProtocolContractModelSchema",
        location: str,
    ) -> dict[str, list[str]]:
        """Validate a schema object and return issues.

        Args:
            schema: Schema to validate.
            location: Location path for error messages.

        Returns:
            Dict with 'errors', 'warnings', and 'info' lists.

        Raises:
            ValueError: If schema structure is fundamentally invalid.
        """
        ...
