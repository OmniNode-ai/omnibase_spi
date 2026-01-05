"""
Unit tests for ProtocolHandlerContractFactory.

Tests the Protocol interface for handler contract factories. Since the SPI
only defines Protocol interfaces (not implementations), these tests verify:
- Protocol is runtime_checkable
- Protocol defines expected method signatures
- Mock implementations satisfy the Protocol interface

Note:
    The concrete HandlerContractFactory implementation has been moved to
    omnibase_infra. These tests now focus on Protocol compliance, not
    implementation behavior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from omnibase_core.enums import EnumHandlerTypeCategory
from omnibase_spi.protocols.factories import ProtocolHandlerContractFactory

if TYPE_CHECKING:
    from omnibase_core.models.contracts.model_handler_contract import (
        ModelHandlerContract,
    )
    from omnibase_core.models.primitives.model_semver import ModelSemVer


# =============================================================================
# Mock Implementation for Testing
# =============================================================================


class MockHandlerContractFactory:
    """Mock implementation of ProtocolHandlerContractFactory for testing.

    This mock demonstrates what a concrete implementation should look like.
    The actual implementation lives in omnibase_infra.
    """

    def __init__(self) -> None:
        """Initialize the mock factory."""
        self._supported_types = [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ]

    def get_default(
        self,
        handler_type: EnumHandlerTypeCategory,
        handler_name: str,
        version: ModelSemVer | str = "1.0.0",
    ) -> ModelHandlerContract:
        """Get a default handler contract for the given handler type.

        Args:
            handler_type: The category of handler.
            handler_name: Unique identifier for the handler.
            version: Contract version.

        Returns:
            A mock ModelHandlerContract (MagicMock for testing).
        """
        if handler_type not in self._supported_types:
            raise ValueError(f"Unsupported handler type: {handler_type}")

        # Return a mock contract for testing purposes
        mock_contract = MagicMock()
        mock_contract.handler_id = handler_name
        mock_contract.name = handler_name
        mock_contract.version = str(version)
        return mock_contract

    def available_types(self) -> list[EnumHandlerTypeCategory]:
        """Return list of handler types this factory supports.

        Returns:
            List of supported EnumHandlerTypeCategory values.
        """
        return list(self._supported_types)


# =============================================================================
# Protocol Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolHandlerContractFactoryProtocol:
    """Tests verifying the Protocol interface definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """Test that ProtocolHandlerContractFactory is runtime_checkable."""
        # The Protocol should be decorated with @runtime_checkable
        # which allows isinstance() checks
        mock = MockHandlerContractFactory()
        assert isinstance(mock, ProtocolHandlerContractFactory)

    def test_protocol_has_get_default_method(self) -> None:
        """Test that Protocol defines get_default method."""
        # Verify the method exists in the Protocol
        assert hasattr(ProtocolHandlerContractFactory, "get_default")

    def test_protocol_has_available_types_method(self) -> None:
        """Test that Protocol defines available_types method."""
        # Verify the method exists in the Protocol
        assert hasattr(ProtocolHandlerContractFactory, "available_types")

    def test_mock_implementation_satisfies_protocol(self) -> None:
        """Test that mock implementation passes isinstance check."""
        mock = MockHandlerContractFactory()

        # isinstance check should pass for runtime_checkable Protocol
        assert isinstance(mock, ProtocolHandlerContractFactory)

    def test_incomplete_implementation_fails_protocol(self) -> None:
        """Test that incomplete implementation fails Protocol check."""

        class IncompleteFactory:
            """Factory missing required methods."""

            pass

        # isinstance should fail for incomplete implementation
        incomplete = IncompleteFactory()
        assert not isinstance(incomplete, ProtocolHandlerContractFactory)

    def test_partial_implementation_fails_protocol(self) -> None:
        """Test that partial implementation (missing available_types) fails."""

        class PartialFactory:
            """Factory with only get_default method."""

            def get_default(
                self,
                handler_type: EnumHandlerTypeCategory,
                handler_name: str,
                version: str = "1.0.0",
            ) -> MagicMock:
                return MagicMock()

        partial = PartialFactory()
        # Missing available_types method
        assert not isinstance(partial, ProtocolHandlerContractFactory)


# =============================================================================
# Mock Implementation Behavior Tests
# =============================================================================


