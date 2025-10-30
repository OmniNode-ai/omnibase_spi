"""
Tests for ProtocolContract protocol.

Validates that ProtocolContract:
- Can be imported from omnibase_spi.protocols.types
- Is runtime checkable
- Works with isinstance checks
- Has all required methods and properties
"""

from typing import Any, Dict

import pytest

from omnibase_spi.protocols.types import ProtocolContract


class ConcreteContract:
    """Concrete implementation of ProtocolContract for testing."""

    def __init__(
        self,
        contract_id: str = "test-contract-001",
        version: str = "1.0.0",
        metadata: Dict[str, Any] | None = None,
    ):
        self._contract_id = contract_id
        self._version = version
        self._metadata = metadata or {"created": "2025-10-30"}

    @property
    def contract_id(self) -> str:
        return self._contract_id

    @property
    def version(self) -> str:
        return self._version

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConcreteContract":
        return cls(
            contract_id=data.get("contract_id", "unknown"),
            version=data.get("version", "0.0.0"),
            metadata=data.get("metadata", {}),
        )


def test_protocol_contract_import() -> None:
    """Test that ProtocolContract can be imported."""
    assert ProtocolContract is not None


def test_protocol_contract_isinstance() -> None:
    """Test that ProtocolContract works with isinstance checks."""
    contract = ConcreteContract()
    assert isinstance(contract, ProtocolContract)


def test_protocol_contract_properties() -> None:
    """Test that ProtocolContract implementation has correct properties."""
    contract = ConcreteContract(
        contract_id="test-123", version="2.1.0", metadata={"key": "value"}
    )

    assert contract.contract_id == "test-123"
    assert contract.version == "2.1.0"
    assert contract.metadata == {"key": "value"}


def test_protocol_contract_serialization() -> None:
    """Test that ProtocolContract supports serialization."""
    contract = ConcreteContract(
        contract_id="contract-456", version="1.5.2", metadata={"author": "test"}
    )

    contract_dict = contract.to_dict()
    assert contract_dict["contract_id"] == "contract-456"
    assert contract_dict["version"] == "1.5.2"
    assert contract_dict["metadata"] == {"author": "test"}


def test_protocol_contract_deserialization() -> None:
    """Test that ProtocolContract supports deserialization."""
    data = {
        "contract_id": "restored-contract",
        "version": "3.0.0",
        "metadata": {"restored": True},
    }

    contract = ConcreteContract.from_dict(data)
    assert isinstance(contract, ProtocolContract)
    assert contract.contract_id == "restored-contract"
    assert contract.version == "3.0.0"
    assert contract.metadata == {"restored": True}


def test_protocol_contract_roundtrip() -> None:
    """Test that ProtocolContract can be serialized and deserialized."""
    original = ConcreteContract(
        contract_id="roundtrip-test", version="4.2.1", metadata={"test": "data"}
    )

    # Serialize
    serialized = original.to_dict()

    # Deserialize
    restored = ConcreteContract.from_dict(serialized)

    # Verify
    assert isinstance(restored, ProtocolContract)
    assert restored.contract_id == original.contract_id
    assert restored.version == original.version
    assert restored.metadata == original.metadata


def test_protocol_contract_not_implemented() -> None:
    """Test that objects without required methods don't match the protocol."""

    class IncompleteContract:
        """Contract missing required methods."""

        @property
        def contract_id(self) -> str:
            return "incomplete"

    incomplete = IncompleteContract()
    assert not isinstance(incomplete, ProtocolContract)
