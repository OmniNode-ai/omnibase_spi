"""Protocols for model registry validation and health reporting."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.schema.protocol_trusted_schema_loader import (
        ProtocolSchemaValidationResult,
    )

# Type alias for backward compatibility
type ProtocolModelValidationResult = ProtocolSchemaValidationResult


@runtime_checkable
class ProtocolRegistryHealthReport(Protocol):
    """
    Protocol for model registry health status reporting.

    Provides comprehensive health metrics for model registries
    including overall status, registry counts, conflict detection,
    validation errors, and performance measurements.

    Attributes:
        is_healthy: Overall health status of all registries
        registry_count: Number of registries under management
        conflict_count: Number of detected conflicts across registries
        validation_errors: List of validation error messages
        performance_metrics: Dictionary of performance measurements

    Example:
        ```python
        validator: ProtocolModelRegistryValidator = get_registry_validator()
        health = await validator.get_registry_health()

        print(f"Healthy: {health.is_healthy}")
        print(f"Registries: {health.registry_count}")
        print(f"Conflicts: {health.conflict_count}")

        if not health.is_healthy:
            for error in health.validation_errors:
                print(f"  Error: {error}")

        summary = await health.get_summary()
        ```

    See Also:
        - ProtocolModelRegistryValidator: Health reporting source
        - ProtocolSchemaValidationResult: Individual validation results
    """

    is_healthy: bool
    registry_count: int
    conflict_count: int
    validation_errors: list[str]
    performance_metrics: dict[str, float]

    async def get_summary(self) -> "JsonType":
        """Get a summary of the registry health status.

        Produces a condensed summary of the health report suitable for
        logging, dashboards, or quick status checks.

        Returns:
            JSON-compatible dictionary containing summary information
            including health status, counts, and key metrics.
        """
        ...


@runtime_checkable
class ProtocolModelRegistryValidator(Protocol):
    """
    Protocol for comprehensive model registry validation and conflict detection.

    Provides validation operations for dynamic model registries including
    action registries, event type registries, capability registries, and
    node reference registries with conflict detection and integrity auditing.

    Example:
        ```python
        validator: ProtocolModelRegistryValidator = get_registry_validator()

        # Validate individual registries
        action_result = await validator.validate_action_registry()
        event_result = await validator.validate_event_type_registry()
        capability_result = await validator.validate_capability_registry()
        node_ref_result = await validator.validate_node_reference_registry()

        # Validate all registries at once
        all_result = await validator.validate_all_registries()

        # Detect conflicts across registries
        conflicts = await validator.detect_conflicts()
        for conflict in conflicts:
            print(f"Conflict: {conflict}")

        # Verify contract compliance
        contract_result = await validator.verify_contract_compliance(
            "/path/to/contract.yaml"
        )

        # Lock verified models
        locked_models = validator.lock_verified_models()

        # Get overall registry health
        health = await validator.get_registry_health()

        # Audit model integrity
        audit_result = await validator.audit_model_integrity()
        ```

    See Also:
        - ProtocolRegistryHealthReport: Health status
        - ProtocolSchemaValidationResult: Validation results
    """

    async def validate_action_registry(self) -> "ProtocolSchemaValidationResult":
        """Validate action registry for conflicts and compliance.

        Checks the action registry for duplicate action names, invalid
        action definitions, and compliance with schema requirements.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.
        """
        ...

    async def validate_event_type_registry(self) -> "ProtocolSchemaValidationResult":
        """Validate event type registry for conflicts and compliance.

        Checks the event type registry for duplicate event types, invalid
        event definitions, and compliance with schema requirements.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.
        """
        ...

    async def validate_capability_registry(self) -> "ProtocolSchemaValidationResult":
        """Validate capability registry for conflicts and compliance.

        Checks the capability registry for duplicate capabilities, invalid
        capability definitions, and compliance with schema requirements.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.
        """
        ...

    async def validate_node_reference_registry(
        self,
    ) -> "ProtocolSchemaValidationResult":
        """Validate node reference registry for conflicts and compliance.

        Checks the node reference registry for duplicate node references,
        invalid reference definitions, and compliance with schema requirements.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.
        """
        ...

    async def validate_all_registries(self) -> "ProtocolSchemaValidationResult":
        """Validate all dynamic registries comprehensively.

        Performs validation on all registry types (action, event type,
        capability, and node reference) and aggregates the results.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages from all registries.
        """
        ...

    async def detect_conflicts(self) -> list[str]:
        """Detect conflicts across all registries.

        Scans all registries for naming conflicts, duplicate definitions,
        and cross-registry inconsistencies.

        Returns:
            List of conflict description strings, empty if no conflicts found.
        """
        ...

    async def verify_contract_compliance(
        self, contract_path: str
    ) -> "ProtocolSchemaValidationResult":
        """Verify a contract file complies with schema requirements.

        Loads the contract from the specified path and validates it against
        the schema requirements for model contracts.

        Args:
            contract_path: Path to the contract file to validate.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.

        Raises:
            FileNotFoundError: If the contract file does not exist.
        """
        ...

    def lock_verified_models(self) -> "JsonType":
        """Lock verified models with version/timestamp/trust tags.

        Creates a snapshot of all verified models with metadata including
        version, timestamp, and trust level tags for immutability tracking.

        Returns:
            JSON-compatible dictionary containing the locked model snapshot
            with version, timestamp, and trust metadata.
        """
        ...

    async def get_registry_health(self) -> ProtocolRegistryHealthReport:
        """Get overall health status of all registries.

        Collects health metrics from all registries and produces a
        comprehensive health report including status, counts, and metrics.

        Returns:
            Health report containing overall status, registry counts,
            conflict counts, validation errors, and performance metrics.
        """
        ...

    async def audit_model_integrity(self) -> "ProtocolSchemaValidationResult":
        """Audit integrity of all registered models.

        Performs a deep integrity check on all registered models including
        hash verification, dependency validation, and consistency checks.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages from the audit.
        """
        ...