@pytest.mark.unit
class TestMockHandlerContractFactory:
    """Tests for the mock implementation behavior.

    These tests demonstrate expected implementation behavior patterns.
    """

    def test_mock_factory_instantiation(self) -> None:
        """Test mock factory can be instantiated."""
        factory = MockHandlerContractFactory()
        assert factory is not None

    def test_mock_available_types_returns_all_categories(self) -> None:
        """Test available_types returns expected handler categories."""
        factory = MockHandlerContractFactory()
        types = factory.available_types()

        assert EnumHandlerTypeCategory.COMPUTE in types
        assert EnumHandlerTypeCategory.EFFECT in types
        assert EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE in types
        assert len(types) == 3

    def test_mock_available_types_returns_list(self) -> None:
        """Test available_types returns a list type."""
        factory = MockHandlerContractFactory()
        types = factory.available_types()

        assert isinstance(types, list)

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_mock_get_default_returns_contract(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test get_default returns a contract for all supported types."""
        factory = MockHandlerContractFactory()
        contract = factory.get_default(
            handler_type=handler_type,
            handler_name="test.handler",
            version="1.0.0",
        )

        # Mock returns a MagicMock with expected attributes
        assert contract is not None
        assert contract.handler_id == "test.handler"

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_mock_get_default_uses_provided_handler_name(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test get_default uses the provided handler name."""
        factory = MockHandlerContractFactory()
        handler_name = "my.custom.handler"

        contract = factory.get_default(
            handler_type=handler_type,
            handler_name=handler_name,
        )

        assert contract.handler_id == handler_name
        assert contract.name == handler_name

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_mock_get_default_uses_provided_version(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test get_default uses the provided version."""
        factory = MockHandlerContractFactory()
        version = "2.5.0"

        contract = factory.get_default(
            handler_type=handler_type,
            handler_name="test.handler",
            version=version,
        )

        assert contract.version == version

    def test_mock_get_default_uses_default_version(self) -> None:
        """Test get_default uses 1.0.0 when version not specified."""
        factory = MockHandlerContractFactory()

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
        )

        assert contract.version == "1.0.0"

    def test_mock_get_default_raises_for_unsupported_type(self) -> None:
        """Test get_default raises ValueError for unsupported type."""
        factory = MockHandlerContractFactory()

        # Pass an invalid handler type (string instead of enum)
        with pytest.raises(ValueError, match="Unsupported handler type"):
            factory.get_default(
                handler_type="INVALID_TYPE",  # type: ignore[arg-type]
                handler_name="test.handler",
            )


# =============================================================================
# Import Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolImports:
    """Tests verifying Protocol imports work correctly."""

    def test_import_from_protocols_factories_module(self) -> None:
        """Test import from protocols/factories module."""
        from omnibase_spi.protocols.factories import (
            ProtocolHandlerContractFactory as DirectProtocol,
        )

        assert DirectProtocol is not None

    def test_import_from_factories_package(self) -> None:
        """Test import from factories package (re-export)."""
        from omnibase_spi.factories import (
            ProtocolHandlerContractFactory as PackageProtocol,
        )

        assert PackageProtocol is not None

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same Protocol."""
        from omnibase_spi.factories import (
            ProtocolHandlerContractFactory as PackageProtocol,
        )
        from omnibase_spi.protocols.factories import (
            ProtocolHandlerContractFactory as DirectProtocol,
        )

        assert DirectProtocol is PackageProtocol

    def test_import_from_protocols_root(self) -> None:
        """Test import from protocols root module."""
        from omnibase_spi.protocols import (
            ProtocolHandlerContractFactory as RootProtocol,
        )

        assert RootProtocol is not None


# =============================================================================
# Protocol Documentation Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolDocumentation:
    """Tests verifying Protocol has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """Test that Protocol class has a docstring."""
        assert ProtocolHandlerContractFactory.__doc__ is not None
        assert len(ProtocolHandlerContractFactory.__doc__) > 0

    def test_get_default_has_docstring(self) -> None:
        """Test that get_default method has a docstring."""
        method = getattr(ProtocolHandlerContractFactory, "get_default", None)
        assert method is not None
        assert method.__doc__ is not None

    def test_available_types_has_docstring(self) -> None:
        """Test that available_types method has a docstring."""
        method = getattr(ProtocolHandlerContractFactory, "available_types", None)
        assert method is not None
        assert method.__doc__ is not None
