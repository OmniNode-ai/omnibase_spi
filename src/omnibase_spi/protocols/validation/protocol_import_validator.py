"""
Protocol interface for import validation in ONEX ecosystem.

This protocol defines the interface for validating import statements and
dependencies across ONEX repositories, providing standardized validation
capabilities for NodeImportValidatorCompute implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )


@runtime_checkable
class ProtocolImportValidationConfig(Protocol):
    """
    Protocol for import validation configuration.

    Defines allowed imports and import items for a specific repository
    type, enabling architecture-aware import validation with flexible
    allow/deny configuration.

    Attributes:
        allowed_imports: Set of allowed module import paths
        allowed_import_items: Set of allowed specific import items
        repository_type: Repository type (core, spi, infra, app)
        validation_mode: Validation strictness (strict, permissive)

    Example:
        ```python
        config = ProtocolImportValidationConfig(
            allowed_imports={"typing", "collections.abc"},
            allowed_import_items={"Protocol", "runtime_checkable"},
            repository_type="spi",
            validation_mode="strict"
        )

        is_ok = await config.is_import_allowed("omnibase_core.models")
        is_ok = await config.is_import_item_allowed("BaseModel")
        ```

    See Also:
        - ProtocolImportValidator: Uses this configuration
        - ProtocolImportAnalysis: Validation results
    """

    allowed_imports: set[str]
    allowed_import_items: set[str]
    repository_type: str
    validation_mode: str

    async def is_import_allowed(self, import_path: str) -> bool: ...

    async def is_import_item_allowed(self, import_item: str) -> bool: ...


@runtime_checkable
class ProtocolImportAnalysis(Protocol):
    """
    Protocol for import statement analysis results.

    Captures comprehensive analysis of an import statement including
    validity, security assessment, dependency depth, and detailed
    analysis information for import validation reporting.

    Attributes:
        import_path: The analyzed import path
        import_items: List of specific items imported
        is_valid: Whether the import is valid per configuration
        security_risk: Security risk level (none, low, medium, high)
        dependency_level: Depth in dependency graph (0=direct)
        analysis_details: Additional analysis details

    Example:
        ```python
        validator: ProtocolImportValidator = get_import_validator()
        analysis = await validator.validate_import_security("subprocess")

        print(f"Import: {analysis.import_path}")
        print(f"Valid: {analysis.is_valid}")
        print(f"Security risk: {analysis.security_risk}")
        print(f"Dependency level: {analysis.dependency_level}")

        risk = await analysis.get_risk_summary()
        recommendations = await analysis.get_recommendations()
        ```

    See Also:
        - ProtocolImportValidator: Analysis source
        - ProtocolImportValidationConfig: Validation rules
    """

    import_path: str
    import_items: list[str]
    is_valid: bool
    security_risk: str
    dependency_level: int
    analysis_details: "JsonType"

    async def get_risk_summary(self) -> str: ...

    async def get_recommendations(self) -> list[str]: ...


@runtime_checkable
class ProtocolImportValidator(Protocol):
    """
    Protocol interface for import validation in ONEX systems.

    This protocol defines the interface for NodeImportValidatorCompute nodes
    that validate import statements, dependencies, and security implications
    across ONEX repositories.
    """

    validation_config: "ProtocolImportValidationConfig"
    security_scanning_enabled: bool
    dependency_analysis_enabled: bool

    async def validate_import(
        self, import_path: str, description: str, context: "JsonType | None" = None
    ) -> "ProtocolValidationResult": ...

    async def validate_from_import(
        self,
        from_path: str,
        import_items: str,
        description: str,
        context: "JsonType | None" = None,
    ) -> "ProtocolValidationResult": ...

    async def validate_import_security(
        self, import_path: str, context: "JsonType | None" = None
    ) -> ProtocolImportAnalysis: ...

    async def validate_dependency_chain(
        self, import_path: str, max_depth: int | None = None
    ) -> list[ProtocolImportAnalysis]: ...

    async def validate_repository_imports(
        self, repository_path: str, patterns: list[str] | None = None
    ) -> list["ProtocolValidationResult"]: ...

    async def get_validation_summary(self) -> "JsonType": ...

    async def configure_validation(
        self, config: "ProtocolImportValidationConfig"
    ) -> None: ...

    async def reset_validation_state(self) -> None: ...
