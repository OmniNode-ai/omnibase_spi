"""
Protocol for Reference Resolver functionality.

Defines the interface for resolving $ref references in JSON Schema
to Python type names for code generation.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolReferenceResolver(Protocol):
    """
    Protocol for JSON Schema reference resolution in code generation.

    Defines the interface for resolving $ref references in JSON Schema
    documents to Python type names, handling internal references, external file
    references, and subcontract references following ONEX contract patterns.

    This protocol enables consistent reference resolution across code generators,
    validators, and schema processors while maintaining proper type safety and
    namespace conventions.

    Example:
        ```python
        resolver: "ProtocolReferenceResolver" = create_reference_resolver()

        # Internal reference
        internal_type = await resolver.resolve_ref("#/definitions/UserProfile")
        # Returns: "UserProfile"

        # External reference
        external_type = await resolver.resolve_ref("schemas/user.yaml#/definitions/User")
        # Returns: "User" (with appropriate module prefix)

        # Subcontract reference
        subcontract_type = await resolver.resolve_ref("contracts/validation.yaml#/ValidationRules")
        # Returns: "SubcontractValidationRules"

        # Check reference type
        if resolver.is_internal_ref("#/definitions/Address"):
            # Handle internal reference
            type_name = resolver.extract_definition_name("#/definitions/Address")
        elif resolver.is_subcontract_ref("contracts/auth.yaml#/Token"):
            # Handle subcontract reference
            type_name = await resolver.resolve_subcontract_ref("contracts/auth.yaml#/Token")
        ```

    Key Features:
        - Internal reference resolution (#/definitions/...)
        - External file reference resolution (file.yaml#/definitions/...)
        - Subcontract reference handling with naming conventions
        - Reference type detection and classification
        - Component extraction for complex references
        - Namespace-aware type name generation

    Reference Formats:
        - Internal: "#/definitions/TypeName" -> "TypeName"
        - External: "schemas/file.yaml#/definitions/TypeName" -> "TypeName"
        - Subcontract: "contracts/file.yaml#/TypeName" -> "SubcontractTypeName"

    See Also:
        - ProtocolRegistryResolver: Registry-based resolution patterns
        - ProtocolConfigurationManager: Configuration-driven reference handling
    """

    async def resolve_ref(self, ref: str) -> str: ...
    async def resolve_internal_ref(self, ref: str) -> str:
        """Resolve internal reference (#/definitions/...).

        Args:
            ref: Internal reference string

        Returns:
            Resolved type name
        """
        ...

    async def resolve_external_ref(self, ref: str) -> str:
        """Resolve external reference (file.yaml#/definitions/...).

        Args:
            ref: External reference string

        Returns:
            Resolved type name
        """
        ...

    async def resolve_subcontract_ref(self, ref: str) -> str:
        """Resolve subcontract reference (contracts/file.yaml#/...).

        Args:
            ref: Subcontract reference string

        Returns:
            Resolved type name with subcontract prefix
        """
        ...

    def extract_definition_name(self, ref: str) -> str:
        """Extract the definition name from a reference.

        Args:
            ref: Reference string

        Returns:
            Definition name extracted from reference
        """
        ...

    def is_internal_ref(self, ref: str) -> bool:
        """Check if reference is internal.

        Args:
            ref: Reference to check

        Returns:
            True if internal reference
        """
        ...

    def is_subcontract_ref(self, ref: str) -> bool:
        """Check if reference is to a subcontract.

        Args:
            ref: Reference to check

        Returns:
            True if subcontract reference
        """
        ...

    async def get_ref_parts(self, ref: str) -> dict[str, str | None]:
        """Parse reference into component parts.

        Args:
            ref: Reference to parse

        Returns:
            Dict with 'file', 'path', and 'name' components
        """
        ...
