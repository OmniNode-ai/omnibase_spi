"""
Protocol interface for import validation in ONEX ecosystem.

This protocol defines the interface for validating import statements and
dependencies across ONEX repositories, providing standardized validation
capabilities for NodeImportValidatorCompute implementations.
"""

from typing import Any, Protocol, runtime_checkable

from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)


@runtime_checkable
class ProtocolImportValidationConfig(Protocol):
    """Protocol for import validation configuration."""

    allowed_imports: set[str]
    allowed_import_items: set[str]
    repository_type: str
    validation_mode: str

    async def is_import_allowed(self, import_path: str) -> bool: ...

    async def is_import_item_allowed(self, import_item: str) -> bool: ...


@runtime_checkable
class ProtocolImportAnalysis(Protocol):
    """Protocol for import analysis results."""

    import_path: str
    import_items: list[str]
    is_valid: bool
    security_risk: str
    dependency_level: int
    analysis_details: dict[str, Any]

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
        self, import_path: str, description: str, context: dict[str, Any] | None = None
    ) -> ProtocolValidationResult: ...

    async def validate_from_import(
        self,
        from_path: str,
        import_items: str,
        description: str,
        context: dict[str, Any] | None = None,
    ) -> ProtocolValidationResult: ...

    async def validate_import_security(
        self, import_path: str, context: dict[str, Any] | None = None
    ) -> ProtocolImportAnalysis: ...

    async def validate_dependency_chain(
        self, import_path: str, max_depth: int = 3
    ) -> list[ProtocolImportAnalysis]: ...

    async def validate_repository_imports(
        self, repository_path: str, patterns: list[str] | None = None
    ) -> list[ProtocolValidationResult]: ...

    async def get_validation_summary(self) -> dict[str, Any]: ...

    async def configure_validation(
        self, config: "ProtocolImportValidationConfig"
    ) -> None: ...

    async def reset_validation_state(self) -> None: ...
