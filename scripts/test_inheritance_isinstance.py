#!/usr/bin/env python3
"""
Test isinstance checks for fixed protocol inheritance patterns.

Validates that our inheritance fixes don't break runtime type checking.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_event_bus_inheritance():
    """Test event bus protocol inheritance."""
    from omnibase_spi.protocols.event_bus.protocol_event_bus_mixin import (
        ProtocolAsyncEventBus,
        ProtocolEventBusBase,
        ProtocolRegistryWithBus,
        ProtocolSyncEventBus,
    )

    class MockSyncEventBus:
        async def publish(self, event):
            pass

        def publish_sync(self, event):
            pass

    class MockAsyncEventBus:
        async def publish(self, event):
            pass

        async def publish_async(self, event):
            pass

    class MockRegistryWithBus:
        event_bus = None

    mock_sync = MockSyncEventBus()
    mock_async = MockAsyncEventBus()
    mock_registry = MockRegistryWithBus()

    # Test inheritance relationships
    assert isinstance(
        mock_sync, ProtocolEventBusBase
    ), "SyncEventBus should inherit from base"
    assert isinstance(
        mock_sync, ProtocolSyncEventBus
    ), "SyncEventBus should match its protocol"

    assert isinstance(
        mock_async, ProtocolEventBusBase
    ), "AsyncEventBus should inherit from base"
    assert isinstance(
        mock_async, ProtocolAsyncEventBus
    ), "AsyncEventBus should match its protocol"

    assert isinstance(
        mock_registry, ProtocolRegistryWithBus
    ), "Registry should match its protocol"

    print("✅ Event bus inheritance tests passed")


def test_memory_base_inheritance():
    """Test memory protocol inheritance."""
    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolAggregationCriteria,
        ProtocolAnalysisParameters,
        ProtocolKeyValueStore,
        ProtocolMemoryMetadata,
        ProtocolWorkflowConfiguration,
    )

    class MockMetadata:
        @property
        def keys(self):
            return ["key1", "key2"]

        @property
        def metadata_keys(self):
            return ["meta1", "meta2"]

        async def get_value(self, key):
            return "value"

        async def get_metadata_value(self, key):
            return "meta_value"

        def has_key(self, key):
            return True

        def has_metadata_key(self, key):
            return True

        async def validate_store(self):
            return True

    mock_metadata = MockMetadata()

    # Test inheritance relationships
    assert isinstance(
        mock_metadata, ProtocolKeyValueStore
    ), "Metadata should inherit from base store"
    assert isinstance(
        mock_metadata, ProtocolMemoryMetadata
    ), "Metadata should match its protocol"

    print("✅ Memory inheritance tests passed")


def test_workflow_value_inheritance():
    """Test workflow value protocol inheritance."""
    from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
        ProtocolWorkflowNumericValue,
        ProtocolWorkflowStringDictValue,
        ProtocolWorkflowStringListValue,
        ProtocolWorkflowStringValue,
        ProtocolWorkflowStructuredValue,
        ProtocolWorkflowValue,
    )

    class MockStringValue:
        value = "test"

        def serialize(self):
            return {"value": self.value}

        def validate(self):
            return True

        def get_type_info(self):
            return "string"

        def get_string_length(self):
            return len(self.value)

        def is_empty_string(self):
            return len(self.value) == 0

    class MockNumericValue:
        value = 42

        def serialize(self):
            return {"value": self.value}

        def validate(self):
            return True

        def get_type_info(self):
            return "numeric"

        def is_integer(self):
            return isinstance(self.value, int)

        def is_positive(self):
            return self.value > 0

    mock_string = MockStringValue()
    mock_numeric = MockNumericValue()

    # Test inheritance relationships
    assert isinstance(
        mock_string, ProtocolWorkflowValue
    ), "StringValue should inherit from base"
    assert isinstance(
        mock_string, ProtocolWorkflowStringValue
    ), "StringValue should match its protocol"

    assert isinstance(
        mock_numeric, ProtocolWorkflowValue
    ), "NumericValue should inherit from base"
    assert isinstance(
        mock_numeric, ProtocolWorkflowNumericValue
    ), "NumericValue should match its protocol"

    print("✅ Workflow value inheritance tests passed")


def main():
    """Run all isinstance tests."""
    print("🔍 Testing protocol inheritance isinstance checks...")

    try:
        test_event_bus_inheritance()
        test_memory_base_inheritance()
        test_workflow_value_inheritance()

        print("\n✅ ALL INHERITANCE TESTS PASSED")
        print("🎉 Protocol inheritance fixes are working correctly!")

    except Exception as e:
        print(f"\n❌ INHERITANCE TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
