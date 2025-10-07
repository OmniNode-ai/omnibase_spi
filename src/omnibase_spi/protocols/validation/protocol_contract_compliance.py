"""
Protocol interface for contract compliance validation tools in ONEX ecosystem.

This protocol defines the interface that contract compliance validation tools must implement.
Provides type-safe contracts for SPI purity validation, namespace isolation checking, and
compliance verification across ONEX service components.

Domain: Validation and Compliance
Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus
    from omnibase_spi.protocols.file_handling.protocol_file_io import ProtocolFileIO
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
    ) -> list["ProtocolValidationResult"]: ...

    def is_compliant(self, results: list["ProtocolValidationResult"]) -> bool: ...

    async def get_violations(
        self, results: list["ProtocolValidationResult"]
    ) -> list["ProtocolValidationResult"]: ...

    def generate_compliance_report(
        self, results: list["ProtocolValidationResult"], format: str | None = None
    ) -> str: ...

    def configure_validation(
        self, configuration: dict[str, "ContextValue"]
    ) -> bool: ...
