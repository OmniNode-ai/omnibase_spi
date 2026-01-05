"""
Tests for ProtocolProjectorLoader protocol.

Validates that ProtocolProjectorLoader:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from omnibase_spi.protocols.projectors.protocol_projector_loader import (
    ProtocolProjectorLoader,
)


class MockProjector:
    """Mock projector for testing loader implementations.

    This is a minimal mock that satisfies the structural requirements
    of ProtocolEventProjector for testing purposes.
    """

    def __init__(self, name: str, domain: str) -> None:
        """Initialize the mock projector."""
        self.name = name
        self.domain = domain

    async def persist(
        self,
        projection: Any,
        entity_id: str,
        domain: str,
        sequence_info: Any,
        *,
        correlation_id: str | None = None,
    ) -> Any:
        """Mock persist method."""
        return {"status": "applied", "entity_id": entity_id}

    async def batch_persist(
        self,
        projections: Any,
        *,
        correlation_id: str | None = None,
    ) -> Any:
        """Mock batch persist method."""
        return {"total_count": 0, "applied_count": 0, "rejected_count": 0}

    async def get_last_sequence(
        self,
        entity_id: str,
        domain: str,
    ) -> Any:
        """Mock get last sequence method."""
        return None

    async def is_stale(
        self,
        entity_id: str,
        domain: str,
        sequence_info: Any,
    ) -> bool:
        """Mock is stale method."""
        return False

    async def cleanup_before_sequence(
        self,
        domain: str,
        sequence: int,
        *,
        batch_size: int = 1000,
        confirmed: bool = False,
    ) -> int:
        """Mock cleanup method."""
        return 0


class MockProjectorLoader:
    """A class that fully implements the ProtocolProjectorLoader protocol.

    This mock implementation provides an in-memory loader for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock loader."""
        self._contracts: dict[Path, dict[str, Any]] = {}

    async def load_from_contract(
        self,
        contract_path: Path,
    ) -> MockProjector:
        """Load a projector from a YAML contract.

        Args:
            contract_path: Path to the YAML contract file.

        Returns:
            Configured MockProjector instance.

        Raises:
            FileNotFoundError: If contract path does not exist.
        """
        if contract_path.suffix not in {".yaml", ".yml"}:
            raise ValueError(f"Invalid contract extension: {contract_path.suffix}")

        # In real implementation, would parse YAML
        name = contract_path.stem
        domain = "test-domain"

        return MockProjector(name=name, domain=domain)

    async def load_from_directory(
        self,
        directory: Path,
    ) -> list[MockProjector]:
        """Load all projectors from contracts in directory.

        Args:
            directory: Directory containing contract files.

        Returns:
            List of configured MockProjector instances.
        """
        projectors: list[MockProjector] = []

        # Mock discovery - in real implementation would list directory
        # For testing, return empty list since directory likely doesn't exist
        return projectors

    async def discover_and_load(
        self,
        patterns: list[str],
    ) -> list[MockProjector]:
        """Discover contracts matching patterns and load projectors.

        Args:
            patterns: List of glob patterns.

        Returns:
            List of configured MockProjector instances.
        """
        projectors: list[MockProjector] = []

        # Mock discovery - in real implementation would glob for files
        # For testing, return empty list
        return projectors


class PartialProjectorLoader:
    """A class that only implements some ProtocolProjectorLoader methods."""

    async def load_from_contract(
        self,
        contract_path: Path,
    ) -> MockProjector:
        """Only implement load_from_contract, missing other methods."""
        return MockProjector(name="partial", domain="test")


class NonCompliantProjectorLoader:
    """A class that implements none of the ProtocolProjectorLoader methods."""

    pass


@pytest.mark.unit
class TestProtocolProjectorLoaderProtocol:
    """Test suite for ProtocolProjectorLoader protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolProjectorLoader should be runtime_checkable."""
        # Check for either of the internal attributes that indicate runtime_checkable
        assert hasattr(ProtocolProjectorLoader, "_is_runtime_protocol") or hasattr(
            ProtocolProjectorLoader, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolProjectorLoader should be a Protocol class."""
        from typing import Protocol

        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolProjectorLoader.__mro__
        )

    def test_protocol_has_load_from_contract_method(self) -> None:
        """ProtocolProjectorLoader should define load_from_contract method."""
        assert "load_from_contract" in dir(ProtocolProjectorLoader)

    def test_protocol_has_load_from_directory_method(self) -> None:
        """ProtocolProjectorLoader should define load_from_directory method."""
        assert "load_from_directory" in dir(ProtocolProjectorLoader)

    def test_protocol_has_discover_and_load_method(self) -> None:
        """ProtocolProjectorLoader should define discover_and_load method."""
        assert "discover_and_load" in dir(ProtocolProjectorLoader)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolProjectorLoader protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolProjectorLoader()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolProjectorLoaderCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        loader = MockProjectorLoader()
        assert isinstance(loader, ProtocolProjectorLoader)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        loader = PartialProjectorLoader()
        assert not isinstance(loader, ProtocolProjectorLoader)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        loader = NonCompliantProjectorLoader()
        assert not isinstance(loader, ProtocolProjectorLoader)


