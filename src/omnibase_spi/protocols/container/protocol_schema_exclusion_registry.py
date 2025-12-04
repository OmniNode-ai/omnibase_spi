"""
Protocol for schema exclusion registry functionality.

Defines the interface for managing schema exclusion patterns across
the ONEX ecosystem. This protocol enables consistent handling of
excluded schemas while maintaining proper architectural boundaries.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolSchemaExclusionRegistry(Protocol):
    """
    Protocol for managing schema file exclusion patterns across ONEX ecosystem.

    Provides a canonical interface for schema exclusion registries that determine
    which files should be excluded from schema processing, validation, or code
    generation. This protocol ensures consistent schema filtering across all nodes
    and processing pipelines.

    Placed in container/ per ONEX architecture guidelines for shared execution-layer
    components reused by multiple nodes. All schema exclusion logic must conform
    to this interface for proper integration with the ONEX toolchain.

    Example:
        ```python
        exclusion_registry: "ProtocolSchemaExclusionRegistry" = get_exclusion_registry()

        # Check if file should be excluded
        if exclusion_registry.is_schema_file("schemas/internal/_private.yaml"):
            # Skip processing this schema file
            pass
        else:
            # Process the schema file normally
            process_schema_file("schemas/internal/_private.yaml")

        # Example patterns that might be excluded:
        # - Internal schemas: "schemas/internal/*"
        # - Test schemas: "schemas/test/*"
        # - Template schemas: "schemas/templates/*"
        # - Work-in-progress: "schemas/wip/*"
        ```

    Key Features:
        - Pattern-based file exclusion for schema processing
        - Consistent exclusion logic across all ONEX nodes
        - Support for wildcard patterns and path matching
        - Integration with code generation pipelines
        - Prevents processing of internal/private schemas
        - Optimization of schema validation workflows

    Common Exclusion Patterns:
        - Internal schemas: Files in internal directories
        - Test fixtures: Schema files used only for testing
        - Templates: Schema templates not meant for direct use
        - Work-in-progress: Schemas under active development
        - Generated files: Auto-generated schema files
        - Documentation schemas: Examples and samples

    Use Cases:
        - Code generation: Exclude non-public schemas from codegen
        - Validation: Skip internal schemas during validation
        - Discovery: Filter schemas in auto-discovery processes
        - Publishing: Exclude private schemas from public APIs
        - Testing: Separate test fixtures from production schemas

    See Also:
        - ProtocolRegistry: General registry operations
        - ProtocolArtifactContainer: Artifact discovery and filtering
        - ProtocolConfigurationManager: Exclusion pattern configuration
    """

    def is_schema_file(self, path: str) -> bool:
        """Return True if the given path is a schema file to be excluded, else False."""
        ...
