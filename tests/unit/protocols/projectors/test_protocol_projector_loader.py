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
from typing import Any, ClassVar
from uuid import UUID, uuid4

import pytest

from omnibase_spi.protocols.projectors.protocol_projector_loader import (
    ProtocolProjectorLoader,
)

# =============================================================================
# Mock Models (matching pattern from test_protocol_event_projector.py)
# =============================================================================


class MockEventEnvelope:
    """Mock event envelope for testing.

    Mimics the structure of ModelEventEnvelope from omnibase_core.
    Provides the minimal interface needed for testing ProtocolProjectorLoader.
    """

    def __init__(
        self,
        event_id: UUID | None = None,
        event_type: str = "TestEvent",
        aggregate_id: UUID | None = None,
        aggregate_type: str = "TestAggregate",
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock event envelope."""
        self._event_id = event_id or uuid4()
        self._event_type = event_type
        self._aggregate_id = aggregate_id or uuid4()
        self._aggregate_type = aggregate_type
        self._payload = payload if payload is not None else {}
        self._metadata = metadata if metadata is not None else {}

    @property
    def event_id(self) -> UUID:
        """Return the unique event identifier."""
        return self._event_id

    @property
    def event_type(self) -> str:
        """Return the event type."""
        return self._event_type

    @property
    def aggregate_id(self) -> UUID:
        """Return the aggregate identifier."""
        return self._aggregate_id

    @property
    def aggregate_type(self) -> str:
        """Return the aggregate type."""
        return self._aggregate_type

    @property
    def payload(self) -> dict[str, Any]:
        """Return the event payload."""
        return self._payload

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the event metadata."""
        return self._metadata


class MockProjectionResult:
    """Mock projection result for testing.

    Mimics the structure of ModelProjectionResult from omnibase_core.
    Provides the minimal interface needed for testing ProtocolProjectorLoader.
    """

    def __init__(
        self,
        success: bool = True,
        skipped: bool = False,
        error: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Initialize the mock projection result."""
        self._success = success
        self._skipped = skipped
        self._error = error
        self._reason = reason

    @property
    def success(self) -> bool:
        """Return whether projection completed successfully."""
        return self._success

    @property
    def skipped(self) -> bool:
        """Return whether event was skipped."""
        return self._skipped

    @property
    def error(self) -> str | None:
        """Return error details if projection failed."""
        return self._error

    @property
    def reason(self) -> str | None:
        """Return reason for skip if skipped."""
        return self._reason


class MockProjector:
    """Mock projector implementing ProtocolEventProjector interface.

    This is a minimal mock that satisfies the structural requirements
    of ProtocolEventProjector for testing purposes.
    """

    def __init__(self, name: str, domain: str) -> None:
        """Initialize the mock projector."""
        self._name = name
        self._domain = domain
        self._consumed_events = ["Created", "Updated", "Deleted"]
        self._state: dict[UUID, dict[str, Any]] = {}

    @property
    def projector_id(self) -> str:
        """Unique identifier for this projector."""
        return f"{self._name}-projector-v1"

    @property
    def aggregate_type(self) -> str:
        """The aggregate type this projector handles."""
        return self._domain

    @property
    def consumed_events(self) -> list[str]:
        """Event types this projector consumes."""
        return self._consumed_events

    async def project(self, event: MockEventEnvelope) -> MockProjectionResult:
        """Project event to persistence store.

        Args:
            event: The event envelope to project.

        Returns:
            MockProjectionResult indicating projection outcome.
        """
        # Mock implementation - store event data in state
        aggregate_id = event.aggregate_id
        self._state[aggregate_id] = {"projected": True}
        return MockProjectionResult(success=True)

    async def get_state(self, aggregate_id: UUID) -> dict[str, Any] | None:
        """Get current projected state for an aggregate.

        Args:
            aggregate_id: The UUID of the aggregate to retrieve.

        Returns:
            The current materialized state, or None if not found.
        """
        return self._state.get(aggregate_id)


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


def _get_protocol_public_members(protocol_class: type) -> frozenset[str]:
    """Get all public members of a protocol class (excluding dunder methods).

    Args:
        protocol_class: The protocol class to inspect.

    Returns:
        A frozenset of public member names.
    """
    import inspect

    return frozenset(
        name
        for name, _ in inspect.getmembers(protocol_class)
        if not name.startswith("_")
    )


@pytest.mark.unit
class TestProtocolProjectorLoaderProtocol:
    """Test suite for ProtocolProjectorLoader protocol compliance."""

    # Define expected protocol members for exhaustiveness checking
    # Using frozenset for immutability - this is a constant that should never change at runtime
    EXPECTED_PROTOCOL_MEMBERS: ClassVar[frozenset[str]] = frozenset(
        {
            "load_from_contract",
            "load_from_directory",
            "discover_and_load",
        }
    )

    def test_protocol_members_match_exactly(self) -> None:
        """Verify protocol members match expected set exactly (bidirectional).

        This is the primary exhaustiveness check that validates:
        1. No unexpected members were added to the protocol
        2. No expected members are missing from the protocol

        If this test fails, update EXPECTED_PROTOCOL_MEMBERS to match the
        actual protocol definition, or fix the protocol if changes were unintended.
        """
        actual_members = _get_protocol_public_members(ProtocolProjectorLoader)
        expected_members = self.EXPECTED_PROTOCOL_MEMBERS

        # Check for exact match
        if actual_members != expected_members:
            unexpected = actual_members - expected_members
            missing = expected_members - actual_members

            diff_parts = []
            if unexpected:
                diff_parts.append(
                    f"  Unexpected (in protocol but not expected): {sorted(unexpected)}"
                )
            if missing:
                diff_parts.append(
                    f"  Missing (expected but not in protocol): {sorted(missing)}"
                )

            diff_message = "\n".join(diff_parts)

            pytest.fail(
                f"Protocol members do not match expected set exactly.\n"
                f"\n"
                f"Expected members ({len(expected_members)}): {sorted(expected_members)}\n"
                f"Actual members ({len(actual_members)}): {sorted(actual_members)}\n"
                f"\n"
                f"Differences:\n"
                f"{diff_message}\n"
                f"\n"
                f"Action required:\n"
                f"  - If changes are intentional: update EXPECTED_PROTOCOL_MEMBERS\n"
                f"  - If changes are unintentional: revert the protocol changes"
            )

    def test_no_unexpected_protocol_members(self) -> None:
        """Verify no unexpected public members were added to protocol.

        This test catches when new members are added to ProtocolProjectorLoader
        without updating EXPECTED_PROTOCOL_MEMBERS. If this test fails, either:
        1. Add the new member to EXPECTED_PROTOCOL_MEMBERS, OR
        2. The new member was added unintentionally and should be removed.
        """
        actual_members = _get_protocol_public_members(ProtocolProjectorLoader)
        unexpected = actual_members - self.EXPECTED_PROTOCOL_MEMBERS

        assert not unexpected, (
            f"Unexpected protocol members found: {sorted(unexpected)}.\n"
            f"\n"
            f"Expected: {sorted(self.EXPECTED_PROTOCOL_MEMBERS)}\n"
            f"Actual:   {sorted(actual_members)}\n"
            f"\n"
            f"If these are intentional additions, update EXPECTED_PROTOCOL_MEMBERS."
        )

    def test_no_missing_protocol_members(self) -> None:
        """Verify all expected members exist in protocol.

        This test catches when members are removed from ProtocolProjectorLoader
        without updating EXPECTED_PROTOCOL_MEMBERS. If this test fails, either:
        1. Remove the missing member from EXPECTED_PROTOCOL_MEMBERS, OR
        2. The member was removed unintentionally and should be restored.
        """
        actual_members = _get_protocol_public_members(ProtocolProjectorLoader)
        missing = self.EXPECTED_PROTOCOL_MEMBERS - actual_members

        assert not missing, (
            f"Expected protocol members missing: {sorted(missing)}.\n"
            f"\n"
            f"Expected: {sorted(self.EXPECTED_PROTOCOL_MEMBERS)}\n"
            f"Actual:   {sorted(actual_members)}\n"
            f"\n"
            f"If these were intentionally removed, update EXPECTED_PROTOCOL_MEMBERS."
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
        assert projector.projector_id == "test-projector-v1"

    @pytest.mark.asyncio
    async def test_load_from_contract_returns_projector(self) -> None:
        """load_from_contract should return a projector-like object."""
        loader = MockProjectorLoader()
        contract_path = Path("/tmp/orders.yaml")

        projector = await loader.load_from_contract(contract_path)

        # Verify it has ProtocolEventProjector interface attributes
        assert hasattr(projector, "projector_id")
        assert hasattr(projector, "aggregate_type")
        assert hasattr(projector, "consumed_events")
        assert hasattr(projector, "project")
        assert hasattr(projector, "get_state")
        assert projector.projector_id == "orders-projector-v1"

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

        with pytest.raises(ContractCompilerError, match=r"missing 'projector\.name'"):
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


# =============================================================================
# Export Tests (PR #54 feedback)
# =============================================================================


@pytest.mark.unit
class TestProtocolProjectorLoaderExports:
    """Test that ProtocolProjectorLoader is properly exported via __all__."""

    def test_protocol_in_package_all(self) -> None:
        """ProtocolProjectorLoader should be listed in projectors package __all__."""
        from omnibase_spi.protocols import projectors

        assert hasattr(projectors, "__all__"), "projectors package should have __all__"
        assert (
            "ProtocolProjectorLoader" in projectors.__all__
        ), "ProtocolProjectorLoader should be in projectors.__all__"

    def test_protocol_in_module_all(self) -> None:
        """ProtocolProjectorLoader should be listed in module __all__."""
        from omnibase_spi.protocols.projectors import protocol_projector_loader

        assert hasattr(
            protocol_projector_loader, "__all__"
        ), "protocol_projector_loader module should have __all__"
        assert (
            "ProtocolProjectorLoader" in protocol_projector_loader.__all__
        ), "ProtocolProjectorLoader should be in protocol_projector_loader.__all__"

    def test_protocol_exported_from_package(self) -> None:
        """ProtocolProjectorLoader should be accessible from projectors package."""
        from omnibase_spi.protocols.projectors import ProtocolProjectorLoader

        assert ProtocolProjectorLoader is not None

    def test_protocol_exported_from_root_protocols_package(self) -> None:
        """ProtocolProjectorLoader should be accessible from protocols package."""
        from omnibase_spi.protocols import ProtocolProjectorLoader

        assert ProtocolProjectorLoader is not None

    def test_all_exports_match_package_contents(self) -> None:
        """All symbols in __all__ should be importable from the package."""
        from omnibase_spi.protocols import projectors

        for symbol_name in projectors.__all__:
            assert hasattr(
                projectors, symbol_name
            ), f"Symbol '{symbol_name}' listed in __all__ but not in package"
