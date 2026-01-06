"""
Tests for EventBus client protocol compliance (base client, provider, and message).

This module validates that the base EventBus protocols are correctly defined and can be
used for runtime type checking. The tests ensure that:

1. **Protocol Structure**: All protocols are properly decorated with @runtime_checkable
   and inherit from typing.Protocol.

2. **Method Signatures**: Required methods are defined with correct parameter types
   and return values.

3. **Instantiation Prevention**: Protocols cannot be directly instantiated (as expected
   for abstract protocol definitions).

4. **isinstance Checks**: Compliant implementations pass isinstance checks while
   partial or non-compliant implementations fail.

5. **Async Nature**: Async methods are properly defined as coroutines in both
   protocol definitions and compliant implementations.

Protocols Tested
----------------
- **ProtocolEventBusClient**: Core event bus producer with start/stop lifecycle,
  message sending, and connection validation.

- **ProtocolEventBusClientProvider**: Factory protocol for creating client instances
  and retrieving configuration.

- **ProtocolEventBusMessage**: Data structure protocol defining message attributes
  (key, value, topic, partition, offset, timestamp, headers).

Test Organization
-----------------
Tests are organized into the following categories:

1. **Protocol Tests** (TestProtocol*Protocol): Verify protocol definition structure.
2. **Compliance Tests** (TestProtocol*Compliance): Verify isinstance behavior.
3. **Signature Tests** (TestProtocol*MethodSignatures): Verify method signatures.
4. **Async Nature Tests** (TestProtocol*AsyncNature): Verify async/sync methods.

Testing Approach
----------------
Each protocol is tested using three types of mock implementations:

- **Compliant***: Fully implements all protocol requirements
- **Partial***: Implements only some methods (should fail isinstance)
- **NonCompliant***: Implements no methods (should fail isinstance)

This pattern ensures that runtime_checkable protocols correctly distinguish between
complete and incomplete implementations.

Note on Type Ignores
--------------------
Type ignores in this file are used in specific contexts:

- ``# type: ignore[misc]`` on protocol instantiation: Required because we're
  intentionally testing that Protocol classes raise TypeError when instantiated.
  The type checker correctly flags this as an error, but we want to verify the
  runtime behavior.

- ``# type: ignore[arg-type]`` in edge case tests: Used when intentionally passing
  invalid types to test validation logic (e.g., passing str where bytes expected).
"""

import inspect
from typing import Protocol, cast

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_client import (
    ProtocolEventBusClient,
    ProtocolEventBusClientProvider,
)
from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusMessage,
)

# =============================================================================
# Mock/Compliant Implementations for Testing
# =============================================================================
#
# These mock implementations serve as test doubles for protocol compliance testing.
# They are intentionally minimal - providing just enough implementation to satisfy
# protocol requirements while allowing us to verify isinstance checks work correctly.
#
# Design Rationale:
# - Compliant* classes implement ALL required protocol methods/attributes
# - Partial* classes implement SOME methods (to test isinstance failure)
# - NonCompliant* classes implement NO methods (to test isinstance failure)
#
# The pattern of marking unused parameters with `_ = (param, ...)` is intentional:
# it satisfies linters while making clear the mock doesn't use these values.
# =============================================================================


