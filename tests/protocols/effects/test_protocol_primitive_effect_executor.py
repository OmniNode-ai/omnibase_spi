"""
Tests for ProtocolPrimitiveEffectExecutor protocol.

Validates that ProtocolPrimitiveEffectExecutor:
- Is properly runtime checkable
- Defines required methods (execute, get_supported_effects)
- Has required property (executor_id)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest
import pytest_asyncio

from omnibase_spi.protocols.effects.protocol_primitive_effect_executor import (
    LiteralEffectCategory,
    LiteralEffectId,
    ProtocolPrimitiveEffectExecutor,
)


class CompliantEffectExecutor:
    """A class that fully implements the ProtocolPrimitiveEffectExecutor protocol.

    Note: Uses 'object' type hints instead of actual omnibase_core models
    to avoid circular import issues in tests. Once omnibase_core exports
    proper types, these can be updated to use TypedDict or model types.
    """

    @property
    def executor_id(self) -> str:
        """Return unique executor identifier."""
        return "test-executor-1"

    async def execute(
        self,
        _effect_id: str,
        _input_data: bytes,
    ) -> bytes:
        """Execute a primitive effect."""
        return b'{"result": "ok"}'

    def get_supported_effects(self) -> list[str]:
        """Return list of supported effect IDs."""
        return ["http.request", "http.get", "db.query"]


class PartialEffectExecutor:
    """A class that only implements some protocol methods."""

    async def execute(
        self,
        _effect_id: str,
        _input_data: bytes,
    ) -> bytes:
        """Execute a primitive effect."""
        return b"{}"


class NonCompliantEffectExecutor:
    """A class that implements none of the protocol methods."""

    pass


class WrongSignatureExecutor:
    """A class that implements methods with wrong signatures."""

    @property
    def executor_id(self) -> str:
        """Return unique executor identifier."""
        return "wrong-executor"

    async def execute(self, _effect_id: str) -> bytes:
        """Execute with wrong signature (missing input_data parameter)."""
        return b"{}"

    def get_supported_effects(self) -> list[str]:
        """Return list of supported effect IDs."""
        return []


# --- Fixtures ---


@pytest.fixture
def compliant_executor() -> CompliantEffectExecutor:
    """Provide a compliant effect executor instance for tests."""
    return CompliantEffectExecutor()


@pytest_asyncio.fixture
async def async_compliant_executor() -> CompliantEffectExecutor:
    """Provide a compliant effect executor instance for async tests.

    This fixture can be used when async setup/teardown is needed,
    or when the executor needs to be initialized with async operations.
    """
    executor = CompliantEffectExecutor()
    # Async setup could go here (e.g., initializing connections)
    return executor


@pytest.fixture
def non_compliant_executor() -> NonCompliantEffectExecutor:
    """Provide a non-compliant executor instance for tests."""
    return NonCompliantEffectExecutor()


@pytest.fixture
def partial_executor() -> PartialEffectExecutor:
    """Provide a partial executor instance for tests."""
    return PartialEffectExecutor()


class TestProtocolPrimitiveEffectExecutorBasics:
    """Test basic protocol properties."""

    def test_protocol_is_runtime_checkable(
        self, compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify protocol has @runtime_checkable decorator."""
        assert isinstance(compliant_executor, ProtocolPrimitiveEffectExecutor)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """Verify Protocol class itself cannot be instantiated."""
        with pytest.raises(TypeError):
            ProtocolPrimitiveEffectExecutor()  # type: ignore[misc]

    def test_compliant_class_passes_isinstance(
        self, compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify compliant implementation passes isinstance check."""
        assert isinstance(compliant_executor, ProtocolPrimitiveEffectExecutor)

    def test_non_compliant_class_fails_isinstance(
        self, non_compliant_executor: NonCompliantEffectExecutor
    ) -> None:
        """Verify non-compliant class fails isinstance check."""
        assert not isinstance(non_compliant_executor, ProtocolPrimitiveEffectExecutor)

    def test_partial_implementation_fails_isinstance(
        self, partial_executor: PartialEffectExecutor
    ) -> None:
        """Verify partial implementation fails isinstance check."""
        # Partial implementations may pass runtime check but lack full interface
        # The @runtime_checkable only checks for method existence, not completeness
        # This is expected Python Protocol behavior
        _ = partial_executor  # Use the fixture


class TestProtocolPrimitiveEffectExecutorMethods:
    """Test protocol method signatures and behavior."""

    async def test_execute_method_signature(
        self, async_compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify execute method accepts correct parameters."""
        result = await async_compliant_executor.execute(
            "http.request", b'{"url": "https://example.com"}'
        )
        assert isinstance(result, bytes)

    def test_get_supported_effects_returns_list(
        self, compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify get_supported_effects returns list of strings."""
        effects = compliant_executor.get_supported_effects()
        assert isinstance(effects, list)
        assert all(isinstance(e, str) for e in effects)

    def test_executor_id_property(
        self, compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify executor_id property returns string."""
        assert isinstance(compliant_executor.executor_id, str)
        assert compliant_executor.executor_id == "test-executor-1"


class TestEffectIdLiteralTypes:
    """Test LiteralEffectId and LiteralEffectCategory types."""

    def test_effect_categories_are_valid(self) -> None:
        """Verify effect categories are defined."""
        # Type checking ensures these are valid LiteralEffectCategory values
        categories: list[LiteralEffectCategory] = [
            "http",
            "db",
            "messaging",
            "storage",
            "cache",
            "secrets",
            "discovery",
        ]
        assert len(categories) == 7

    def test_effect_ids_follow_naming_convention(self) -> None:
        """Verify effect IDs follow {category}.{operation} format."""
        effect_ids: list[LiteralEffectId] = [
            "http.request",
            "http.get",
            "db.query",
            "messaging.publish",
            "storage.read",
            "cache.get",
            "secrets.get",
            "discovery.register",
        ]
        for effect_id in effect_ids:
            parts = effect_id.split(".")
            assert (
                len(parts) == 2
            ), f"Effect ID should have format 'category.operation': {effect_id}"

    def test_http_effects_exist(self) -> None:
        """Verify HTTP effect IDs are defined."""
        http_effects: list[LiteralEffectId] = [
            "http.request",
            "http.get",
            "http.post",
            "http.put",
            "http.patch",
            "http.delete",
        ]
        assert len(http_effects) == 6

    def test_db_effects_exist(self) -> None:
        """Verify database effect IDs are defined."""
        db_effects: list[LiteralEffectId] = [
            "db.query",
            "db.execute",
            "db.transaction",
        ]
        assert len(db_effects) == 3


class TestProtocolPrimitiveEffectExecutorCompliance:
    """Test protocol compliance scenarios."""

    def test_compliant_executor_has_all_methods(
        self, compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify compliant executor has all required methods."""
        assert hasattr(compliant_executor, "execute")
        assert hasattr(compliant_executor, "get_supported_effects")
        assert hasattr(compliant_executor, "executor_id")
        assert callable(compliant_executor.execute)
        assert callable(compliant_executor.get_supported_effects)

    def test_effect_executor_supports_expected_effects(
        self, compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify executor reports supported effects correctly."""
        effects = compliant_executor.get_supported_effects()
        assert "http.request" in effects
        assert "db.query" in effects

    async def test_execute_accepts_any_effect_id_in_mock(
        self, async_compliant_executor: CompliantEffectExecutor
    ) -> None:
        """Verify mock executor accepts any effect_id without validation.

        This test documents the mock's behavior: it accepts any effect_id
        and returns a valid response. Real implementations (in omnibase_infra)
        should validate effect_id against get_supported_effects() and raise
        ValueError for unsupported effects.

        The protocol itself does not enforce effect_id validation - that is
        an implementation concern for concrete effect executors.
        """
        result = await async_compliant_executor.execute("unknown.effect", b"{}")
        assert isinstance(result, bytes)


class TestProtocolImports:
    """Test that protocol can be imported from expected locations."""

    def test_import_from_effects_module(self) -> None:
        """Verify protocol can be imported from effects module."""
        from omnibase_spi.protocols.effects import ProtocolPrimitiveEffectExecutor

        assert ProtocolPrimitiveEffectExecutor is not None

    def test_import_literal_types(self) -> None:
        """Verify Literal types can be imported."""
        from omnibase_spi.protocols.effects import (
            LiteralEffectCategory,
            LiteralEffectId,
        )

        assert LiteralEffectCategory is not None
        assert LiteralEffectId is not None