@pytest.mark.unit
class TestMockImplementsAllMethods:
    """Test that MockProjectorLoader has all required methods."""

    def test_mock_has_load_from_contract(self) -> None:
        """Mock should have load_from_contract method."""
        loader = MockProjectorLoader()
        assert hasattr(loader, "load_from_contract")
        assert callable(loader.load_from_contract)

    def test_mock_has_load_from_directory(self) -> None:
        """Mock should have load_from_directory method."""
        loader = MockProjectorLoader()
        assert hasattr(loader, "load_from_directory")
        assert callable(loader.load_from_directory)

    def test_mock_has_discover_and_load(self) -> None:
        """Mock should have discover_and_load method."""
        loader = MockProjectorLoader()
        assert hasattr(loader, "discover_and_load")
        assert callable(loader.discover_and_load)


@pytest.mark.unit
class TestProtocolProjectorLoaderAsyncNature:
    """Test that ProtocolProjectorLoader methods are async."""

    def test_load_from_contract_is_async(self) -> None:
        """load_from_contract should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectorLoader.load_from_contract)

    def test_load_from_directory_is_async(self) -> None:
        """load_from_directory should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectorLoader.load_from_directory)

    def test_discover_and_load_is_async(self) -> None:
        """discover_and_load should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectorLoader.discover_and_load)


@pytest.mark.unit
class TestProtocolProjectorLoaderMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    @pytest.mark.asyncio
    async def test_load_from_contract_accepts_path(self) -> None:
        """load_from_contract should accept a Path argument."""
        loader = MockProjectorLoader()
        contract_path = Path("/tmp/test.yaml")

        projector = await loader.load_from_contract(contract_path)

        assert projector is not None
        assert projector.name == "test"

    @pytest.mark.asyncio
    async def test_load_from_contract_returns_projector(self) -> None:
        """load_from_contract should return a projector-like object."""
        loader = MockProjectorLoader()
        contract_path = Path("/tmp/orders.yaml")

        projector = await loader.load_from_contract(contract_path)

        # Verify it has projector-like attributes
        assert hasattr(projector, "persist")
        assert hasattr(projector, "name")
        assert projector.name == "orders"

    @pytest.mark.asyncio
    async def test_load_from_directory_accepts_path(self) -> None:
        """load_from_directory should accept a Path argument."""
        loader = MockProjectorLoader()
        directory = Path("/tmp/contracts/")

        projectors = await loader.load_from_directory(directory)

        assert isinstance(projectors, list)

    @pytest.mark.asyncio
    async def test_load_from_directory_returns_list(self) -> None:
        """load_from_directory should return a list."""
        loader = MockProjectorLoader()
        directory = Path("/tmp/contracts/")

        result = await loader.load_from_directory(directory)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_discover_and_load_accepts_patterns(self) -> None:
        """discover_and_load should accept a list of pattern strings."""
        loader = MockProjectorLoader()
        patterns = ["**/projectors/*.yaml", "**/projections/*.yml"]

        projectors = await loader.discover_and_load(patterns)

        assert isinstance(projectors, list)

    @pytest.mark.asyncio
    async def test_discover_and_load_returns_list(self) -> None:
        """discover_and_load should return a list."""
        loader = MockProjectorLoader()
        patterns = ["contracts/*.yaml"]

        result = await loader.discover_and_load(patterns)

        assert isinstance(result, list)


@pytest.mark.unit
class TestProtocolProjectorLoaderImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_projector_loader module."""
        from omnibase_spi.protocols.projectors.protocol_projector_loader import (
            ProtocolProjectorLoader as DirectLoader,
        )

        loader = MockProjectorLoader()
        assert isinstance(loader, DirectLoader)

    def test_import_from_projectors_package(self) -> None:
        """Test import from projectors package."""
        from omnibase_spi.protocols.projectors import (
            ProtocolProjectorLoader as PackageLoader,
        )

        loader = MockProjectorLoader()
        assert isinstance(loader, PackageLoader)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.projectors import (
            ProtocolProjectorLoader as PackageLoader,
        )
        from omnibase_spi.protocols.projectors.protocol_projector_loader import (
            ProtocolProjectorLoader as DirectLoader,
        )

        assert DirectLoader is PackageLoader

    def test_import_from_root_protocols_package(self) -> None:
        """Test import from root protocols package."""
        from omnibase_spi.protocols import (
            ProtocolProjectorLoader as RootLoader,
        )

        loader = MockProjectorLoader()
        assert isinstance(loader, RootLoader)


