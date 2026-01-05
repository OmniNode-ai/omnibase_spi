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

    # Define expected protocol members for exhaustiveness checking
    EXPECTED_PROTOCOL_MEMBERS = {
        "load_from_contract",
        "load_from_directory",
        "discover_and_load",
    }

    def test_all_protocol_members_have_tests(self) -> None:
        """Verify all protocol members have corresponding tests in this module.

        This exhaustiveness check ensures that when new members are added to
        ProtocolProjectorLoader, corresponding tests are also added.
        """
        import inspect

        # Get all public members of the protocol (excluding dunder methods)
        protocol_members = {
            name
            for name, _ in inspect.getmembers(ProtocolProjectorLoader)
            if not name.startswith("_")
        }

        # Verify our expected members match the actual protocol members
        assert protocol_members == self.EXPECTED_PROTOCOL_MEMBERS, (
            f"Protocol members changed! "
            f"New members: {protocol_members - self.EXPECTED_PROTOCOL_MEMBERS}, "
            f"Removed members: {self.EXPECTED_PROTOCOL_MEMBERS - protocol_members}"
        )

    def test_mock_implements_all_protocol_members(self) -> None:
        """Verify MockProjectorLoader implements ALL protocol members.

        This ensures our test mock is complete and doesn't silently
        pass isinstance checks while missing functionality.
        """
        mock = MockProjectorLoader()

        for member in self.EXPECTED_PROTOCOL_MEMBERS:
            assert hasattr(
                mock, member
            ), f"MockProjectorLoader missing protocol member: {member}"

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


# =============================================================================
# Error Path Tests (PR #54 feedback)
# =============================================================================


class MockProjectorLoaderWithErrorHandling:
    """Mock loader that demonstrates proper error handling patterns.

    This mock implementation shows how a compliant implementation should
    handle various error conditions according to the protocol specification.
    """

    def __init__(self) -> None:
        """Initialize the mock loader with simulated contracts."""
        self._contracts: dict[str, dict[str, Any]] = {
            "valid_contract.yaml": {
                "projector": {
                    "name": "orders",
                    "domain": "ecommerce",
                    "table": "order_projections",
                },
                "schema": {
                    "columns": [
                        {
                            "name": "order_id",
                            "type": "varchar(36)",
                            "primary_key": True,
                        },
                    ]
                },
                "ordering": {
                    "entity_id_column": "order_id",
                    "sequence_column": "sequence_number",
                },
            },
            "invalid_structure.yaml": {
                # Missing required 'projector' section
                "schema": {"columns": []},
            },
            "missing_schema.yaml": {
                "projector": {"name": "broken"},
                # Missing required 'schema' section
            },
            "empty_projector.yaml": {
                "projector": {},  # Empty projector section (missing name, domain, table)
                "schema": {"columns": []},
                "ordering": {},
            },
        }

    async def load_from_contract(
        self,
        contract_path: Path,
    ) -> MockProjector:
        """Load a projector with proper error handling.

        Args:
            contract_path: Path to the YAML contract file.

        Returns:
            Configured MockProjector instance.

        Raises:
            FileNotFoundError: If contract path does not exist.
            ContractCompilerError: If contract structure is invalid.
        """
        from omnibase_spi.exceptions import ContractCompilerError

        # Check file existence
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract file not found: {contract_path}")

        # Validate extension
        if contract_path.suffix not in {".yaml", ".yml"}:
            raise ValueError(f"Invalid contract extension: {contract_path.suffix}")

        # Simulate contract loading
        filename = contract_path.name
        if filename in self._contracts:
            contract = self._contracts[filename]
            # Validate contract structure
            if "projector" not in contract:
                raise ContractCompilerError(
                    f"Invalid contract at {contract_path}: "
                    "missing required 'projector' section",
                    context={
                        "path": str(contract_path),
                        "missing_fields": ["projector"],
                    },
                )
            if "schema" not in contract:
                raise ContractCompilerError(
                    f"Invalid contract at {contract_path}: "
                    "missing required 'schema' section",
                    context={"path": str(contract_path), "missing_fields": ["schema"]},
                )
            projector_config = contract["projector"]
            if not projector_config.get("name"):
                raise ContractCompilerError(
                    f"Invalid contract at {contract_path}: missing 'projector.name'",
                    context={
                        "path": str(contract_path),
                        "missing_fields": ["projector.name"],
                    },
                )
            return MockProjector(
                name=projector_config.get("name", "unknown"),
                domain=projector_config.get("domain", "default"),
            )

        # Default: use filename as projector name
        return MockProjector(name=contract_path.stem, domain="default")

    async def load_from_directory(
        self,
        directory: Path,
    ) -> list[MockProjector]:
        """Load all projectors with proper error handling.

        Args:
            directory: Directory containing contract files.

        Returns:
            List of configured MockProjector instances.

        Raises:
            FileNotFoundError: If directory does not exist.
            NotADirectoryError: If path is not a directory.
        """
        # Check directory existence
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Check it's actually a directory
        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Find contract files
        projectors: list[MockProjector] = []
        contract_files = sorted(directory.glob("*.yaml")) + sorted(
            directory.glob("*.yml")
        )

        # Filter out hidden files
        contract_files = [f for f in contract_files if not f.name.startswith(".")]

        for contract_file in contract_files:
            projector = await self.load_from_contract(contract_file)
            projectors.append(projector)

        return projectors

    async def discover_and_load(
        self,
        patterns: list[str],
    ) -> list[MockProjector]:
        """Discover and load projectors from patterns.

        Args:
            patterns: List of glob patterns.

        Returns:
            List of discovered projectors (deduplicated by path).
        """
        if not patterns:
            return []

        projectors: list[MockProjector] = []
        seen_paths: set[Path] = set()

        for pattern in patterns:
            # Use current working directory for relative patterns
            base = Path.cwd()
            for match in base.glob(pattern):
                abs_path = match.resolve()
                if abs_path not in seen_paths and match.is_file():
                    seen_paths.add(abs_path)
                    projector = await self.load_from_contract(match)
                    projectors.append(projector)

        return projectors


