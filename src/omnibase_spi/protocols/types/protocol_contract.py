"""
Protocol for ONEX contract objects.

Domain: Core system protocols (contract management)
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolContract(Protocol):
    """
    Protocol for ONEX contract objects.

    Defines the interface for contract objects in the ONEX distributed system,
    including identification, versioning, metadata management, and serialization.
    Contracts define behavioral agreements between system components.

    Key Features:
        - Unique contract identification
        - Semantic versioning support
        - Extensible metadata dictionary
        - Bidirectional serialization (to/from dict)

    Usage:
        contract = get_contract()
        contract_id = contract.contract_id
        version = contract.version
        metadata = contract.metadata

        # Serialization
        contract_dict = contract.to_dict()

        # Deserialization
        restored_contract = ContractImpl.from_dict(contract_dict)
    """

    @property
    def contract_id(self) -> str:
        """
        Get unique contract identifier.

        Returns:
            Unique string identifier for this contract instance
        """
        ...

    @property
    def version(self) -> str:
        """
        Get contract version.

        Returns:
            Semantic version string (e.g., "1.2.3")
        """
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """
        Get contract metadata.

        Returns:
            Dictionary containing contract metadata and configuration
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize contract to dictionary.

        Returns:
            Dictionary representation of the contract suitable for
            persistence or transmission
        """
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProtocolContract":
        """
        Deserialize contract from dictionary.

        Args:
            data: Dictionary containing serialized contract data

        Returns:
            New contract instance created from the dictionary data
        """
        ...