class CompliantEventBusClient:
    """Test double implementing all ProtocolEventBusClient requirements.

    This mock provides a complete implementation of the ProtocolEventBusClient
    protocol, suitable for use in tests that require a compliant client instance.

    Implements:
        - start(): Async lifecycle start
        - stop(timeout_seconds): Async lifecycle stop with configurable timeout
        - send_and_wait(topic, value, key): Async message send with acknowledgment
        - bootstrap_servers(): Sync method returning server list
        - validate_connection(): Async connection validation
        - validate_message(topic, value, key): Async message validation

    All async methods are no-ops (pass/return immediately) since we're only
    testing protocol compliance, not actual EventBus behavior.
    """

    async def start(self) -> None:
        """Start the EventBus client."""
        pass

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client."""
        _ = timeout_seconds  # Unused in mock

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """Send a message and wait for acknowledgment."""
        _ = (topic, value, key)  # Unused in mock

    def bootstrap_servers(self) -> list[str]:
        """Get bootstrap servers."""
        return ["localhost:9092"]

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True

    async def validate_message(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> bool:
        """Validate a message before publishing."""
        _ = (topic, value, key)  # Unused in mock
        return True


class PartialEventBusClient:
    """Test double implementing only SOME ProtocolEventBusClient methods.

    This mock intentionally omits required methods to verify that isinstance()
    correctly identifies incomplete protocol implementations.

    Missing methods (intentionally):
        - send_and_wait
        - bootstrap_servers
        - validate_connection
        - validate_message

    Used by: test_partial_implementation_fails_isinstance
    """

    async def start(self) -> None:
        """Start the EventBus client."""
        pass

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client."""
        _ = timeout_seconds  # Unused in mock


class NonCompliantEventBusClient:
    """Test double implementing NONE of the ProtocolEventBusClient methods.

    This empty class verifies that isinstance() correctly rejects objects
    with no protocol method implementations.

    Used by: test_non_compliant_class_fails_isinstance
    """

    pass


class CompliantEventBusClientProvider:
    """Test double implementing all ProtocolEventBusClientProvider requirements.

    This mock provides a factory implementation that creates compliant client
    instances, suitable for testing provider protocol compliance.

    Implements:
        - create_event_bus_client(): Creates a new ProtocolEventBusClient
        - get_event_bus_configuration(): Returns configuration dict
    """

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """Create a new EventBus client instance."""
        # Cast is safe: CompliantEventBusClient implements all ProtocolEventBusClient methods.
        # The cast is needed because CompliantEventBusClient doesn't explicitly inherit
        # from the Protocol, but it structurally satisfies it (duck typing).
        return cast(ProtocolEventBusClient, CompliantEventBusClient())

    async def get_event_bus_configuration(self) -> dict[str, str | int | float | bool]:
        """Retrieve EventBus client configuration parameters."""
        return {"bootstrap_servers": "localhost:9092", "client_id": "test-client"}


class PartialEventBusClientProvider:
    """Test double implementing only SOME ProtocolEventBusClientProvider methods.

    Missing methods (intentionally):
        - get_event_bus_configuration

    Used by: test_partial_implementation_fails_isinstance
    """

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """Create a new EventBus client instance."""
        # Cast is safe: CompliantEventBusClient implements all ProtocolEventBusClient methods
        return cast(ProtocolEventBusClient, CompliantEventBusClient())