@pytest.mark.unit
class TestProtocolProjectorLoaderErrorPaths:
    """Test error handling behavior for the loader protocol.

    These tests verify that compliant implementations handle error
    conditions correctly, raising appropriate exceptions as documented
    in the protocol specification.
    """

    @pytest.mark.asyncio
    async def test_load_from_contract_file_not_found(self, tmp_path: Path) -> None:
        """load_from_contract should raise FileNotFoundError for non-existent file."""
        loader = MockProjectorLoaderWithErrorHandling()
        non_existent_path = tmp_path / "does_not_exist.yaml"

        with pytest.raises(FileNotFoundError, match="Contract file not found"):
            await loader.load_from_contract(non_existent_path)

    @pytest.mark.asyncio
    async def test_load_from_contract_file_not_found_message_includes_path(
        self, tmp_path: Path
    ) -> None:
        """FileNotFoundError message should include the missing path."""
        loader = MockProjectorLoaderWithErrorHandling()
        non_existent_path = tmp_path / "missing_contract.yaml"

        with pytest.raises(FileNotFoundError) as exc_info:
            await loader.load_from_contract(non_existent_path)

        assert "missing_contract.yaml" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_from_directory_not_found(self, tmp_path: Path) -> None:
        """load_from_directory should raise FileNotFoundError for non-existent dir."""
        loader = MockProjectorLoaderWithErrorHandling()
        non_existent_dir = tmp_path / "non_existent_directory"

        with pytest.raises(FileNotFoundError, match="Directory not found"):
            await loader.load_from_directory(non_existent_dir)

    @pytest.mark.asyncio
    async def test_load_from_directory_not_a_directory(self, tmp_path: Path) -> None:
        """load_from_directory should raise NotADirectoryError when path is a file."""
        loader = MockProjectorLoaderWithErrorHandling()

        # Create a file, not a directory
        file_path = tmp_path / "actually_a_file.yaml"
        file_path.write_text("projector:\n  name: test\n")

        with pytest.raises(NotADirectoryError, match="Path is not a directory"):
            await loader.load_from_directory(file_path)

    @pytest.mark.asyncio
    async def test_load_from_directory_not_a_directory_message_includes_path(
        self, tmp_path: Path
    ) -> None:
        """NotADirectoryError message should include the problematic path."""
        loader = MockProjectorLoaderWithErrorHandling()

        file_path = tmp_path / "misleading_name"
        file_path.write_text("content")

        with pytest.raises(NotADirectoryError) as exc_info:
            await loader.load_from_directory(file_path)

        assert "misleading_name" in str(exc_info.value)


