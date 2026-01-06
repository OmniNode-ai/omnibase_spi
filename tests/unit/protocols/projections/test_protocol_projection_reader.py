"""
Tests for ProtocolProjectionReader protocol.

Validates that ProtocolProjectionReader:
- Is properly runtime checkable
- Defines required methods (get_entity_state, exists, get_by_criteria)
- Defines registration-specific methods (get_registration_status, get_registered_nodes, get_node_capabilities)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from typing import Any

import pytest

from omnibase_spi.protocols.projections.protocol_projection_reader import (
    ProtocolProjectionReader,
)


class MockProjectionReader:
    """A class that fully implements the ProtocolProjectionReader protocol.

    This mock implementation provides an in-memory projection store for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock reader with empty projections."""
        # Structure: {domain: {entity_id: state_dict}}
        self._projections: dict[str, dict[str, dict[str, Any]]] = {}

    async def get_entity_state(
        self,
        entity_id: str,
        domain: str,
    ) -> dict[str, Any] | None:
        """
        Get the current projected state of an entity.

        Args:
            entity_id: Unique identifier for the entity.
            domain: The domain namespace for the projection.

        Returns:
            Dictionary containing the entity's projected state if found.
            None if the entity does not exist in the projection.
        """
        domain_projections = self._projections.get(domain, {})
        return domain_projections.get(entity_id)

    async def exists(
        self,
        entity_id: str,
        domain: str,
    ) -> bool:
        """
        Check if an entity exists in the projection.

        Args:
            entity_id: Unique identifier for the entity.
            domain: The domain namespace for the projection.

        Returns:
            True if the entity exists in the projection.
            False if the entity does not exist.
        """
        domain_projections = self._projections.get(domain, {})
        return entity_id in domain_projections

    async def get_by_criteria(
        self,
        criteria: dict[str, Any],
        domain: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query entities matching specified criteria.

        Args:
            criteria: Dictionary of field-value pairs to match.
            domain: The domain namespace for the projection.
            limit: Maximum number of results to return.
            offset: Number of results to skip for pagination.

        Returns:
            List of dictionaries containing matching entities' projected state.
        """
        domain_projections = self._projections.get(domain, {})
        results: list[dict[str, Any]] = []

        for entity_id, state in domain_projections.items():
            # Simple criteria matching
            match = all(state.get(key) == value for key, value in criteria.items())
            if match:
                results.append({"entity_id": entity_id, **state})

        # Apply pagination
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]

        return results

    async def get_registration_status(
        self,
        node_id: str,
        domain: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Get the registration status of a specific node.

        Args:
            node_id: Unique identifier for the node.
            domain: Optional domain qualifier for multi-domain registrations.

        Returns:
            Dictionary containing registration state if registered.
            None if the node is not registered.
        """
        effective_domain = domain or "registration"
        return await self.get_entity_state(node_id, effective_domain)

    async def get_registered_nodes(
        self,
        domain: str | None = None,
        state: str | None = None,
        capabilities: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        List registered nodes matching optional filters.

        Args:
            domain: Optional domain filter.
            state: Optional state filter.
            capabilities: Optional list of required capabilities.
            limit: Maximum number of results.

        Returns:
            List of dictionaries containing node registration state.
        """
        effective_domain = domain or "registration"
        criteria: dict[str, Any] = {}

        if state:
            criteria["state"] = state

        results = await self.get_by_criteria(criteria, effective_domain, limit=limit)

        # Filter by capabilities if specified
        if capabilities:
            results = [
                r
                for r in results
                if all(cap in r.get("capabilities", []) for cap in capabilities)
            ]

        return results

    async def get_node_capabilities(
        self,
        node_id: str,
    ) -> list[str] | None:
        """
        Get the capability list for a specific node.

        Args:
            node_id: Unique identifier for the node.

        Returns:
            List of capability strings if registered.
            None if the node is not registered.
        """
        status = await self.get_registration_status(node_id)
        if status is None:
            return None
        return status.get("capabilities", [])

    # Test helper methods
    def add_entity(self, domain: str, entity_id: str, state: dict[str, Any]) -> None:
        """Add an entity to the mock projection for testing."""
        if domain not in self._projections:
            self._projections[domain] = {}
        self._projections[domain][entity_id] = state


class PartialProjectionReader:
    """A class that only implements some ProtocolProjectionReader methods."""

    async def get_entity_state(
        self,
        entity_id: str,
        domain: str,
    ) -> dict[str, Any] | None:
        """Only implement get_entity_state, missing other methods."""
        return None

    async def exists(
        self,
        entity_id: str,
        domain: str,
    ) -> bool:
        """Only implement exists, missing other methods."""
        return False


class NonCompliantReader:
    """A class that implements none of the ProtocolProjectionReader methods."""

    pass


class TestProtocolProjectionReaderProtocol:
    """Test suite for ProtocolProjectionReader protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolProjectionReader should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolProjectionReader, "_is_runtime_protocol") or hasattr(
            ProtocolProjectionReader, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolProjectionReader should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolProjectionReader has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolProjectionReader.__mro__
        )

    def test_protocol_has_get_entity_state_method(self) -> None:
        """ProtocolProjectionReader should define get_entity_state method."""
        assert "get_entity_state" in dir(ProtocolProjectionReader)

    def test_protocol_has_exists_method(self) -> None:
        """ProtocolProjectionReader should define exists method."""
        assert "exists" in dir(ProtocolProjectionReader)

    def test_protocol_has_get_by_criteria_method(self) -> None:
        """ProtocolProjectionReader should define get_by_criteria method."""
        assert "get_by_criteria" in dir(ProtocolProjectionReader)

    def test_protocol_has_get_registration_status_method(self) -> None:
        """ProtocolProjectionReader should define get_registration_status method."""
        assert "get_registration_status" in dir(ProtocolProjectionReader)

    def test_protocol_has_get_registered_nodes_method(self) -> None:
        """ProtocolProjectionReader should define get_registered_nodes method."""
        assert "get_registered_nodes" in dir(ProtocolProjectionReader)

    def test_protocol_has_get_node_capabilities_method(self) -> None:
        """ProtocolProjectionReader should define get_node_capabilities method."""
        assert "get_node_capabilities" in dir(ProtocolProjectionReader)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolProjectionReader protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolProjectionReader()  # type: ignore[misc]


class TestProtocolProjectionReaderCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolProjectionReader methods should pass isinstance check."""
        reader = MockProjectionReader()
        assert isinstance(reader, ProtocolProjectionReader)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolProjectionReader methods should fail isinstance check."""
        reader = PartialProjectionReader()
        assert not isinstance(reader, ProtocolProjectionReader)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolProjectionReader methods should fail isinstance check."""
        reader = NonCompliantReader()
        assert not isinstance(reader, ProtocolProjectionReader)


class TestMockImplementsAllMethods:
    """Test that MockProjectionReader has all required methods."""

    def test_mock_has_get_entity_state(self) -> None:
        """Mock should have get_entity_state method."""
        reader = MockProjectionReader()
        assert hasattr(reader, "get_entity_state")
        assert callable(reader.get_entity_state)

    def test_mock_has_exists(self) -> None:
        """Mock should have exists method."""
        reader = MockProjectionReader()
        assert hasattr(reader, "exists")
        assert callable(reader.exists)

    def test_mock_has_get_by_criteria(self) -> None:
        """Mock should have get_by_criteria method."""
        reader = MockProjectionReader()
        assert hasattr(reader, "get_by_criteria")
        assert callable(reader.get_by_criteria)

    def test_mock_has_get_registration_status(self) -> None:
        """Mock should have get_registration_status method."""
        reader = MockProjectionReader()
        assert hasattr(reader, "get_registration_status")
        assert callable(reader.get_registration_status)

    def test_mock_has_get_registered_nodes(self) -> None:
        """Mock should have get_registered_nodes method."""
        reader = MockProjectionReader()
        assert hasattr(reader, "get_registered_nodes")
        assert callable(reader.get_registered_nodes)

    def test_mock_has_get_node_capabilities(self) -> None:
        """Mock should have get_node_capabilities method."""
        reader = MockProjectionReader()
        assert hasattr(reader, "get_node_capabilities")
        assert callable(reader.get_node_capabilities)


class TestProtocolProjectionReaderAsyncNature:
    """Test that ProtocolProjectionReader methods are async."""

    def test_get_entity_state_is_async(self) -> None:
        """get_entity_state should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectionReader.get_entity_state)

    def test_exists_is_async(self) -> None:
        """exists should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectionReader.exists)

    def test_get_by_criteria_is_async(self) -> None:
        """get_by_criteria should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectionReader.get_by_criteria)

    def test_get_registration_status_is_async(self) -> None:
        """get_registration_status should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectionReader.get_registration_status)

    def test_get_registered_nodes_is_async(self) -> None:
        """get_registered_nodes should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectionReader.get_registered_nodes)

    def test_get_node_capabilities_is_async(self) -> None:
        """get_node_capabilities should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjectionReader.get_node_capabilities)


class TestProtocolProjectionReaderMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    @pytest.mark.asyncio
    async def test_get_entity_state_returns_dict_or_none(self) -> None:
        """get_entity_state should return dict or None."""
        reader = MockProjectionReader()
        entity_id = "test-entity-1"
        domain = "test-domain"

        # Non-existent entity returns None
        result = await reader.get_entity_state(entity_id, domain)
        assert result is None

        # Existing entity returns dict
        reader.add_entity(domain, entity_id, {"state": "active"})
        result = await reader.get_entity_state(entity_id, domain)
        assert isinstance(result, dict)
        assert result.get("state") == "active"

    @pytest.mark.asyncio
    async def test_exists_returns_bool(self) -> None:
        """exists should return bool."""
        reader = MockProjectionReader()
        entity_id = "test-entity-1"
        domain = "test-domain"

        # Non-existent entity returns False
        result = await reader.exists(entity_id, domain)
        assert result is False

        # Existing entity returns True
        reader.add_entity(domain, entity_id, {"state": "active"})
        result = await reader.exists(entity_id, domain)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_by_criteria_returns_list(self) -> None:
        """get_by_criteria should return list of dicts."""
        reader = MockProjectionReader()
        domain = "test-domain"

        # Empty projection returns empty list
        result = await reader.get_by_criteria({"state": "active"}, domain)
        assert isinstance(result, list)
        assert len(result) == 0

        # Add some entities
        reader.add_entity(domain, "entity-1", {"state": "active", "name": "one"})
        reader.add_entity(domain, "entity-2", {"state": "active", "name": "two"})
        reader.add_entity(domain, "entity-3", {"state": "inactive", "name": "three"})

        # Filter by state
        result = await reader.get_by_criteria({"state": "active"}, domain)
        assert len(result) == 2
        assert all(r["state"] == "active" for r in result)

    @pytest.mark.asyncio
    async def test_get_by_criteria_with_pagination(self) -> None:
        """get_by_criteria should support limit and offset."""
        reader = MockProjectionReader()
        domain = "test-domain"

        # Add entities
        for i in range(10):
            reader.add_entity(domain, f"entity-{i}", {"state": "active", "index": i})

        # Test limit
        result = await reader.get_by_criteria({"state": "active"}, domain, limit=3)
        assert len(result) == 3

        # Test offset
        result = await reader.get_by_criteria(
            {"state": "active"}, domain, limit=3, offset=2
        )
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_registration_status_returns_dict_or_none(self) -> None:
        """get_registration_status should return dict or None."""
        reader = MockProjectionReader()
        node_id = "test-node-1"

        # Non-existent node returns None
        result = await reader.get_registration_status(node_id)
        assert result is None

        # Registered node returns dict
        reader.add_entity(
            "registration",
            node_id,
            {"state": "active", "capabilities": ["compute"]},
        )
        result = await reader.get_registration_status(node_id)
        assert isinstance(result, dict)
        assert result.get("state") == "active"

    @pytest.mark.asyncio
    async def test_get_registration_status_with_domain(self) -> None:
        """get_registration_status should respect domain parameter."""
        reader = MockProjectionReader()
        node_id = "test-node-1"

        # Add to specific domain
        reader.add_entity("compute", node_id, {"state": "active"})

        # Default domain returns None
        result = await reader.get_registration_status(node_id)
        assert result is None

        # Specific domain returns state
        result = await reader.get_registration_status(node_id, domain="compute")
        assert result is not None
        assert result.get("state") == "active"

    @pytest.mark.asyncio
    async def test_get_registered_nodes_returns_list(self) -> None:
        """get_registered_nodes should return list of dicts."""
        reader = MockProjectionReader()

        # Empty returns empty list
        result = await reader.get_registered_nodes()
        assert isinstance(result, list)
        assert len(result) == 0

        # Add some nodes
        reader.add_entity(
            "registration",
            "node-1",
            {"state": "active", "capabilities": ["compute", "gpu"]},
        )
        reader.add_entity(
            "registration",
            "node-2",
            {"state": "active", "capabilities": ["compute"]},
        )
        reader.add_entity(
            "registration",
            "node-3",
            {"state": "inactive", "capabilities": ["compute"]},
        )

        # Get all
        result = await reader.get_registered_nodes()
        assert len(result) == 3

        # Filter by state
        result = await reader.get_registered_nodes(state="active")
        assert len(result) == 2

        # Filter by capabilities
        result = await reader.get_registered_nodes(capabilities=["gpu"])
        assert len(result) == 1
        assert result[0]["entity_id"] == "node-1"

    @pytest.mark.asyncio
    async def test_get_node_capabilities_returns_list_or_none(self) -> None:
        """get_node_capabilities should return list of strings or None."""
        reader = MockProjectionReader()
        node_id = "test-node-1"

        # Non-existent node returns None
        result = await reader.get_node_capabilities(node_id)
        assert result is None

        # Registered node returns list
        reader.add_entity(
            "registration",
            node_id,
            {"state": "active", "capabilities": ["compute", "gpu", "cuda-12"]},
        )
        result = await reader.get_node_capabilities(node_id)
        assert isinstance(result, list)
        assert "compute" in result
        assert "gpu" in result
        assert "cuda-12" in result


class TestProtocolProjectionReaderImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_projection_reader module."""
        from omnibase_spi.protocols.projections.protocol_projection_reader import (
            ProtocolProjectionReader as DirectProtocolProjectionReader,
        )

        reader = MockProjectionReader()
        assert isinstance(reader, DirectProtocolProjectionReader)

    def test_import_from_projections_package(self) -> None:
        """Test import from projections package."""
        from omnibase_spi.protocols.projections import (
            ProtocolProjectionReader as ProjectionsProtocolProjectionReader,
        )

        reader = MockProjectionReader()
        assert isinstance(reader, ProjectionsProtocolProjectionReader)

    def test_import_from_protocols_package(self) -> None:
        """Test import from protocols root package."""
        from omnibase_spi.protocols import (
            ProtocolProjectionReader as ProtocolsProjectionReader,
        )

        reader = MockProjectionReader()
        assert isinstance(reader, ProtocolsProjectionReader)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols import (
            ProtocolProjectionReader as ProtocolsProjectionReader,
        )
        from omnibase_spi.protocols.projections import (
            ProtocolProjectionReader as ProjectionsProtocolProjectionReader,
        )
        from omnibase_spi.protocols.projections.protocol_projection_reader import (
            ProtocolProjectionReader as DirectProtocolProjectionReader,
        )

        assert DirectProtocolProjectionReader is ProjectionsProtocolProjectionReader
        assert ProjectionsProtocolProjectionReader is ProtocolsProjectionReader


class TestProtocolProjectionReaderDocumentation:
    """Test that ProtocolProjectionReader has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolProjectionReader should have a docstring."""
        assert ProtocolProjectionReader.__doc__ is not None
        assert len(ProtocolProjectionReader.__doc__.strip()) > 0

    def test_docstring_mentions_no_topic_scanning(self) -> None:
        """Docstring should document the no topic scanning constraint."""
        assert ProtocolProjectionReader.__doc__ is not None
        docstring = ProtocolProjectionReader.__doc__.lower()
        assert "topic" in docstring or "scan" in docstring

    def test_mock_get_entity_state_has_docstring(self) -> None:
        """get_entity_state method should have a docstring."""
        assert MockProjectionReader.get_entity_state.__doc__ is not None

    def test_mock_exists_has_docstring(self) -> None:
        """exists method should have a docstring."""
        assert MockProjectionReader.exists.__doc__ is not None

    def test_mock_get_by_criteria_has_docstring(self) -> None:
        """get_by_criteria method should have a docstring."""
        assert MockProjectionReader.get_by_criteria.__doc__ is not None

    def test_mock_get_registration_status_has_docstring(self) -> None:
        """get_registration_status method should have a docstring."""
        assert MockProjectionReader.get_registration_status.__doc__ is not None

    def test_mock_get_registered_nodes_has_docstring(self) -> None:
        """get_registered_nodes method should have a docstring."""
        assert MockProjectionReader.get_registered_nodes.__doc__ is not None

    def test_mock_get_node_capabilities_has_docstring(self) -> None:
        """get_node_capabilities method should have a docstring."""
        assert MockProjectionReader.get_node_capabilities.__doc__ is not None


class TestArchitecturalConstraintDocumentation:
    """Test that the no-topic-scanning constraint is properly documented."""

    def test_module_docstring_mentions_constraint(self) -> None:
        """Module docstring should mention the no topic scanning constraint."""
        import omnibase_spi.protocols.projections.protocol_projection_reader as module

        assert module.__doc__ is not None
        docstring = module.__doc__.lower()
        assert "never" in docstring or "must not" in docstring
        assert "topic" in docstring or "scan" in docstring

    def test_protocol_docstring_mentions_constraint(self) -> None:
        """Protocol class docstring should emphasize the constraint."""
        assert ProtocolProjectionReader.__doc__ is not None
        docstring = ProtocolProjectionReader.__doc__
        # Check for CRITICAL CONSTRAINT section
        assert "CRITICAL" in docstring or "NEVER" in docstring