class CompliantEventBusMessage:
    """Test double implementing all ProtocolEventBusMessage attribute requirements.

    This mock provides a data container satisfying the message protocol,
    with validation logic to ensure proper message construction.

    Attributes:
        key: Optional message key for partitioning
        value: Message payload (required, must be bytes)
        topic: Destination topic name (required, non-empty)
        partition: Target partition (optional, must be >= 0)
        offset: Message offset (optional, must be >= 0)
        timestamp: Unix timestamp in milliseconds (optional)
        headers: Message headers dictionary (defaults to {})

    The constructor performs validation to ensure messages are well-formed,
    which helps test edge cases in the validation error tests.
    """

    def __init__(
        self,
        value: bytes = b'{"test": "data"}',
        topic: str = "test-topic",
        key: bytes | None = b"test-key",
        partition: int | None = 0,
        offset: int | None = 100,
        timestamp: int | None = 1699999999,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Initialize a compliant EventBus message with validation.

        Args:
            value: Message payload (required, must be bytes).
            topic: Topic name (must be non-empty string).
            key: Optional message key.
            partition: Optional partition number (must be >= 0 if provided).
            offset: Optional offset (must be >= 0 if provided).
            timestamp: Optional timestamp in milliseconds.
            headers: Optional headers dictionary.

        Raises:
            TypeError: If value is not bytes.
            ValueError: If topic is empty or partition/offset is negative.
        """
        if not isinstance(value, bytes):
            raise TypeError("value must be bytes")
        if not topic or not isinstance(topic, str):
            raise ValueError("topic must be a non-empty string")
        if partition is not None and partition < 0:
            raise ValueError("partition must be non-negative")
        if offset is not None and offset < 0:
            raise ValueError("offset must be non-negative")

        self.key = key
        self.value = value
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.timestamp = timestamp
        self.headers: dict[str, bytes] = headers if headers is not None else {}


class PartialEventBusMessage:
    """Test double implementing only SOME ProtocolEventBusMessage attributes.

    Missing attributes (intentionally):
        - partition
        - offset
        - timestamp
        - headers

    Used by: test_partial_implementation_fails_isinstance
    """

    key: bytes | None = b"test-key"
    value: bytes = b'{"test": "data"}'
    topic: str = "test-topic"


# =============================================================================
# Pytest Fixtures
# =============================================================================
#
# Fixtures provide pre-configured test doubles for protocol compliance testing.
# Each fixture returns a fresh instance of the corresponding compliant mock,
# ensuring test isolation.
# =============================================================================


@pytest.fixture
def compliant_client() -> CompliantEventBusClient:
    """Provide a compliant EventBus client for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusClient instance implementing all
        ProtocolEventBusClient requirements.
    """
    return CompliantEventBusClient()


@pytest.fixture
def compliant_message() -> CompliantEventBusMessage:
    """Provide a compliant EventBus message for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusMessage instance with default values,
        implementing all ProtocolEventBusMessage attribute requirements.
    """
    return CompliantEventBusMessage()


@pytest.fixture
def compliant_client_provider() -> CompliantEventBusClientProvider:
    """Provide a compliant EventBus client provider for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusClientProvider instance implementing all
        ProtocolEventBusClientProvider requirements.
    """
    return CompliantEventBusClientProvider()


# =============================================================================
# Test Classes
# =============================================================================
#
# Tests are organized by protocol, with each protocol having multiple test classes:
# - *Protocol: Verifies protocol definition structure
# - *Compliance: Verifies isinstance behavior for compliant/non-compliant classes
# - *MethodSignatures: Verifies method signatures match expectations
# - *AsyncNature: Verifies async/sync method characteristics
# =============================================================================


class TestProtocolEventBusClientProtocol:
    """Test suite verifying ProtocolEventBusClient protocol definition structure.

    These tests ensure the protocol is correctly defined with all required
    methods and the @runtime_checkable decorator for isinstance checks.

    Tests cover:
        - Protocol is marked as @runtime_checkable
        - Protocol inherits from typing.Protocol
        - All required methods are defined in the protocol
        - Protocol cannot be directly instantiated
    """

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusClient should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolEventBusClient, "_is_runtime_protocol") or hasattr(
            ProtocolEventBusClient, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusClient should be a Protocol class."""
        # type: ignore[comparison-overlap] - mypy incorrectly flags this comparison,
        # but at runtime we need to check if Protocol is in the MRO
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolEventBusClient.__mro__
        )

    def test_protocol_has_start_method(self) -> None:
        """ProtocolEventBusClient should define start method."""
        assert "start" in dir(ProtocolEventBusClient)

    def test_protocol_has_stop_method(self) -> None:
        """ProtocolEventBusClient should define stop method."""
        assert "stop" in dir(ProtocolEventBusClient)

    def test_protocol_has_send_and_wait_method(self) -> None:
        """ProtocolEventBusClient should define send_and_wait method."""
        assert "send_and_wait" in dir(ProtocolEventBusClient)

    def test_protocol_has_bootstrap_servers_method(self) -> None:
        """ProtocolEventBusClient should define bootstrap_servers method."""
        assert "bootstrap_servers" in dir(ProtocolEventBusClient)

    def test_protocol_has_validate_connection_method(self) -> None:
        """ProtocolEventBusClient should define validate_connection method."""
        assert "validate_connection" in dir(ProtocolEventBusClient)

    def test_protocol_has_validate_message_method(self) -> None:
        """ProtocolEventBusClient should define validate_message method."""
        assert "validate_message" in dir(ProtocolEventBusClient)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusClient should not be directly instantiable."""
        with pytest.raises(TypeError):
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusClient()  # type: ignore[misc]


class TestProtocolEventBusClientCompliance:
    """Test isinstance checks for ProtocolEventBusClient protocol compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_client, ProtocolEventBusClient)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        client = PartialEventBusClient()
        assert not isinstance(client, ProtocolEventBusClient)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        client = NonCompliantEventBusClient()
        assert not isinstance(client, ProtocolEventBusClient)