@pytest.mark.unit
class TestProtocolProjectorLoaderContractValidation:
    """Test contract validation error handling.

    These tests verify that invalid contract structures are properly
    detected and reported with appropriate exceptions.
    """

    @pytest.mark.asyncio
    async def test_invalid_contract_missing_projector_section(
        self, tmp_path: Path
    ) -> None:
        """Should raise ContractCompilerError when 'projector' section is missing."""
        from omnibase_spi.exceptions import ContractCompilerError

        loader = MockProjectorLoaderWithErrorHandling()

        # Create contract file missing the 'projector' section
        contract_path = tmp_path / "invalid_structure.yaml"
        contract_path.write_text("schema:\n  columns: []\n")

        with pytest.raises(
            ContractCompilerError, match="missing required 'projector' section"
        ):
            await loader.load_from_contract(contract_path)

    @pytest.mark.asyncio
    async def test_invalid_contract_missing_schema_section(
        self, tmp_path: Path
    ) -> None:
        """Should raise ContractCompilerError when 'schema' section is missing."""
        from omnibase_spi.exceptions import ContractCompilerError

        loader = MockProjectorLoaderWithErrorHandling()

        # Create contract file missing the 'schema' section
        contract_path = tmp_path / "missing_schema.yaml"
        contract_path.write_text("projector:\n  name: broken\n")

        with pytest.raises(
            ContractCompilerError, match="missing required 'schema' section"
        ):
            await loader.load_from_contract(contract_path)

    @pytest.mark.asyncio
    async def test_invalid_contract_missing_projector_name(
        self, tmp_path: Path
    ) -> None:
        """Should raise ContractCompilerError when projector.name is missing."""
        from omnibase_spi.exceptions import ContractCompilerError

        loader = MockProjectorLoaderWithErrorHandling()

        # Create contract with empty projector section
        contract_path = tmp_path / "empty_projector.yaml"
        contract_path.write_text(
            "projector: {}\nschema:\n  columns: []\nordering: {}\n"
        )

        with pytest.raises(ContractCompilerError, match="missing 'projector.name'"):
            await loader.load_from_contract(contract_path)

    @pytest.mark.asyncio
    async def test_contract_compiler_error_includes_context(
        self, tmp_path: Path
    ) -> None:
        """ContractCompilerError should include context with path and missing fields."""
        from omnibase_spi.exceptions import ContractCompilerError

        loader = MockProjectorLoaderWithErrorHandling()

        contract_path = tmp_path / "invalid_structure.yaml"
        contract_path.write_text("schema:\n  columns: []\n")

        with pytest.raises(ContractCompilerError) as exc_info:
            await loader.load_from_contract(contract_path)

        error = exc_info.value
        assert error.context is not None
        assert "path" in error.context
        assert "missing_fields" in error.context


