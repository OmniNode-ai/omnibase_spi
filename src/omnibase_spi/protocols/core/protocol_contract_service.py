"""
Protocol for Contract Service.

Defines the interface for contract loading, parsing, validation, caching,
and metadata extraction operations following ONEX standards.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, Union, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolMetadata,
        ProtocolSemVer,
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
        # Implementation example (not part of SPI)
        class ContractServiceImpl:
            def load_contract(self, contract_path: Path) -> dict:
                with open(contract_path) as f:
                    import yaml
                    return yaml.safe_load(f)

            def validate_contract(self, contract_data: dict) -> dict:
                # Validate contract structure and content
                is_valid = self._validate_structure(contract_data)
                return {
                    'is_valid': is_valid,
                    'errors': [],
                    'warnings': []
                }

        # Usage in application code
        contract_service: ProtocolContractService = ContractServiceImpl()

        contract = contract_service.load_contract(Path('/path/to/contract.yaml'))
        validation_result = contract_service.validate_contract(contract)
        ```
    """

    def load_contract(self, contract_path: Path) -> "ProtocolMetadata":
        """
        Load and parse a contract from file system.

        Args:
            contract_path: Path to the contract YAML file

        Returns:
            Fully parsed contract with all references resolved

        Raises:
            FileNotFoundError: If contract file does not exist
            ValueError: If contract format is invalid
            RuntimeError: If contract loading or parsing fails
        """
        ...

    def validate_contract(
        self, contract_data: "ProtocolMetadata"
    ) -> "ProtocolValidationResult":
        """
        Validate contract structure and content.

        Args:
            contract_data: Contract to validate

        Returns:
            Validation result with status, errors, and warnings

        Note:
            Returns structured validation result rather than boolean
            to provide detailed error information for debugging.
        """
        ...

    def get_cached_contract(
        self,
        contract_path: Path,
    ) -> "ProtocolMetadata | None":
        """
        Retrieve contract from cache if available.

        Args:
            contract_path: Path to the contract file

        Returns:
            Cached contract or None if not cached

        Note:
            Cache should consider file modification time for
            automatic invalidation of stale contracts.
        """
        ...

    def cache_contract(
        self,
        contract_path: Path,
        contract_data: "ProtocolMetadata",
    ) -> bool:
        """
        Cache a contract for future retrieval.

        Args:
            contract_path: Path to the contract file
            contract_data: Contract to cache

        Returns:
            True if caching succeeded

        Note:
            Should include cache expiration and size management
            to prevent unbounded memory usage.
        """
        ...

    def clear_cache(self, contract_path: Union[Path, None] = None) -> int:
        """
        Clear contract cache.

        Args:
            contract_path: Specific contract to remove, or None to clear all

        Returns:
            Number of contracts removed from cache

        Note:
            Provides granular cache management for memory optimization
            and cache consistency operations.
        """
        ...

    def extract_node_id(self, contract_data: "ProtocolMetadata") -> str:
        """
        Extract node ID from contract.

        Args:
            contract_data: Contract to extract ID from

        Returns:
            Node identifier

        Raises:
            ValueError: If node ID is missing or invalid
        """
        ...

    def extract_version(self, contract_data: "ProtocolMetadata") -> "ProtocolSemVer":
        """
        Extract semantic version from contract.

        Args:
            contract_data: Contract to extract version from

        Returns:
            Semantic version object

        Raises:
            ValueError: If version is missing or invalid format
        """
        ...

    def extract_dependencies(
        self,
        contract_data: "ProtocolMetadata",
    ) -> list[dict[str, "ContextValue"]]:
        """
        Extract dependency list from contract.

        Args:
            contract_data: Contract to extract dependencies from

        Returns:
            List of dependency specifications

        Note:
            Each dependency specification includes module, class,
            and configuration information for service registration.
        """
        ...

    def extract_tool_class_name(self, contract_data: "ProtocolMetadata") -> str:
        """
        Extract main tool class name from contract.

        Args:
            contract_data: Contract to extract tool class from

        Returns:
            Main tool class name

        Raises:
            ValueError: If tool class name is missing or invalid
        """
        ...

    def extract_event_patterns(self, contract_data: "ProtocolMetadata") -> list[str]:
        """
        Extract event subscription patterns from contract.

        Args:
            contract_data: Contract to extract patterns from

        Returns:
            List of event patterns for subscription

        Note:
            Event patterns support glob-style matching and
            hierarchical event type organization.
        """
        ...

    def get_cache_statistics(self) -> dict[str, object]:
        """
        Get contract cache statistics for monitoring.

        Returns:
            Cache statistics including hit rates, size, and performance metrics

        Note:
            Provides cache metrics for performance monitoring and
            optimization of contract loading and parsing operations.
        """
        ...

    def health_check(self) -> dict[str, object]:
        """
        Perform health check on contract service.

        Returns:
            Health check results with status and metrics

        Note:
            Should include cache statistics, file system access,
            and service availability information.
        """
        ...