class TestProtocolEventBusClientMethodSignatures:
    """Test method signatures from compliant implementations."""

    @pytest.mark.asyncio
    async def test_start_takes_no_args(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """start method should take no arguments."""
        await compliant_client.start()  # Should not raise

    @pytest.mark.asyncio
    async def test_stop_accepts_timeout(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """stop method should accept optional timeout parameter."""
        await compliant_client.stop()  # Default timeout
        await compliant_client.stop(timeout_seconds=10.0)  # Custom timeout

    @pytest.mark.asyncio
    async def test_send_and_wait_accepts_required_params(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """send_and_wait should accept topic and value parameters."""
        await compliant_client.send_and_wait(topic="test", value=b"data")

    @pytest.mark.asyncio
    async def test_send_and_wait_accepts_optional_key(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """send_and_wait should accept optional key parameter."""
        await compliant_client.send_and_wait(topic="test", value=b"data", key=b"key")

    def test_bootstrap_servers_returns_list(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """bootstrap_servers should return a list of strings."""
        servers = compliant_client.bootstrap_servers()
        assert isinstance(servers, list)
        assert all(isinstance(s, str) for s in servers)

    @pytest.mark.asyncio
    async def test_validate_connection_returns_bool(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """validate_connection should return a boolean."""
        result = await compliant_client.validate_connection()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_validate_message_returns_bool(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """validate_message should return a boolean."""
        result = await compliant_client.validate_message(topic="test", value=b"data")
        assert isinstance(result, bool)


class TestProtocolEventBusClientAsyncNature:
    """Test that ProtocolEventBusClient methods are async."""

    def test_start_is_async(self) -> None:
        """start should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "start", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.start)

    def test_stop_is_async(self) -> None:
        """stop should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "stop", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.stop)

    def test_send_and_wait_is_async(self) -> None:
        """send_and_wait should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "send_and_wait", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.send_and_wait)

    def test_validate_connection_is_async(self) -> None:
        """validate_connection should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "validate_connection", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.validate_connection)

    def test_validate_message_is_async(self) -> None:
        """validate_message should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "validate_message", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.validate_message)

    def test_bootstrap_servers_is_sync(self) -> None:
        """bootstrap_servers should be a sync method in both protocol and implementation."""
        # Check protocol defines sync signature
        protocol_method = getattr(ProtocolEventBusClient, "bootstrap_servers", None)
        assert protocol_method is not None
        assert not inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is sync
        assert not inspect.iscoroutinefunction(
            CompliantEventBusClient.bootstrap_servers
        )


class TestProtocolEventBusClientProviderProtocol:
    """Test suite for ProtocolEventBusClientProvider protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusClientProvider should be runtime_checkable."""
        assert hasattr(
            ProtocolEventBusClientProvider, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventBusClientProvider, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusClientProvider should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolEventBusClientProvider.__mro__
        )

    def test_protocol_has_create_event_bus_client_method(self) -> None:
        """Should define create_event_bus_client method."""
        assert "create_event_bus_client" in dir(ProtocolEventBusClientProvider)

    def test_protocol_has_get_event_bus_configuration_method(self) -> None:
        """Should define get_event_bus_configuration method."""
        assert "get_event_bus_configuration" in dir(ProtocolEventBusClientProvider)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusClientProvider should not be directly instantiable."""
        with pytest.raises(TypeError):
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusClientProvider()  # type: ignore[misc]


class TestProtocolEventBusClientProviderCompliance:
    """Test isinstance checks for ProtocolEventBusClientProvider compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_client_provider: CompliantEventBusClientProvider
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_client_provider, ProtocolEventBusClientProvider)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        provider = PartialEventBusClientProvider()
        assert not isinstance(provider, ProtocolEventBusClientProvider)


class TestProtocolEventBusClientProviderMethodSignatures:
    """Test method signatures for ProtocolEventBusClientProvider."""

    @pytest.mark.asyncio
    async def test_create_event_bus_client_returns_client(
        self, compliant_client_provider: CompliantEventBusClientProvider
    ) -> None:
        """create_event_bus_client should return a ProtocolEventBusClient."""
        client = await compliant_client_provider.create_event_bus_client()
        assert isinstance(client, ProtocolEventBusClient)

    @pytest.mark.asyncio
    async def test_get_event_bus_configuration_returns_dict(
        self, compliant_client_provider: CompliantEventBusClientProvider
    ) -> None:
        """get_event_bus_configuration should return a configuration dict."""
        config = await compliant_client_provider.get_event_bus_configuration()
        assert isinstance(config, dict)


class TestProtocolEventBusMessageProtocol:
    """Test suite for ProtocolEventBusMessage protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusMessage should be runtime_checkable."""
        assert hasattr(ProtocolEventBusMessage, "_is_runtime_protocol") or hasattr(
            ProtocolEventBusMessage, "__runtime_protocol__"
        )

    def test_protocol_has_key_attribute(self) -> None:
        """ProtocolEventBusMessage should define key attribute."""
        # Check protocol defines the attribute in annotations
        assert "key" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "key")

    def test_protocol_has_value_attribute(self) -> None:
        """ProtocolEventBusMessage should define value attribute."""
        # Check protocol defines the attribute in annotations
        assert "value" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "value")

    def test_protocol_has_topic_attribute(self) -> None:
        """ProtocolEventBusMessage should define topic attribute."""
        # Check protocol defines the attribute in annotations
        assert "topic" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "topic")

    def test_protocol_has_partition_attribute(self) -> None:
        """ProtocolEventBusMessage should define partition attribute."""
        # Check protocol defines the attribute in annotations
        assert "partition" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "partition")

    def test_protocol_has_offset_attribute(self) -> None:
        """ProtocolEventBusMessage should define offset attribute."""
        # Check protocol defines the attribute in annotations
        assert "offset" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "offset")

    def test_protocol_has_timestamp_attribute(self) -> None:
        """ProtocolEventBusMessage should define timestamp attribute."""
        # Check protocol defines the attribute in annotations
        assert "timestamp" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "timestamp")

    def test_protocol_has_headers_attribute(self) -> None:
        """ProtocolEventBusMessage should define headers attribute."""
        # Check protocol defines the attribute in annotations
        assert "headers" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation instance has it
        assert hasattr(CompliantEventBusMessage(), "headers")

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusMessage should not be directly instantiable."""
        with pytest.raises(TypeError):
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusMessage()  # type: ignore[misc]


class TestProtocolEventBusMessageCompliance:
    """Test isinstance checks for ProtocolEventBusMessage compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_message: CompliantEventBusMessage
    ) -> None:
        """A class implementing all attributes should pass isinstance check."""
        assert isinstance(compliant_message, ProtocolEventBusMessage)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing attributes should fail isinstance check."""
        message = PartialEventBusMessage()
        assert not isinstance(message, ProtocolEventBusMessage)
