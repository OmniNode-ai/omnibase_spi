"""
Tests for ProtocolRegistryBase[K, V] generic protocol.

Validates that ProtocolRegistryBase:
- Is properly runtime checkable
- Works with Generic type parameters (str→type, int→str, tuple→dict, etc.)
- Defines required methods (register, get, list_keys, is_registered, unregister)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
- Handles error conditions (KeyError, etc.)
- Maintains invariants (register→is_registered, unregister→not is_registered)
"""

import pytest

from omnibase_spi.protocols.registry.protocol_registry_base import (
    ProtocolRegistryBase,
)


class MockService:
    """Mock service class for testing."""

    def __init__(self, name: str = "mock"):
        """Initialize mock service."""
        self.name = name


class ConcreteStringRegistry:
    """Simple registry implementation with str→type mapping for testing."""

    def __init__(self) -> None:
        """Initialize registry with empty storage."""
        self._registry: dict[str, type] = {}

    def register(self, key: str, value: type) -> None:
        """Register a key-value pair."""
        self._registry[key] = value

    def get(self, key: str) -> type:
        """Get value for key."""
        if key not in self._registry:
            raise KeyError(f"Key not registered: {key}")
        return self._registry[key]

    def list_keys(self) -> list[str]:
        """List all registered keys."""
        return list(self._registry.keys())

    def is_registered(self, key: str) -> bool:
        """Check if key is registered."""
        return key in self._registry

    def unregister(self, key: str) -> bool:
        """Unregister a key."""
        if key in self._registry:
            del self._registry[key]
            return True
        return False


class ConcreteIntRegistry:
    """Registry implementation with int→str mapping for testing type parameters."""

    def __init__(self) -> None:
        """Initialize registry with empty storage."""
        self._registry: dict[int, str] = {}

    def register(self, key: int, value: str) -> None:
        """Register a key-value pair."""
        self._registry[key] = value

    def get(self, key: int) -> str:
        """Get value for key."""
        if key not in self._registry:
            raise KeyError(f"Key not registered: {key}")
        return self._registry[key]

    def list_keys(self) -> list[int]:
        """List all registered keys."""
        return list(self._registry.keys())

    def is_registered(self, key: int) -> bool:
        """Check if key is registered."""
        return key in self._registry

    def unregister(self, key: int) -> bool:
        """Unregister a key."""
        if key in self._registry:
            del self._registry[key]
            return True
        return False


class ConcreteTupleRegistry:
    """Registry implementation with tuple→dict mapping for complex type parameters."""

    def __init__(self) -> None:
        """Initialize registry with empty storage."""
        self._registry: dict[tuple[str, int], dict[str, str]] = {}

    def register(self, key: tuple[str, int], value: dict[str, str]) -> None:
        """Register a key-value pair."""
        self._registry[key] = value

    def get(self, key: tuple[str, int]) -> dict[str, str]:
        """Get value for key."""
        if key not in self._registry:
            raise KeyError(f"Key not registered: {key}")
        return self._registry[key]

    def list_keys(self) -> list[tuple[str, int]]:
        """List all registered keys."""
        return list(self._registry.keys())

    def is_registered(self, key: tuple[str, int]) -> bool:
        """Check if key is registered."""
        return key in self._registry

    def unregister(self, key: tuple[str, int]) -> bool:
        """Unregister a key."""
        if key in self._registry:
            del self._registry[key]
            return True
        return False


class PartialRegistry:
    """A class that only implements some ProtocolRegistryBase methods."""

    def register(self, key: str, value: type) -> None:
        """Register a key-value pair."""
        pass

    def get(self, key: str) -> type:
        """Get value for key."""
        return MockService


class NonCompliantRegistry:
    """A class that implements none of the ProtocolRegistryBase methods."""

    pass


class WrongSignatureRegistry:
    """A class that implements methods with wrong signatures."""

    def register(self, key: str) -> None:  # Missing value parameter
        """Register a key-value pair."""
        pass

    def get(self, key: str) -> type:
        """Get value for key."""
        return MockService

    def list_keys(self) -> list[str]:
        """List all registered keys."""
        return []

    def is_registered(self, key: str) -> bool:
        """Check if key is registered."""
        return False

    def unregister(self, key: str) -> bool:
        """Unregister a key."""
        return False