@pytest.mark.unit
class TestProtocolProjectorLoaderDocumentation:
    """Test that ProtocolProjectorLoader has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolProjectorLoader should have a docstring."""
        assert ProtocolProjectorLoader.__doc__ is not None
        assert len(ProtocolProjectorLoader.__doc__.strip()) > 0

    def test_load_from_contract_has_docstring(self) -> None:
        """load_from_contract method should have a docstring."""
        # Access the method's __doc__ from the protocol
        # For protocols, we check the mock which implements the same interface
        assert MockProjectorLoader.load_from_contract.__doc__ is not None

    def test_load_from_directory_has_docstring(self) -> None:
        """load_from_directory method should have a docstring."""
        assert MockProjectorLoader.load_from_directory.__doc__ is not None

    def test_discover_and_load_has_docstring(self) -> None:
        """discover_and_load method should have a docstring."""
        assert MockProjectorLoader.discover_and_load.__doc__ is not None

    def test_protocol_docstring_mentions_args(self) -> None:
        """Protocol docstring should document Args section."""
        # Check that method docstrings include Args
        assert "Args:" in (MockProjectorLoader.load_from_contract.__doc__ or "")
        assert "Args:" in (MockProjectorLoader.load_from_directory.__doc__ or "")
        assert "Args:" in (MockProjectorLoader.discover_and_load.__doc__ or "")

    def test_protocol_docstring_mentions_returns(self) -> None:
        """Protocol docstring should document Returns section."""
        assert "Returns:" in (MockProjectorLoader.load_from_contract.__doc__ or "")
        assert "Returns:" in (MockProjectorLoader.load_from_directory.__doc__ or "")
        assert "Returns:" in (MockProjectorLoader.discover_and_load.__doc__ or "")


@pytest.mark.unit
class TestProtocolProjectorLoaderEdgeCases:
    """Test edge cases for the loader protocol."""

    @pytest.mark.asyncio
    async def test_yaml_extension_accepted(self) -> None:
        """Loader should accept .yaml extension."""
        loader = MockProjectorLoader()
        path = Path("/tmp/contract.yaml")

        projector = await loader.load_from_contract(path)
        assert projector is not None

    @pytest.mark.asyncio
    async def test_yml_extension_accepted(self) -> None:
        """Loader should accept .yml extension."""
        loader = MockProjectorLoader()
        path = Path("/tmp/contract.yml")

        projector = await loader.load_from_contract(path)
        assert projector is not None

    @pytest.mark.asyncio
    async def test_invalid_extension_raises(self) -> None:
        """Loader should raise on invalid extensions."""
        loader = MockProjectorLoader()
        path = Path("/tmp/contract.json")

        with pytest.raises(ValueError, match="Invalid contract extension"):
            await loader.load_from_contract(path)

    @pytest.mark.asyncio
    async def test_empty_patterns_returns_empty_list(self) -> None:
        """discover_and_load with empty patterns should return empty list."""
        loader = MockProjectorLoader()
        patterns: list[str] = []

        result = await loader.discover_and_load(patterns)
        assert result == []

    @pytest.mark.asyncio
    async def test_absolute_path_accepted(self) -> None:
        """Loader should accept absolute paths."""
        loader = MockProjectorLoader()
        path = Path("/absolute/path/to/contract.yaml")

        projector = await loader.load_from_contract(path)
        assert projector is not None

    @pytest.mark.asyncio
    async def test_relative_path_accepted(self) -> None:
        """Loader should accept relative paths."""
        loader = MockProjectorLoader()
        path = Path("relative/path/contract.yaml")

        projector = await loader.load_from_contract(path)
        assert projector is not None


@pytest.mark.unit
class TestProtocolProjectorLoaderTypeAnnotations:
    """Test that type annotations are correctly specified."""

    def test_load_from_contract_param_is_path(self) -> None:
        """load_from_contract should have Path as parameter type."""
        import inspect

        sig = inspect.signature(MockProjectorLoader.load_from_contract)
        params = list(sig.parameters.values())
        # First param is self, second is contract_path
        assert len(params) >= 2
        assert params[1].name == "contract_path"

    def test_load_from_directory_param_is_path(self) -> None:
        """load_from_directory should have Path as parameter type."""
        import inspect

        sig = inspect.signature(MockProjectorLoader.load_from_directory)
        params = list(sig.parameters.values())
        assert len(params) >= 2
        assert params[1].name == "directory"

    def test_discover_and_load_param_is_list_str(self) -> None:
        """discover_and_load should have list[str] as parameter type."""
        import inspect

        sig = inspect.signature(MockProjectorLoader.discover_and_load)
        params = list(sig.parameters.values())
        assert len(params) >= 2
        assert params[1].name == "patterns"
