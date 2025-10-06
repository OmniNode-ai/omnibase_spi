from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolModelValidationResult(Protocol):
    """Protocol for validation results."""

    success: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolRegistryHealthReport(Protocol):
    """Protocol for registry health reports."""

    is_healthy: bool
    registry_count: int
    conflict_count: int
    validation_errors: list[str]
    performance_metrics: dict[str, float]

    async def get_summary(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolModelRegistryValidator(Protocol):
    """Protocol for validating dynamic model registries and detecting conflicts"""

    async def validate_action_registry(self) -> "ProtocolModelValidationResult":
        """Validate action registry for conflicts and compliance"""
        ...

    async def validate_event_type_registry(self) -> "ProtocolModelValidationResult":
        """Validate event type registry for conflicts and compliance"""
        ...

    async def validate_capability_registry(self) -> "ProtocolModelValidationResult":
        """Validate capability registry for conflicts and compliance"""
        ...

    async def validate_node_reference_registry(self) -> "ProtocolModelValidationResult":
        """Validate node reference registry for conflicts and compliance"""
        ...

    async def validate_all_registries(self) -> "ProtocolModelValidationResult":
        """Validate all dynamic registries comprehensively"""
        ...

    async def detect_conflicts(self) -> list[str]:
        """Detect conflicts across all registries"""
        ...

    async def verify_contract_compliance(
        self, contract_path: str
    ) -> "ProtocolModelValidationResult":
        """Verify a contract file complies with schema requirements"""
        ...

    def lock_verified_models(self) -> dict[str, Any]:
        """Lock verified models with version/timestamp/trust tags"""
        ...

    async def get_registry_health(self) -> ProtocolRegistryHealthReport:
        """Get overall health status of all registries"""
        ...

    async def audit_model_integrity(self) -> "ProtocolModelValidationResult":
        """Audit integrity of all registered models"""
        ...
