"""Protocol interface for contract compliance validation tools in ONEX ecosystem.

This module defines the interface that contract compliance validation tools must implement.
It provides type-safe contracts for SPI purity validation, namespace isolation checking,
and compliance verification across ONEX service components.

The protocol ensures that SPI packages maintain proper isolation from implementation
packages, follow protocol definition patterns, and adhere to ONEX compliance rules.

Key Validation Rules:
    - SPI012: Namespace isolation between SPI and implementation packages
    - SPI007: Concrete class violation detection (no implementations in SPI)
    - SPI003: @runtime_checkable decorator validation
    - Protocol purity compliance (proper typing, no business logic)

Example:
    ```python
    from omnibase_spi.protocols.validation import ProtocolContractCompliance

    # Get validator from dependency injection
    validator: ProtocolContractCompliance = get_compliance_validator()

    # Validate SPI purity
    results = await validator.validate_compliance(
        targets=["src/omnibase_spi/protocols/"],
        rules=["SPI012", "SPI007", "SPI003"],
        context={"strict_mode": True}
    )

    # Check compliance status
    if validator.is_compliant(results):
        print("SPI purity validation passed")
    else:
        violations = await validator.get_violations(results)
        report = validator.generate_compliance_report(results, output_format="markdown")
        print(report)
    ```

Integration Patterns:
    - Works with ONEX validation framework
    - Integrates with quality assurance pipelines
    - Supports CI/CD validation workflows
    - Provides detailed violation reporting

See Also:
    - ProtocolValidationResult: Result type for validation operations.
    - omnibase_core.validation: Core validation utilities.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue, ProtocolValidationResult


@runtime_checkable
class ProtocolContractCompliance(Protocol):
    """
    Protocol interface for contract compliance validation operations.

    Defines the contract for SPI purity validation tools that ensure:
    - Namespace isolation between SPI and implementation packages
    - Protocol purity compliance (no concrete classes, proper typing)
    - Zero implementation dependencies in SPI packages
    - Proper protocol definition patterns

    Key Features:
        - SPI012 namespace isolation validation
        - SPI007 concrete class violation detection
        - SPI003 runtime_checkable decorator validation
        - Comprehensive compliance reporting
        - Type-safe validation contracts

    Usage Example:
        ```python
        validator: ProtocolContractCompliance = SomeValidator()

        # Validate SPI purity
        results = validator.validate_compliance(
            targets=[protocol_file],
            rules=["SPI012", "SPI007", "SPI003"]
        )

        # Check compliance status
        if validator.is_compliant(results):
            print("SPI purity validation passed")
        else:
            violations = validator.get_violations(results)
            handle_violations(violations)
        ```

    Integration Patterns:
        - Works with ONEX validation framework
        - Integrates with quality assurance pipelines
        - Supports CI/CD validation workflows
        - Provides detailed violation reporting
    """

    async def validate_compliance(
        self,
        targets: list[str],
        rules: list[str],
        context: dict[str, "ContextValue"] | None = None,
    ) -> list["ProtocolValidationResult"]:
        """Validate targets against specified compliance rules.

        Analyzes the specified targets (files, directories, or patterns) against
        the provided compliance rules and returns validation results.

        Args:
            targets: List of file paths, directory paths, or glob patterns to validate.
            rules: List of rule identifiers to apply (e.g., ["SPI012", "SPI007"]).
            context: Optional context values for validation configuration.

        Returns:
            List of validation results, one per target/rule combination.

        Raises:
            SPIError: If validation cannot be performed due to internal error.
            InvalidProtocolStateError: If validator is not properly configured.

        Example:
            ```python
            results = await validator.validate_compliance(
                targets=["src/omnibase_spi/"],
                rules=["SPI012", "SPI007", "SPI003"],
                context={"strict_mode": True}
            )
            ```
        """
        ...

    def is_compliant(self, results: list["ProtocolValidationResult"]) -> bool:
        """Check if all validation results indicate compliance.

        Args:
            results: List of validation results to check.

        Returns:
            True if all results pass, False if any violations exist.

        Raises:
            SPIError: If compliance check cannot be performed.

        Example:
            ```python
            if validator.is_compliant(results):
                print("All checks passed")
            ```
        """
        ...

    async def get_violations(
        self, results: list["ProtocolValidationResult"]
    ) -> list["ProtocolValidationResult"]:
        """Filter results to return only violations.

        Args:
            results: List of validation results to filter.

        Returns:
            List of validation results that represent violations.

        Raises:
            SPIError: If violation filtering cannot be performed.

        Example:
            ```python
            violations = await validator.get_violations(results)
            for v in violations:
                print(f"Violation: {v.rule} - {v.message}")
            ```
        """
        ...

    def generate_compliance_report(
        self, results: list["ProtocolValidationResult"], output_format: str = "text"
    ) -> str:
        """Generate a formatted compliance report.

        Creates a human-readable report summarizing validation results,
        including pass/fail counts, violation details, and recommendations.

        Args:
            results: List of validation results to include in report.
            output_format: Output format ("text", "markdown", "json"). Defaults to "text".

        Returns:
            Formatted report string.

        Raises:
            SPIError: If report generation fails.
            InvalidProtocolStateError: If output_format is not a supported format.

        Example:
            ```python
            report = validator.generate_compliance_report(results, output_format="markdown")
            print(report)
            ```
        """
        ...

    def configure_validation(self, configuration: dict[str, "ContextValue"]) -> bool:
        """Configure validation behavior.

        Updates validator configuration with provided settings.

        Args:
            configuration: Dictionary of configuration options including:
                - strict_mode: Enable strict validation
                - exclude_patterns: Patterns to exclude from validation
                - custom_rules: Additional custom rules to apply

        Returns:
            True if configuration was applied successfully.

        Raises:
            SPIError: If configuration cannot be applied.
            InvalidProtocolStateError: If configuration values are invalid.

        Example:
            ```python
            success = validator.configure_validation({
                "strict_mode": True,
                "exclude_patterns": ["**/test_*"]
            })
            ```
        """
        ...
