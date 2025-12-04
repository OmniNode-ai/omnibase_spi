from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.schema.protocol_trusted_schema_loader import (
        ProtocolSchemaValidationResult,
    )

# Type alias for backward compatibility
ProtocolModelValidationResult = "ProtocolSchemaValidationResult"


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

    async def get_summary(self) -> dict[str, Any]: ...


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
        """Validate action registry for conflicts and compliance"""
        ...

    async def validate_event_type_registry(self) -> "ProtocolSchemaValidationResult":
        """Validate event type registry for conflicts and compliance"""
        ...

    async def validate_capability_registry(self) -> "ProtocolSchemaValidationResult":
        """Validate capability registry for conflicts and compliance"""
        ...

    async def validate_node_reference_registry(
        self,
    ) -> "ProtocolSchemaValidationResult":
        """Validate node reference registry for conflicts and compliance"""
        ...

    async def validate_all_registries(self) -> "ProtocolSchemaValidationResult":
        """Validate all dynamic registries comprehensively"""
        ...

    async def detect_conflicts(self) -> list[str]:
        """Detect conflicts across all registries"""
        ...

    async def verify_contract_compliance(
        self, contract_path: str
    ) -> "ProtocolSchemaValidationResult":
        """Verify a contract file complies with schema requirements"""
        ...

    def lock_verified_models(self) -> dict[str, Any]:
        """Lock verified models with version/timestamp/trust tags"""
        ...

    async def get_registry_health(self) -> ProtocolRegistryHealthReport:
        """Get overall health status of all registries"""
        ...

    async def audit_model_integrity(self) -> "ProtocolSchemaValidationResult":
        """Audit integrity of all registered models"""
        ...