class TestProtocolRegistryBaseProtocol:
    """Test suite for ProtocolRegistryBase protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolRegistryBase should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolRegistryBase, "_is_runtime_protocol") or hasattr(
            ProtocolRegistryBase, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolRegistryBase should be a Protocol class."""
        # Check that ProtocolRegistryBase has Protocol in its bases
        assert any(
            base.__name__ == "Protocol" for base in ProtocolRegistryBase.__mro__
        )

    def test_protocol_has_register_method(self) -> None:
        """ProtocolRegistryBase should define register method."""
        assert "register" in dir(ProtocolRegistryBase)

    def test_protocol_has_get_method(self) -> None:
        """ProtocolRegistryBase should define get method."""
        assert "get" in dir(ProtocolRegistryBase)

    def test_protocol_has_list_keys_method(self) -> None:
        """ProtocolRegistryBase should define list_keys method."""
        assert "list_keys" in dir(ProtocolRegistryBase)

    def test_protocol_has_is_registered_method(self) -> None:
        """ProtocolRegistryBase should define is_registered method."""
        assert "is_registered" in dir(ProtocolRegistryBase)

    def test_protocol_has_unregister_method(self) -> None:
        """ProtocolRegistryBase should define unregister method."""
        assert "unregister" in dir(ProtocolRegistryBase)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolRegistryBase protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolRegistryBase()  # type: ignore[misc]


class TestProtocolRegistryBaseCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_string_registry_passes_isinstance(self) -> None:
        """A class implementing all ProtocolRegistryBase methods should pass isinstance check."""
        registry = ConcreteStringRegistry()
        assert isinstance(registry, ProtocolRegistryBase)

    def test_compliant_int_registry_passes_isinstance(self) -> None:
        """A registry with different type parameters should pass isinstance check."""
        registry = ConcreteIntRegistry()
        assert isinstance(registry, ProtocolRegistryBase)

    def test_compliant_tuple_registry_passes_isinstance(self) -> None:
        """A registry with complex type parameters should pass isinstance check."""
        registry = ConcreteTupleRegistry()
        assert isinstance(registry, ProtocolRegistryBase)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolRegistryBase methods should fail isinstance check."""
        registry = PartialRegistry()
        assert not isinstance(registry, ProtocolRegistryBase)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolRegistryBase methods should fail isinstance check."""
        registry = NonCompliantRegistry()
        assert not isinstance(registry, ProtocolRegistryBase)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with methods of wrong signatures still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Type checking is enforced by static analysis tools.
        """
        registry = WrongSignatureRegistry()
        # Runtime check passes because methods exist
        assert isinstance(registry, ProtocolRegistryBase)


class TestProtocolRegistryBaseGenericTypes:
    """Test generic type parameter support."""

    def test_string_to_type_mapping(self) -> None:
        """Test registry with str→type mapping."""
        registry: ProtocolRegistryBase[str, type] = ConcreteStringRegistry()

        registry.register("service_a", MockService)
        registry.register("service_b", type)

        assert registry.get("service_a") is MockService
        assert registry.get("service_b") is type
        assert registry.is_registered("service_a")
        assert registry.is_registered("service_b")

    def test_int_to_string_mapping(self) -> None:
        """Test registry with int→str mapping."""
        registry: ProtocolRegistryBase[int, str] = ConcreteIntRegistry()

        registry.register(1, "first")
        registry.register(2, "second")

        assert registry.get(1) == "first"
        assert registry.get(2) == "second"
        assert registry.is_registered(1)
        assert registry.is_registered(2)

    def test_tuple_to_dict_mapping(self) -> None:
        """Test registry with tuple→dict mapping."""
        registry: ProtocolRegistryBase[
            tuple[str, int], dict[str, str]
        ] = ConcreteTupleRegistry()

        key1 = ("alpha", 1)
        key2 = ("beta", 2)
        value1 = {"name": "first", "type": "alpha"}
        value2 = {"name": "second", "type": "beta"}

        registry.register(key1, value1)
        registry.register(key2, value2)

        assert registry.get(key1) == value1
        assert registry.get(key2) == value2
        assert registry.is_registered(key1)
        assert registry.is_registered(key2)


class TestProtocolRegistryBaseCoreMethods:
    """Test core method behavior."""

    def test_register_and_get(self) -> None:
        """Test register and get operations."""
        registry = ConcreteStringRegistry()

        registry.register("key1", MockService)
        assert registry.get("key1") is MockService

    def test_list_keys_empty_registry(self) -> None:
        """Test list_keys on empty registry."""
        registry = ConcreteStringRegistry()
        assert registry.list_keys() == []

    def test_list_keys_single_item(self) -> None:
        """Test list_keys with single item."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)

        keys = registry.list_keys()
        assert len(keys) == 1
        assert "key1" in keys

    def test_list_keys_multiple_items(self) -> None:
        """Test list_keys with multiple items."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)
        registry.register("key2", type)
        registry.register("key3", str)

        keys = registry.list_keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

    def test_is_registered_returns_false_for_missing_key(self) -> None:
        """Test is_registered returns False for missing key."""
        registry = ConcreteStringRegistry()
        assert not registry.is_registered("missing_key")

    def test_is_registered_returns_true_after_register(self) -> None:
        """Test is_registered returns True after registration."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)
        assert registry.is_registered("key1")

    def test_unregister_existing_key_returns_true(self) -> None:
        """Test unregister returns True when removing existing key."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)

        result = registry.unregister("key1")
        assert result is True
        assert not registry.is_registered("key1")

    def test_unregister_missing_key_returns_false(self) -> None:
        """Test unregister returns False when key not registered."""
        registry = ConcreteStringRegistry()
        result = registry.unregister("missing_key")
        assert result is False

    def test_unregister_idempotent(self) -> None:
        """Test unregister is idempotent - safe to call multiple times."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)

        # First unregister succeeds
        assert registry.unregister("key1") is True

        # Second unregister returns False (no-op)
        assert registry.unregister("key1") is False
        assert registry.unregister("key1") is False


