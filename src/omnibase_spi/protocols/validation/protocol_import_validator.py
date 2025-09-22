"""
Protocol interface for import validation in ONEX ecosystem.

This protocol defines the interface for validating import statements and
dependencies across ONEX repositories, providing standardized validation
capabilities for NodeImportValidatorCompute implementations.
"""

from typing import Any, Dict, List, Optional, Protocol, Tuple

from .protocol_validation import ProtocolValidationResult


class ProtocolImportValidationConfig(Protocol):
    """Protocol for import validation configuration."""

    allowed_imports: set[str]
    allowed_import_items: set[str]
    repository_type: str
    validation_mode: str  # "strict", "permissive", "security"

    def is_import_allowed(self, import_path: str) -> bool:
        """Check if an import path is allowed."""
        ...

    def is_import_item_allowed(self, import_item: str) -> bool:
        """Check if an import item is allowed."""
        ...


class ProtocolImportAnalysis(Protocol):
    """Protocol for import analysis results."""

    import_path: str
    import_items: List[str]
    is_valid: bool
    security_risk: str  # "none", "low", "medium", "high", "critical"
    dependency_level: int
    analysis_details: Dict[str, Any]

    def get_risk_summary(self) -> str:
        """Get summary of security risk assessment."""
        ...

    def get_recommendations(self) -> List[str]:
        """Get optimization/security recommendations."""
        ...


class ProtocolImportValidator(Protocol):
    """
    Protocol interface for import validation in ONEX systems.

    This protocol defines the interface for NodeImportValidatorCompute nodes
    that validate import statements, dependencies, and security implications
    across ONEX repositories.
    """

    validation_config: ProtocolImportValidationConfig
    security_scanning_enabled: bool
    dependency_analysis_enabled: bool

    def validate_import(
        self,
        import_path: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProtocolValidationResult:
        """
        Validate a single import statement.

        Args:
            import_path: The import path to validate
            description: Human-readable description for reporting
            context: Additional context for validation

        Returns:
            ProtocolValidationResult with validation outcome
        """
        ...

    def validate_from_import(
        self,
        from_path: str,
        import_items: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProtocolValidationResult:
        """
        Validate a from...import statement.

        Args:
            from_path: The module path being imported from
            import_items: Comma-separated list of items being imported
            description: Human-readable description for reporting
            context: Additional context for validation

        Returns:
            ProtocolValidationResult with validation outcome
        """
        ...

    def validate_import_security(
        self, import_path: str, context: Optional[Dict[str, Any]] = None
    ) -> ProtocolImportAnalysis:
        """
        Perform security analysis of an import.

        Args:
            import_path: The import path to analyze
            context: Additional context for security analysis

        Returns:
            ProtocolImportAnalysis with security assessment
        """
        ...

    def validate_dependency_chain(
        self, import_path: str, max_depth: int = 3
    ) -> List[ProtocolImportAnalysis]:
        """
        Analyze dependency chain for an import.

        Args:
            import_path: The root import path to analyze
            max_depth: Maximum depth for dependency analysis

        Returns:
            List of ProtocolImportAnalysis for the dependency chain
        """
        ...

    def validate_repository_imports(
        self, repository_path: str, patterns: Optional[List[str]] = None
    ) -> List[ProtocolValidationResult]:
        """
        Validate all imports in a repository.

        Args:
            repository_path: Path to repository to validate
            patterns: File patterns to include (default: ["*.py"])

        Returns:
            List of ProtocolValidationResult for all discovered imports
        """
        ...

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive validation summary.

        Returns:
            Dictionary containing validation statistics, recommendations,
            and security findings
        """
        ...

    def configure_validation(self, config: ProtocolImportValidationConfig) -> None:
        """
        Configure validation parameters.

        Args:
            config: Import validation configuration
        """
        ...

    def reset_validation_state(self) -> None:
        """Reset internal validation state for fresh validation cycle."""
        ...
