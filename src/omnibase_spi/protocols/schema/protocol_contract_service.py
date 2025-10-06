"""
Protocol for Contract Service.

Defines the interface for contract loading, parsing, validation, caching,
and metadata extraction operations following ONEX standards.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolMetadata,
        ProtocolSemVer,
    )
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )


@runtime_checkable
class ProtocolContractService(Protocol):
    """
    Protocol for contract service operations following ONEX standards.

    Provides contract management including loading, parsing, validation,
    caching, and metadata extraction for ONEX-compliant systems.

    Key Features:
        - Contract loading and parsing from YAML files
        - Contract validation and structure verification
        - Contract caching for performance optimization
        - Contract metadata extraction and processing
        - Version management and dependency resolution
        - Event pattern extraction
        - Health monitoring

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "ContractService" = get_contract_service()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        contract_service: "ProtocolContractService" = ContractServiceImpl()

        contract = contract_service.load_contract('/path/to/contract.yaml')
        validation_result = contract_service.validate_contract(contract)
        ```
    """

    async def load_contract(self, contract_path: str) -> "ProtocolMetadata": ...

    async def validate_contract(
        self, contract_data: "ProtocolMetadata"
    ) -> "ProtocolValidationResult": ...

    async def get_cached_contract(
        self, contract_path: str
    ) -> "ProtocolMetadata | None": ...

    def cache_contract(
        self, contract_path: str, contract_data: "ProtocolMetadata"
    ) -> bool: ...

    def clear_cache(self, contract_path: str | None = None) -> int: ...

    def extract_node_id(self, contract_data: "ProtocolMetadata") -> str: ...

    def extract_version(
        self, contract_data: "ProtocolMetadata"
    ) -> "ProtocolSemVer": ...

    def extract_dependencies(
        self, contract_data: "ProtocolMetadata"
    ) -> list[dict[str, "ContextValue"]]: ...

    def extract_tool_class_name(self, contract_data: "ProtocolMetadata") -> str: ...

    def extract_event_patterns(
        self, contract_data: "ProtocolMetadata"
    ) -> list[str]: ...

    async def get_cache_statistics(self) -> dict[str, object]: ...