class TestProtocolRegistryBaseErrorHandling:
    """Test error handling behavior."""

    def test_get_missing_key_raises_key_error(self) -> None:
        """Test get raises KeyError for missing key."""
        registry = ConcreteStringRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get("missing_key")

        assert "missing_key" in str(exc_info.value)

    def test_get_after_unregister_raises_key_error(self) -> None:
        """Test get raises KeyError after unregister."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)
        registry.unregister("key1")

        with pytest.raises(KeyError):
            registry.get("key1")


class TestProtocolRegistryBaseInvariants:
    """Test protocol invariants."""

    def test_invariant_register_then_is_registered(self) -> None:
        """After register(k, v), is_registered(k) must return True."""
        registry = ConcreteStringRegistry()

        registry.register("key1", MockService)
        assert registry.is_registered("key1")

        registry.register("key2", type)
        assert registry.is_registered("key2")

    def test_invariant_unregister_then_not_is_registered(self) -> None:
        """After unregister(k), is_registered(k) must return False."""
        registry = ConcreteStringRegistry()
        registry.register("key1", MockService)

        registry.unregister("key1")
        assert not registry.is_registered("key1")

    def test_invariant_get_requires_is_registered(self) -> None:
        """get(k) only succeeds if is_registered(k) is True."""
        registry = ConcreteStringRegistry()

        # Not registered → get fails
        assert not registry.is_registered("key1")
        with pytest.raises(KeyError):
            registry.get("key1")

        # After registration → get succeeds
        registry.register("key1", MockService)
        assert registry.is_registered("key1")
        assert registry.get("key1") is MockService

        # After unregister → get fails again
        registry.unregister("key1")
        assert not registry.is_registered("key1")
        with pytest.raises(KeyError):
            registry.get("key1")

    def test_invariant_list_keys_matches_is_registered(self) -> None:
        """list_keys() contains exactly the keys for which is_registered() is True."""
        registry = ConcreteStringRegistry()

        # Empty registry
        assert registry.list_keys() == []

        # Add keys
        registry.register("key1", MockService)
        registry.register("key2", type)
        registry.register("key3", str)

        keys = registry.list_keys()
        assert len(keys) == 3

        # All keys in list_keys should be registered
        for key in keys:
            assert registry.is_registered(key)

        # All registered keys should be in list_keys
        assert registry.is_registered("key1") and "key1" in keys
        assert registry.is_registered("key2") and "key2" in keys
        assert registry.is_registered("key3") and "key3" in keys

        # Unregister one key
        registry.unregister("key2")
        keys_after = registry.list_keys()

        assert len(keys_after) == 2
        assert "key1" in keys_after
        assert "key2" not in keys_after
        assert "key3" in keys_after


class TestProtocolRegistryBaseEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_registry_operations(self) -> None:
        """Test all operations on empty registry."""
        registry = ConcreteStringRegistry()

        assert registry.list_keys() == []
        assert not registry.is_registered("any_key")
        assert not registry.unregister("any_key")

        with pytest.raises(KeyError):
            registry.get("any_key")

    def test_single_item_operations(self) -> None:
        """Test all operations with single item."""
        registry = ConcreteStringRegistry()

        # Register
        registry.register("only_key", MockService)

        # Verify
        assert len(registry.list_keys()) == 1
        assert registry.is_registered("only_key")
        assert registry.get("only_key") is MockService

        # Unregister
        assert registry.unregister("only_key") is True

        # Verify empty again
        assert registry.list_keys() == []
        assert not registry.is_registered("only_key")

    def test_overwrite_behavior(self) -> None:
        """Test overwriting existing key (implementation allows it)."""
        registry = ConcreteStringRegistry()

        # Register initial value
        registry.register("key1", MockService)
        assert registry.get("key1") is MockService

        # Overwrite with new value
        registry.register("key1", type)
        assert registry.get("key1") is type

        # Still only one key in registry
        assert len(registry.list_keys()) == 1


class TestProtocolRegistryBaseWorkflow:
    """Test typical workflow using ProtocolRegistryBase."""

    def test_complete_registration_workflow(self) -> None:
        """Test complete register, get, list, is_registered, unregister workflow."""
        registry = ConcreteStringRegistry()

        # Initially empty
        assert registry.list_keys() == []
        assert not registry.is_registered("service_a")

        # Register service
        registry.register("service_a", MockService)

        # Verify registration
        assert registry.is_registered("service_a")
        assert "service_a" in registry.list_keys()

        # Retrieve service
        service_cls = registry.get("service_a")
        assert service_cls is MockService

        # Unregister service
        assert registry.unregister("service_a") is True

        # Verify unregistration
        assert not registry.is_registered("service_a")
        assert "service_a" not in registry.list_keys()

    def test_multiple_registration_workflow(self) -> None:
        """Test registering multiple items."""
        registry = ConcreteStringRegistry()

        class ServiceA:
            pass

        class ServiceB:
            pass

        class ServiceC:
            pass

        # Register multiple services
        registry.register("service_a", ServiceA)
        registry.register("service_b", ServiceB)
        registry.register("service_c", ServiceC)

        # Verify all registered
        assert len(registry.list_keys()) == 3
        assert registry.get("service_a") is ServiceA
        assert registry.get("service_b") is ServiceB
        assert registry.get("service_c") is ServiceC

        # Unregister one
        registry.unregister("service_b")

        # Verify remaining
        assert len(registry.list_keys()) == 2
        assert registry.is_registered("service_a")
        assert not registry.is_registered("service_b")
        assert registry.is_registered("service_c")


class TestProtocolRegistryBaseImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_registry_base_module(self) -> None:
        """Test direct import from protocol_registry_base module."""
        from omnibase_spi.protocols.registry.protocol_registry_base import (
            ProtocolRegistryBase as DirectProtocolRegistryBase,
        )

        registry = ConcreteStringRegistry()
        assert isinstance(registry, DirectProtocolRegistryBase)

    def test_import_from_registry_package(self) -> None:
        """Test import from registry package."""
        from omnibase_spi.protocols.registry import (
            ProtocolRegistryBase as RegistryProtocolRegistryBase,
        )

        registry = ConcreteStringRegistry()
        assert isinstance(registry, RegistryProtocolRegistryBase)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.registry import (
            ProtocolRegistryBase as RegistryProtocolRegistryBase,
        )
        from omnibase_spi.protocols.registry.protocol_registry_base import (
            ProtocolRegistryBase as DirectProtocolRegistryBase,
        )

        assert RegistryProtocolRegistryBase is DirectProtocolRegistryBase


class TestProtocolRegistryBaseThreadSafetyDocumentation:
    """
    Document thread safety requirements (no actual concurrency tests).

    Note: These tests document thread safety requirements from the protocol.
    Actual thread safety testing should be done in implementation-specific tests.
    """

    def test_thread_safety_requirement_documented(self) -> None:
        """Verify thread safety is documented in protocol docstring."""
        protocol_doc = ProtocolRegistryBase.__doc__ or ""
        assert (
            "thread" in protocol_doc.lower() or "concurrent" in protocol_doc.lower()
        ), "Protocol should document thread safety requirements"

    def test_register_method_thread_safety_documented(self) -> None:
        """Verify register method documents thread safety."""
        register_doc = ProtocolRegistryBase.register.__doc__ or ""
        assert (
            "thread" in register_doc.lower()
        ), "register should document thread safety"

    def test_get_method_thread_safety_documented(self) -> None:
        """Verify get method documents thread safety."""
        get_doc = ProtocolRegistryBase.get.__doc__ or ""
        assert "thread" in get_doc.lower(), "get should document thread safety"

    def test_unregister_method_thread_safety_documented(self) -> None:
        """Verify unregister method documents thread safety."""
        unregister_doc = ProtocolRegistryBase.unregister.__doc__ or ""
        assert (
            "thread" in unregister_doc.lower()
        ), "unregister should document thread safety"