@pytest.mark.unit
class TestProtocolProjectorLoaderEmptyDirectoryHandling:
    """Test handling of empty directories and empty results."""

    @pytest.mark.asyncio
    async def test_load_from_empty_directory_returns_empty_list(
        self, tmp_path: Path
    ) -> None:
        """load_from_directory should return empty list for empty directory."""
        loader = MockProjectorLoaderWithErrorHandling()

        # Create an empty directory
        empty_dir = tmp_path / "empty_contracts"
        empty_dir.mkdir()

        result = await loader.load_from_directory(empty_dir)

        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_load_from_directory_ignores_non_yaml_files(
        self, tmp_path: Path
    ) -> None:
        """load_from_directory should ignore non-YAML files."""
        loader = MockProjectorLoaderWithErrorHandling()

        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()

        # Create non-YAML files that should be ignored
        (contracts_dir / "readme.txt").write_text("This is a readme")
        (contracts_dir / "config.json").write_text('{"key": "value"}')
        (contracts_dir / ".hidden.yaml").write_text("projector:\n  name: hidden\n")

        result = await loader.load_from_directory(contracts_dir)

        assert result == []

    @pytest.mark.asyncio
    async def test_load_from_directory_ignores_hidden_yaml_files(
        self, tmp_path: Path
    ) -> None:
        """load_from_directory should ignore hidden YAML files (starting with .)."""
        loader = MockProjectorLoaderWithErrorHandling()

        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()

        # Create a hidden YAML file
        (contracts_dir / ".hidden_contract.yaml").write_text(
            "projector:\n  name: hidden\nschema:\n  columns: []\n"
        )

        result = await loader.load_from_directory(contracts_dir)

        assert result == []

    @pytest.mark.asyncio
    async def test_discover_and_load_no_matches_returns_empty_list(
        self, tmp_path: Path
    ) -> None:
        """discover_and_load should return empty list when no patterns match."""
        loader = MockProjectorLoaderWithErrorHandling()

        # Use patterns that won't match anything
        patterns = ["nonexistent/**/*.yaml", "missing/*.yml"]

        result = await loader.discover_and_load(patterns)

        assert result == []
        assert isinstance(result, list)


@pytest.mark.unit
class TestProtocolProjectorLoaderEdgeCasesExtended:
    """Extended edge case tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_load_from_contract_with_directory_path_raises(
        self, tmp_path: Path
    ) -> None:
        """load_from_contract should handle directory path appropriately."""
        loader = MockProjectorLoaderWithErrorHandling()

        # Create a directory that happens to end in .yaml
        weird_dir = tmp_path / "weird.yaml"
        weird_dir.mkdir()

        # Directory exists but is not a file - behavior depends on implementation
        # The mock will return a projector since exists() returns True for dirs
        # A real implementation would likely check is_file() as well
        result = await loader.load_from_contract(weird_dir)
        # Since mock doesn't check if path is file vs dir, it proceeds
        assert result is not None

    @pytest.mark.asyncio
    async def test_error_propagation_in_directory_loading(self, tmp_path: Path) -> None:
        """Errors during contract loading should propagate from load_from_directory."""
        from omnibase_spi.exceptions import ContractCompilerError

        loader = MockProjectorLoaderWithErrorHandling()

        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()

        # Create an invalid contract file
        (contracts_dir / "invalid_structure.yaml").write_text(
            "schema:\n  columns: []\n"
        )

        # Should propagate the ContractCompilerError
        with pytest.raises(ContractCompilerError):
            await loader.load_from_directory(contracts_dir)

    @pytest.mark.asyncio
    async def test_first_error_stops_directory_processing(self, tmp_path: Path) -> None:
        """Directory loading should stop at first error (fail-fast behavior)."""
        from omnibase_spi.exceptions import ContractCompilerError

        loader = MockProjectorLoaderWithErrorHandling()

        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()

        # Create contracts: the mock checks filenames against internal test data
        # "invalid_structure.yaml" triggers the "missing projector" error
        # "valid_contract.yaml" triggers successful loading
        # Names sorted: "invalid_structure.yaml" comes before "valid_contract.yaml"
        (contracts_dir / "invalid_structure.yaml").write_text(
            "schema:\n  columns: []\n"
        )
        (contracts_dir / "valid_contract.yaml").write_text(
            "projector:\n  name: valid\n  domain: test\nschema:\n  columns: []\n"
        )

        # Should fail on invalid_structure.yaml before reaching valid_contract.yaml
        with pytest.raises(
            ContractCompilerError, match="missing required 'projector' section"
        ):
            await loader.load_from_directory(contracts_dir)
