# Testing Guide

## Overview

Comprehensive testing strategies for omnibase-spi protocol-based applications. This guide covers protocol compliance testing, mock strategies, integration testing, and quality assurance patterns for distributed systems using the Service Provider Interface architecture.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Protocol Compliance Testing](#protocol-compliance-testing)
- [Mocking and Stubbing](#mocking-and-stubbing)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Test Infrastructure](#test-infrastructure)

## Testing Philosophy

### Protocol-First Testing

With omnibase-spi, testing focuses on protocol contracts rather than implementations:

```python
# ✅ Test against protocol interface
async def test_user_creation(user_service: ProtocolUserService):
    """Test user creation through protocol interface."""
    user = await user_service.create_user("test@example.com", "Test User")

    # Test protocol contract
    assert isinstance(user.id, UUID)
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.status in get_args(UserStatus)  # Valid enum value

# ❌ Avoid testing implementation details
async def test_database_user_creation_internal():
    """Avoid testing internal implementation details."""
    db_service = DatabaseUserService(connection)

    # ❌ Testing implementation internals
    assert db_service._connection is not None
    assert db_service._query_cache.size == 0
```

### Testing Pyramid for Protocols

```mermaid
graph TB
    E2E[End-to-End Tests<br/>Protocol Integration]
    INT[Integration Tests<br/>Multi-Protocol Workflows]
    PROT[Protocol Compliance Tests<br/>Contract Verification]
    UNIT[Unit Tests<br/>Individual Method Behavior]

    UNIT --> PROT
    PROT --> INT
    INT --> E2E
```

**Testing Levels:**

1. **Unit Tests**: Individual protocol method behavior
2. **Protocol Compliance**: Contract verification across implementations
3. **Integration Tests**: Multi-protocol workflows
4. **End-to-End**: Complete system scenarios

## Protocol Compliance Testing

### Abstract Test Suites

Create abstract test suites that verify protocol contracts:

```python
from abc import ABC
import pytest
from typing import get_args
from omnibase_spi.protocols.core import ProtocolUserService
from omnibase_spi.protocols.types.core_types import UserStatus

class UserServiceComplianceTests(ABC):
    """
    Abstract test suite for ProtocolUserService compliance.

    All implementations must pass these tests to ensure
    they correctly implement the protocol contract.
    """

    @pytest.fixture
    def user_service(self) -> ProtocolUserService:
        """
        Override in subclasses to provide implementation.

        Returns:
            Implementation of ProtocolUserService to test
        """
        raise NotImplementedError("Subclasses must provide user_service fixture")

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service: ProtocolUserService):
        """Test successful user creation."""
        user = await user_service.create_user("test@example.com", "Test User")

        # Verify protocol contract
        assert isinstance(user.id, UUID), "User ID must be UUID"
        assert user.email == "test@example.com", "Email must match input"
        assert user.name == "Test User", "Name must match input"
        assert user.status in get_args(UserStatus), "Status must be valid UserStatus"
        assert isinstance(user.created_at, datetime), "Created timestamp required"
        assert user.updated_at is None, "New users should have no update timestamp"

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, user_service: ProtocolUserService):
        """Test user creation with invalid email."""
        invalid_emails = ["", "invalid", "@example.com", "test@", "test..test@example.com"]

        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="email|Email"):
                await user_service.create_user(invalid_email, "Test User")

    @pytest.mark.asyncio
    async def test_create_user_empty_name(self, user_service: ProtocolUserService):
        """Test user creation with empty name."""
        empty_names = ["", "   ", "\t", "\n"]

        for empty_name in empty_names:
            with pytest.raises(ValueError, match="name|Name"):
                await user_service.create_user("test@example.com", empty_name)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service: ProtocolUserService):
        """Test duplicate email handling."""
        email = "duplicate@example.com"

        # Create first user
        user1 = await user_service.create_user(email, "First User")
        assert user1.email == email

        # Attempt to create duplicate
        with pytest.raises(ValueError, match="already exists|duplicate"):
            await user_service.create_user(email, "Second User")

    @pytest.mark.asyncio
    async def test_get_user_existing(self, user_service: ProtocolUserService):
        """Test retrieving existing user."""
        # Create user first
        created_user = await user_service.create_user("get@example.com", "Get User")

        # Retrieve user
        retrieved_user = await user_service.get_user(created_user.id)

        # Verify protocol contract
        assert retrieved_user is not None, "Existing user should be found"
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name
        assert retrieved_user.status == created_user.status

    @pytest.mark.asyncio
    async def test_get_user_nonexistent(self, user_service: ProtocolUserService):
        """Test retrieving non-existent user."""
        non_existent_id = uuid4()
        user = await user_service.get_user(non_existent_id)
        assert user is None, "Non-existent user should return None"

    @pytest.mark.asyncio
    async def test_list_users_empty(self, user_service: ProtocolUserService):
        """Test listing users when none exist."""
        users = await user_service.list_users()
        assert isinstance(users, list), "list_users must return list"
        # Note: May be empty or contain existing test data

    @pytest.mark.asyncio
    async def test_list_users_with_data(self, user_service: ProtocolUserService):
        """Test listing users with data."""
        # Create test users
        user1 = await user_service.create_user("list1@example.com", "List User 1")
        user2 = await user_service.create_user("list2@example.com", "List User 2")

        # List users
        users = await user_service.list_users()

        # Verify protocol contract
        assert isinstance(users, list), "list_users must return list"
        assert len(users) >= 2, "Should contain at least the created users"

        # Verify created users are in the list
        user_ids = {user.id for user in users}
        assert user1.id in user_ids, "Created user 1 should be in list"
        assert user2.id in user_ids, "Created user 2 should be in list"

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service: ProtocolUserService):
        """Test successful user update."""
        # Create user
        user = await user_service.create_user("update@example.com", "Original Name")

        # Update user
        updates = {"name": "Updated Name"}
        result = await user_service.update_user(user.id, updates)
        assert result is True, "Update should return True on success"

        # Verify update
        updated_user = await user_service.get_user(user.id)
        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        assert updated_user.updated_at is not None
        assert updated_user.updated_at > user.created_at

    @pytest.mark.asyncio
    async def test_update_user_nonexistent(self, user_service: ProtocolUserService):
        """Test updating non-existent user."""
        non_existent_id = uuid4()
        with pytest.raises(ValueError, match="not found|does not exist"):
            await user_service.update_user(non_existent_id, {"name": "Updated"})

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service: ProtocolUserService):
        """Test successful user deletion."""
        # Create user
        user = await user_service.create_user("delete@example.com", "Delete User")

        # Delete user
        result = await user_service.delete_user(user.id)
        assert result is True, "Delete should return True on success"

        # Verify deletion
        deleted_user = await user_service.get_user(user.id)
        assert deleted_user is None, "Deleted user should not be found"

    @pytest.mark.asyncio
    async def test_delete_user_nonexistent(self, user_service: ProtocolUserService):
        """Test deleting non-existent user."""
        non_existent_id = uuid4()
        result = await user_service.delete_user(non_existent_id)
        assert result is False, "Deleting non-existent user should return False"

    @pytest.mark.asyncio
    async def test_protocol_runtime_checking(self, user_service: ProtocolUserService):
        """Test that implementation satisfies protocol at runtime."""
        # Verify isinstance works with protocol
        assert isinstance(user_service, ProtocolUserService), (
            "Implementation must satisfy ProtocolUserService"
        )

# Concrete test implementations
class TestInMemoryUserService(UserServiceComplianceTests):
    """Test InMemoryUserService implementation."""

    @pytest.fixture
    def user_service(self):
        return InMemoryUserService()

class TestDatabaseUserService(UserServiceComplianceTests):
    """Test DatabaseUserService implementation."""

    @pytest.fixture
    def user_service(self):
        # Use test database
        return DatabaseUserService(connection_string="sqlite:///:memory:")

class TestCachedUserService(UserServiceComplianceTests):
    """Test CachedUserService implementation."""

    @pytest.fixture
    def user_service(self):
        base_service = InMemoryUserService()
        cache_service = InMemoryCache()
        return CachedUserService(base_service, cache_service)

# Protocol-specific compliance testing
def test_all_implementations_satisfy_protocol():
    """Verify all implementations satisfy the protocol."""
    implementations = [
        InMemoryUserService(),
        DatabaseUserService("sqlite:///:memory:"),
        CachedUserService(InMemoryUserService(), InMemoryCache())
    ]

    for impl in implementations:
        assert isinstance(impl, ProtocolUserService), (
            f"{type(impl).__name__} must implement ProtocolUserService"
        )
```

### Cross-Implementation Testing

Test multiple implementations with the same data:

```python
class CrossImplementationTests:
    """Test behavior consistency across implementations."""

    def __init__(self):
        self.implementations = [
            ("InMemory", lambda: InMemoryUserService()),
            ("Database", lambda: DatabaseUserService("sqlite:///:memory:")),
            ("Cached", lambda: CachedUserService(InMemoryUserService(), InMemoryCache()))
        ]

    @pytest.mark.asyncio
    async def test_consistent_behavior_across_implementations(self):
        """Test that all implementations behave consistently."""
        test_email = "consistent@example.com"
        test_name = "Consistent User"

        created_users = {}

        # Create user in each implementation
        for name, factory in self.implementations:
            service = factory()
            user = await service.create_user(test_email, test_name)
            created_users[name] = user

            # Verify consistent properties
            assert user.email == test_email
            assert user.name == test_name
            assert isinstance(user.id, UUID)
            assert user.status in get_args(UserStatus)

        # Verify all implementations created users with same basic properties
        emails = {user.email for user in created_users.values()}
        names = {user.name for user in created_users.values()}

        assert len(emails) == 1 and test_email in emails
        assert len(names) == 1 and test_name in names

    @pytest.mark.asyncio
    async def test_error_consistency_across_implementations(self):
        """Test that error handling is consistent."""
        invalid_inputs = [
            ("", "Test User"),  # Empty email
            ("invalid-email", "Test User"),  # Invalid email format
            ("test@example.com", ""),  # Empty name
        ]

        for email, name in invalid_inputs:
            error_types = set()

            for impl_name, factory in self.implementations:
                service = factory()

                try:
                    await service.create_user(email, name)
                    pytest.fail(f"{impl_name} should have raised an error for {email}, {name}")
                except Exception as e:
                    error_types.add(type(e))

            # All implementations should raise the same exception type
            assert len(error_types) == 1, (
                f"Inconsistent error types for {email}, {name}: {error_types}"
            )
```

## Mocking and Stubbing

### Protocol Mock Factory

Create a comprehensive mock factory for protocols:

```python
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, Optional, Callable
from collections import defaultdict

class ProtocolMockFactory:
    """Factory for creating comprehensive protocol mocks."""

    @staticmethod
    def create_user_service_mock(
        with_state: bool = True,
        custom_behaviors: Optional[Dict[str, Callable]] = None
    ) -> ProtocolUserService:
        """
        Create comprehensive mock of ProtocolUserService.

        Args:
            with_state: If True, mock maintains state for realistic behavior
            custom_behaviors: Custom behavior overrides for specific methods

        Returns:
            Mock implementation of ProtocolUserService
        """
        mock = AsyncMock(spec=ProtocolUserService)

        if with_state:
            # Add stateful behavior
            mock._users: Dict[UUID, Any] = {}
            mock._call_log: list[dict] = []

            async def mock_create_user(email: str, name: str) -> Any:
                # Log call
                mock._call_log.append({
                    "method": "create_user",
                    "args": {"email": email, "name": name},
                    "timestamp": datetime.now()
                })

                # Validate input
                if not email or "@" not in email:
                    raise ValueError("Invalid email address")
                if not name or len(name.strip()) == 0:
                    raise ValueError("Name cannot be empty")

                # Check for duplicates
                for user in mock._users.values():
                    if user.email == email:
                        raise ValueError(f"User with email {email} already exists")

                # Create mock user
                user = MagicMock()
                user.id = uuid4()
                user.email = email
                user.name = name
                user.status = "active"
                user.created_at = datetime.now()
                user.updated_at = None
                user.metadata = {}

                mock._users[user.id] = user
                return user

            async def mock_get_user(user_id: UUID) -> Optional[Any]:
                mock._call_log.append({
                    "method": "get_user",
                    "args": {"user_id": user_id},
                    "timestamp": datetime.now()
                })
                return mock._users.get(user_id)

            async def mock_list_users() -> list[Any]:
                mock._call_log.append({
                    "method": "list_users",
                    "args": {},
                    "timestamp": datetime.now()
                })
                return list(mock._users.values())

            async def mock_update_user(user_id: UUID, updates: dict[str, str]) -> bool:
                mock._call_log.append({
                    "method": "update_user",
                    "args": {"user_id": user_id, "updates": updates},
                    "timestamp": datetime.now()
                })

                if user_id not in mock._users:
                    raise ValueError("User not found")

                user = mock._users[user_id]
                for key, value in updates.items():
                    setattr(user, key, value)
                user.updated_at = datetime.now()

                return True

            async def mock_delete_user(user_id: UUID) -> bool:
                mock._call_log.append({
                    "method": "delete_user",
                    "args": {"user_id": user_id},
                    "timestamp": datetime.now()
                })

                if user_id in mock._users:
                    del mock._users[user_id]
                    return True
                return False

            # Bind mock methods
            mock.create_user.side_effect = mock_create_user
            mock.get_user.side_effect = mock_get_user
            mock.list_users.side_effect = mock_list_users
            mock.update_user.side_effect = mock_update_user
            mock.delete_user.side_effect = mock_delete_user

        # Apply custom behaviors
        if custom_behaviors:
            for method_name, behavior in custom_behaviors.items():
                if hasattr(mock, method_name):
                    getattr(mock, method_name).side_effect = behavior

        # Add helper methods for testing
        def assert_create_user_called_with(email: str, name: str):
            """Assert create_user was called with specific parameters."""
            for call in mock._call_log:
                if (call["method"] == "create_user" and
                    call["args"]["email"] == email and
                    call["args"]["name"] == name):
                    return
            raise AssertionError(f"create_user not called with email={email}, name={name}")

        def get_call_count(method_name: str) -> int:
            """Get number of times method was called."""
            return sum(1 for call in mock._call_log if call["method"] == method_name)

        def get_users_created() -> list:
            """Get all users created during test."""
            return list(mock._users.values())

        # Attach helper methods
        mock.assert_create_user_called_with = assert_create_user_called_with
        mock.get_call_count = get_call_count
        mock.get_users_created = get_users_created

        return mock

    @staticmethod
    def create_logger_mock() -> ProtocolLogger:
        """Create mock logger that captures log entries."""
        mock = AsyncMock(spec=ProtocolLogger)
        mock.log_entries = []

        async def capture_log(level: str, message: str, context: dict):
            mock.log_entries.append({
                "level": level,
                "message": message,
                "context": context.copy(),
                "timestamp": datetime.now()
            })

        mock.info.side_effect = lambda msg, ctx: capture_log("INFO", msg, ctx)
        mock.error.side_effect = lambda msg, ctx: capture_log("ERROR", msg, ctx)
        mock.warning.side_effect = lambda msg, ctx: capture_log("WARNING", msg, ctx)
        mock.debug.side_effect = lambda msg, ctx: capture_log("DEBUG", msg, ctx)
        mock.critical.side_effect = lambda msg, ctx: capture_log("CRITICAL", msg, ctx)

        # Helper methods
        def assert_logged(level: str, message_contains: str):
            """Assert specific log entry exists."""
            for entry in mock.log_entries:
                if entry["level"] == level and message_contains in entry["message"]:
                    return
            raise AssertionError(f"No {level} log containing '{message_contains}'")

        def get_log_count(level: str) -> int:
            """Get count of logs at specific level."""
            return sum(1 for entry in mock.log_entries if entry["level"] == level)

        mock.assert_logged = assert_logged
        mock.get_log_count = get_log_count

        return mock

    @staticmethod
    def create_cache_mock() -> ProtocolCacheService:
        """Create mock cache service with stateful behavior."""
        mock = AsyncMock(spec=ProtocolCacheService)
        mock._cache: Dict[str, Any] = {}
        mock._access_times: Dict[str, datetime] = {}

        async def mock_get(key: str) -> Optional[Any]:
            mock._access_times[key] = datetime.now()
            return mock._cache.get(key)

        async def mock_set(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
            mock._cache[key] = value
            mock._access_times[key] = datetime.now()
            return True

        async def mock_delete(key: str) -> bool:
            deleted = key in mock._cache
            mock._cache.pop(key, None)
            mock._access_times.pop(key, None)
            return deleted

        async def mock_clear() -> None:
            mock._cache.clear()
            mock._access_times.clear()

        mock.get.side_effect = mock_get
        mock.set.side_effect = mock_set
        mock.delete.side_effect = mock_delete
        mock.clear.side_effect = mock_clear

        # Helper methods
        def get_cache_size() -> int:
            return len(mock._cache)

        def assert_cached(key: str):
            if key not in mock._cache:
                raise AssertionError(f"Key '{key}' not found in cache")

        mock.get_cache_size = get_cache_size
        mock.assert_cached = assert_cached

        return mock

# Test fixtures using mock factory
@pytest.fixture
def mock_user_service():
    """Provide stateful mock user service."""
    return ProtocolMockFactory.create_user_service_mock(with_state=True)

@pytest.fixture
def mock_logger():
    """Provide mock logger."""
    return ProtocolMockFactory.create_logger_mock()

@pytest.fixture  
def mock_cache():
    """Provide mock cache service."""
    return ProtocolMockFactory.create_cache_mock()

@pytest.fixture
def test_container(mock_user_service, mock_logger, mock_cache):
    """Provide service container with mocks."""
    container = ServiceContainer()
    container.register_singleton(ProtocolUserService, mock_user_service)
    container.register_singleton(ProtocolLogger, mock_logger)
    container.register_singleton(ProtocolCacheService, mock_cache)
    return container
```

### Behavior-Driven Mock Testing

```python
class BehaviorDrivenMockTests:
    """Tests using behavior-driven mock patterns."""

    @pytest.mark.asyncio
    async def test_user_service_with_custom_behavior(self):
        """Test service with custom mock behavior."""

        # Custom behavior: Simulate database connection failure
        async def failing_create_user(email: str, name: str):
            if "fail" in email:
                raise RuntimeError("Database connection failed")
            # Normal behavior for other emails
            user = MagicMock()
            user.id = uuid4()
            user.email = email
            user.name = name
            return user

        mock_service = ProtocolMockFactory.create_user_service_mock(
            custom_behaviors={
                "create_user": failing_create_user
            }
        )

        # Test normal operation
        user = await mock_service.create_user("normal@example.com", "Normal User")
        assert user.email == "normal@example.com"

        # Test failure behavior
        with pytest.raises(RuntimeError, match="Database connection failed"):
            await mock_service.create_user("fail@example.com", "Fail User")

    @pytest.mark.asyncio
    async def test_service_interaction_patterns(self):
        """Test interactions between mocked services."""
        user_service = ProtocolMockFactory.create_user_service_mock(with_state=True)
        logger = ProtocolMockFactory.create_logger_mock()
        cache = ProtocolMockFactory.create_cache_mock()

        # Service that uses all three protocols
        composite_service = CompositeUserManager(user_service, logger, cache)

        # Test workflow
        user = await composite_service.create_user_with_caching(
            "composite@example.com", "Composite User"
        )

        # Verify interactions
        assert user is not None
        user_service.assert_create_user_called_with("composite@example.com", "Composite User")
        logger.assert_logged("INFO", "User created")
        cache.assert_cached(f"user:{user.id}")

        # Verify call counts
        assert user_service.get_call_count("create_user") == 1
        assert logger.get_log_count("INFO") >= 1
        assert cache.get_cache_size() == 1
```

## Integration Testing

### Multi-Service Integration Tests

```python
class MultiServiceIntegrationTests:
    """Integration tests across multiple protocols."""

    @pytest.fixture
    async def integration_services(self):
        """Setup services for integration testing."""
        # Use real implementations for integration tests
        db_user_service = DatabaseUserService("postgresql://test_db")
        redis_cache = RedisCache("redis://localhost:6379/1")
        kafka_event_bus = KafkaEventBus("localhost:9092")
        structured_logger = StructuredLogger(level="DEBUG")

        return {
            "user_service": db_user_service,
            "cache": redis_cache,
            "event_bus": kafka_event_bus,
            "logger": structured_logger
        }

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_user_workflow_integration(self, integration_services):
        """Test complete user workflow with real services."""
        user_service = integration_services["user_service"]
        logger = integration_services["logger"]
        event_bus = integration_services["event_bus"]

        correlation_id = uuid4()

        # Setup event handler to track workflow
        events_received = []

        async def event_handler(event: ProtocolWorkflowEvent, context: dict):
            events_received.append(event)

        # Subscribe to user events
        unsubscribe = await event_bus.subscribe_to_workflow_events(
            workflow_type="user_management",
            event_types=["user.created", "user.updated"],
            handler=event_handler,
            group_id="test_integration"
        )

        try:
            # Create user with workflow
            await logger.info("Starting user integration test", context={
                "correlation_id": str(correlation_id)
            })

            user = await user_service.create_user(
                "integration@example.com",
                "Integration User"
            )

            # Publish user created event
            user_created_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="user.created",
                workflow_type="user_management",
                instance_id=correlation_id,
                sequence_number=1,
                timestamp=datetime.now(),
                data={"user_id": str(user.id), "email": user.email},
                metadata={"test": "integration"},
                idempotency_key=f"user-created-{user.id}",
                source_node_id="test-integration"
            )

            await event_bus.publish_workflow_event(user_created_event)

            # Update user
            await user_service.update_user(user.id, {"name": "Updated Integration User"})

            # Publish user updated event
            user_updated_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="user.updated",
                workflow_type="user_management",
                instance_id=correlation_id,
                sequence_number=2,
                causation_id=user_created_event.event_id,
                timestamp=datetime.now(),
                data={"user_id": str(user.id), "updated_fields": ["name"]},
                metadata={"test": "integration"},
                idempotency_key=f"user-updated-{user.id}-1",
                source_node_id="test-integration"
            )

            await event_bus.publish_workflow_event(user_updated_event)

            # Wait for events to be processed
            await asyncio.sleep(2)

            # Verify integration
            assert len(events_received) == 2
            assert events_received[0].event_type == "user.created"
            assert events_received[1].event_type == "user.updated"

            # Verify user in database
            retrieved_user = await user_service.get_user(user.id)
            assert retrieved_user is not None
            assert retrieved_user.name == "Updated Integration User"

        finally:
            # Cleanup
            await unsubscribe()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_caching_integration(self, integration_services):
        """Test caching integration across services."""
        user_service = integration_services["user_service"]
        cache = integration_services["cache"]

        # Create cached service wrapper
        cached_service = CachedUserService(user_service, cache)

        # Test cache miss → database hit
        user = await cached_service.get_user_cached(uuid4())
        assert user is None  # Not found

        # Create user
        created_user = await cached_service.create_user(
            "cached@example.com", "Cached User"
        )

        # Test cache hit
        cached_user = await cached_service.get_user_cached(created_user.id)
        assert cached_user is not None
        assert cached_user.id == created_user.id

        # Verify cache was used (check cache directly)
        cache_key = f"user:{created_user.id}"
        cached_data = await cache.get(cache_key)
        assert cached_data is not None
```

### Database Integration Testing

```python
class DatabaseIntegrationTests:
    """Integration tests with real database."""

    @pytest.fixture(scope="session")
    async def test_database():
        """Setup test database."""
        # Use PostgreSQL test container or SQLite for CI
        if os.getenv("CI"):
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        else:
            engine = create_async_engine(
                "postgresql+asyncpg://test:test@localhost/test_omnibase"
            )

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        # Cleanup
        if not os.getenv("CI"):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()

    @pytest.fixture
    async def db_session(self, test_database):
        """Provide database session for tests."""
        async_session = sessionmaker(
            test_database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session() as session:
            yield session
            await session.rollback()  # Rollback after each test

    @pytest.fixture
    def db_user_service(self, db_session):
        """Provide database user service."""
        return DatabaseUserService(session=db_session)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_user_service_compliance(self, db_user_service):
        """Test database service protocol compliance."""
        # Run the full compliance test suite
        compliance_tests = UserServiceComplianceTests()
        compliance_tests.user_service = lambda: db_user_service

        # Run all compliance tests
        await compliance_tests.test_create_user_success()
        await compliance_tests.test_create_user_invalid_email()
        await compliance_tests.test_get_user_existing()
        await compliance_tests.test_get_user_nonexistent()
        # ... other compliance tests

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_transaction_handling(self, db_user_service):
        """Test database transaction behavior."""
        # Test transaction rollback on error
        with pytest.raises(ValueError):
            async with db_user_service.transaction():
                await db_user_service.create_user("tx@example.com", "TX User")
                # Force error to trigger rollback
                await db_user_service.create_user("", "Invalid User")

        # Verify user was not created due to rollback
        users = await db_user_service.list_users()
        emails = [user.email for user in users]
        assert "tx@example.com" not in emails
```

## Performance Testing

### Protocol Performance Benchmarks

```python
import time
import asyncio
from statistics import mean, median, stdev
from dataclasses import dataclass
from typing import List

@dataclass
class PerformanceResult:
    """Performance test result."""
    operation: str
    total_time: float
    requests: int
    avg_time: float
    median_time: float
    min_time: float
    max_time: float
    std_dev: float
    requests_per_second: float

class ProtocolPerformanceTester:
    """Performance testing for protocol implementations."""

    async def benchmark_user_service(
        self,
        user_service: ProtocolUserService,
        num_operations: int = 1000
    ) -> Dict[str, PerformanceResult]:
        """Benchmark user service operations."""
        results = {}

        # Benchmark user creation
        create_times = []
        created_users = []

        for i in range(num_operations):
            start_time = time.perf_counter()
            try:
                user = await user_service.create_user(
                    f"perf{i}@example.com",
                    f"Performance User {i}"
                )
                created_users.append(user)
                end_time = time.perf_counter()
                create_times.append(end_time - start_time)
            except Exception:
                # Skip failed operations in performance test
                pass

        if create_times:
            total_time = sum(create_times)
            results["create_user"] = PerformanceResult(
                operation="create_user",
                total_time=total_time,
                requests=len(create_times),
                avg_time=mean(create_times),
                median_time=median(create_times),
                min_time=min(create_times),
                max_time=max(create_times),
                std_dev=stdev(create_times) if len(create_times) > 1 else 0,
                requests_per_second=len(create_times) / total_time
            )

        # Benchmark user retrieval
        if created_users:
            get_times = []

            for user in created_users[:min(num_operations, len(created_users))]:
                start_time = time.perf_counter()
                await user_service.get_user(user.id)
                end_time = time.perf_counter()
                get_times.append(end_time - start_time)

            total_time = sum(get_times)
            results["get_user"] = PerformanceResult(
                operation="get_user",
                total_time=total_time,
                requests=len(get_times),
                avg_time=mean(get_times),
                median_time=median(get_times),
                min_time=min(get_times),
                max_time=max(get_times),
                std_dev=stdev(get_times) if len(get_times) > 1 else 0,
                requests_per_second=len(get_times) / total_time
            )

        # Benchmark list users
        list_times = []
        for _ in range(min(10, num_operations // 100)):  # Less frequent operation
            start_time = time.perf_counter()
            await user_service.list_users()
            end_time = time.perf_counter()
            list_times.append(end_time - start_time)

        if list_times:
            total_time = sum(list_times)
            results["list_users"] = PerformanceResult(
                operation="list_users",
                total_time=total_time,
                requests=len(list_times),
                avg_time=mean(list_times),
                median_time=median(list_times),
                min_time=min(list_times),
                max_time=max(list_times),
                std_dev=stdev(list_times) if len(list_times) > 1 else 0,
                requests_per_second=len(list_times) / total_time
            )

        return results

    async def concurrent_benchmark(
        self,
        user_service: ProtocolUserService,
        concurrent_users: int = 10,
        operations_per_user: int = 100
    ) -> Dict[str, PerformanceResult]:
        """Benchmark concurrent access to user service."""

        async def user_workflow(user_id: int) -> List[float]:
            """Simulate user workflow operations."""
            times = []

            for i in range(operations_per_user):
                # Create user
                start_time = time.perf_counter()
                user = await user_service.create_user(
                    f"concurrent{user_id}_{i}@example.com",
                    f"Concurrent User {user_id}-{i}"
                )
                end_time = time.perf_counter()
                times.append(end_time - start_time)

                # Get user
                start_time = time.perf_counter()
                await user_service.get_user(user.id)
                end_time = time.perf_counter()
                times.append(end_time - start_time)

            return times

        # Run concurrent workflows
        start_time = time.perf_counter()
        tasks = [user_workflow(i) for i in range(concurrent_users)]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.perf_counter()

        # Aggregate results
        all_times = []
        successful_tasks = 0

        for result in results_list:
            if isinstance(result, list):
                all_times.extend(result)
                successful_tasks += 1

        total_time = end_time - start_time

        return {
            "concurrent_operations": PerformanceResult(
                operation="concurrent_operations",
                total_time=total_time,
                requests=len(all_times),
                avg_time=mean(all_times) if all_times else 0,
                median_time=median(all_times) if all_times else 0,
                min_time=min(all_times) if all_times else 0,
                max_time=max(all_times) if all_times else 0,
                std_dev=stdev(all_times) if len(all_times) > 1 else 0,
                requests_per_second=len(all_times) / total_time if total_time > 0 else 0
            )
        }

# Performance test integration
@pytest.mark.asyncio
@pytest.mark.performance
async def test_user_service_performance():
    """Test user service performance benchmarks."""
    # Test multiple implementations
    implementations = [
        ("InMemory", InMemoryUserService()),
        ("Database", DatabaseUserService("sqlite:///:memory:")),
    ]

    tester = ProtocolPerformanceTester()

    for name, service in implementations:
        print(f"\nBenchmarking {name} implementation:")

        results = await tester.benchmark_user_service(service, num_operations=1000)

        for operation, result in results.items():
            print(f"{operation}:")
            print(f"  Average: {result.avg_time*1000:.2f}ms")
            print(f"  Median: {result.median_time*1000:.2f}ms")
            print(f"  RPS: {result.requests_per_second:.2f}")
            print(f"  Std Dev: {result.std_dev*1000:.2f}ms")

            # Performance assertions (adjust thresholds as needed)
            if operation == "create_user":
                assert result.avg_time < 0.1, f"{name} create_user too slow: {result.avg_time}s"
                assert result.requests_per_second > 10, f"{name} create_user RPS too low"
            elif operation == "get_user":
                assert result.avg_time < 0.01, f"{name} get_user too slow: {result.avg_time}s"
                assert result.requests_per_second > 100, f"{name} get_user RPS too low"

@pytest.mark.asyncio
@pytest.mark.performance  
async def test_concurrent_performance():
    """Test concurrent access performance."""
    service = InMemoryUserService()
    tester = ProtocolPerformanceTester()

    results = await tester.concurrent_benchmark(
        service,
        concurrent_users=5,
        operations_per_user=20
    )

    concurrent_result = results["concurrent_operations"]
    print(f"\nConcurrent Performance:")
    print(f"  Total operations: {concurrent_result.requests}")
    print(f"  Total time: {concurrent_result.total_time:.2f}s")
    print(f"  Average per operation: {concurrent_result.avg_time*1000:.2f}ms")
    print(f"  Operations per second: {concurrent_result.requests_per_second:.2f}")

    # Assert reasonable concurrent performance
    assert concurrent_result.requests_per_second > 50, "Concurrent performance too low"
    assert concurrent_result.avg_time < 0.1, "Average operation time too high"
```

## End-to-End Testing

### Complete Workflow Testing

```python
class EndToEndWorkflowTests:
    """End-to-end testing of complete workflows."""

    @pytest.fixture
    async def e2e_system(self):
        """Setup complete system for E2E testing."""
        # Use lightweight implementations for E2E tests
        container = ServiceContainer()

        # Register services
        container.register_singleton(
            ProtocolLogger,
            ConsoleLogger(level="DEBUG")
        )
        container.register_singleton(
            ProtocolCacheService,
            InMemoryCache()
        )
        container.register_singleton(
            ProtocolUserService,
            InMemoryUserService()
        )
        container.register_singleton(
            ProtocolWorkflowEventBus,
            InMemoryEventBus()
        )

        return container

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_complete_user_lifecycle_workflow(self, e2e_system):
        """Test complete user lifecycle from creation to deletion."""

        # Get services
        user_service = e2e_system.get(ProtocolUserService)
        logger = e2e_system.get(ProtocolLogger)
        cache = e2e_system.get(ProtocolCacheService)
        event_bus = e2e_system.get(ProtocolWorkflowEventBus)

        workflow_instance_id = uuid4()
        correlation_id = uuid4()

        # Track workflow events
        workflow_events = []

        async def workflow_event_handler(event: ProtocolWorkflowEvent, context: dict):
            workflow_events.append(event)

        await event_bus.subscribe_to_workflow_events(
            workflow_type="user_lifecycle",
            event_types=[
                "user.creation_started", "user.created", "user.updated",
                "user.deleted", "workflow.completed"
            ],
            handler=workflow_event_handler,
            group_id="e2e_test"
        )

        try:
            # Step 1: Start workflow
            await logger.info("Starting user lifecycle workflow", context={
                "workflow_instance_id": str(workflow_instance_id),
                "correlation_id": str(correlation_id)
            })

            start_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="user.creation_started",
                workflow_type="user_lifecycle",
                instance_id=workflow_instance_id,
                sequence_number=1,
                timestamp=datetime.now(),
                data={"email": "e2e@example.com", "name": "E2E User"},
                metadata={"correlation_id": str(correlation_id)},
                idempotency_key=f"user-lifecycle-{workflow_instance_id}-start",
                source_node_id="e2e-test"
            )
            await event_bus.publish_workflow_event(start_event)

            # Step 2: Create user
            user = await user_service.create_user("e2e@example.com", "E2E User")

            # Cache user
            cache_key = f"user:{user.id}"
            await cache.set(cache_key, user, ttl_seconds=300)

            # Publish creation event
            created_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="user.created",
                workflow_type="user_lifecycle",
                instance_id=workflow_instance_id,
                sequence_number=2,
                causation_id=start_event.event_id,
                timestamp=datetime.now(),
                data={"user_id": str(user.id), "email": user.email},
                metadata={"correlation_id": str(correlation_id)},
                idempotency_key=f"user-created-{user.id}",
                source_node_id="e2e-test"
            )
            await event_bus.publish_workflow_event(created_event)

            # Step 3: Update user
            await user_service.update_user(user.id, {"name": "Updated E2E User"})

            # Update cache
            updated_user = await user_service.get_user(user.id)
            await cache.set(cache_key, updated_user, ttl_seconds=300)

            # Publish update event
            updated_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="user.updated",
                workflow_type="user_lifecycle",
                instance_id=workflow_instance_id,
                sequence_number=3,
                causation_id=created_event.event_id,
                timestamp=datetime.now(),
                data={"user_id": str(user.id), "changes": {"name": "Updated E2E User"}},
                metadata={"correlation_id": str(correlation_id)},
                idempotency_key=f"user-updated-{user.id}-1",
                source_node_id="e2e-test"
            )
            await event_bus.publish_workflow_event(updated_event)

            # Step 4: Delete user
            await user_service.delete_user(user.id)

            # Remove from cache
            await cache.delete(cache_key)

            # Publish deletion event
            deleted_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="user.deleted",
                workflow_type="user_lifecycle",
                instance_id=workflow_instance_id,
                sequence_number=4,
                causation_id=updated_event.event_id,
                timestamp=datetime.now(),
                data={"user_id": str(user.id)},
                metadata={"correlation_id": str(correlation_id)},
                idempotency_key=f"user-deleted-{user.id}",
                source_node_id="e2e-test"
            )
            await event_bus.publish_workflow_event(deleted_event)

            # Step 5: Complete workflow
            completion_event = ProtocolWorkflowEvent(
                event_id=uuid4(),
                event_type="workflow.completed",
                workflow_type="user_lifecycle",
                instance_id=workflow_instance_id,
                sequence_number=5,
                causation_id=deleted_event.event_id,
                timestamp=datetime.now(),
                data={"status": "completed", "user_id": str(user.id)},
                metadata={"correlation_id": str(correlation_id)},
                idempotency_key=f"workflow-completed-{workflow_instance_id}",
                source_node_id="e2e-test"
            )
            await event_bus.publish_workflow_event(completion_event)

            # Wait for event processing
            await asyncio.sleep(1)

            # Verify complete workflow
            assert len(workflow_events) == 5

            # Verify event sequence
            event_types = [event.event_type for event in workflow_events]
            expected_sequence = [
                "user.creation_started", "user.created", "user.updated",
                "user.deleted", "workflow.completed"
            ]
            assert event_types == expected_sequence

            # Verify causation chain
            assert workflow_events[1].causation_id == workflow_events[0].event_id
            assert workflow_events[2].causation_id == workflow_events[1].event_id
            assert workflow_events[3].causation_id == workflow_events[2].event_id
            assert workflow_events[4].causation_id == workflow_events[3].event_id

            # Verify user is deleted
            deleted_user = await user_service.get_user(user.id)
            assert deleted_user is None

            # Verify cache is cleared
            cached_user = await cache.get(cache_key)
            assert cached_user is None

            # Log completion
            await logger.info("E2E workflow completed successfully", context={
                "workflow_instance_id": str(workflow_instance_id),
                "events_processed": len(workflow_events)
            })

        except Exception as e:
            await logger.error("E2E workflow failed", context={
                "error": str(e),
                "workflow_instance_id": str(workflow_instance_id)
            })
            raise
```

## Test Infrastructure

### Test Configuration and Fixtures

```python
# conftest.py - Global test configuration
import pytest
import asyncio
import os
from typing import AsyncGenerator

# Configure asyncio for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

# Test environment setup
@pytest.fixture(scope="session")
def test_environment():
    """Setup test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    yield

    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)
    os.environ.pop("DATABASE_URL", None)

# Protocol test utilities
@pytest.fixture
def protocol_tester():
    """Provide protocol testing utilities."""
    return ProtocolTestUtilities()

class ProtocolTestUtilities:
    """Utilities for protocol testing."""

    def assert_protocol_compliance(self, obj: object, protocol: type):
        """Assert object implements protocol."""
        assert isinstance(obj, protocol), f"{type(obj)} must implement {protocol}"

    def assert_protocol_method_signatures(self, obj: object, protocol: type):
        """Assert method signatures match protocol."""
        import inspect

        protocol_methods = [
            name for name, method in inspect.getmembers(protocol, inspect.isfunction)
            if not name.startswith('_')
        ]

        for method_name in protocol_methods:
            assert hasattr(obj, method_name), f"Missing method: {method_name}"

            # Check signature compatibility (basic check)
            protocol_sig = inspect.signature(getattr(protocol, method_name))
            obj_sig = inspect.signature(getattr(obj, method_name))

            # Basic parameter count check
            assert len(protocol_sig.parameters) == len(obj_sig.parameters), (
                f"Parameter count mismatch for {method_name}"
            )
```

## Summary

This testing guide provides comprehensive strategies for:

1. **Protocol Compliance**: Ensure all implementations satisfy protocol contracts
2. **Mock Testing**: Create realistic mocks with stateful behavior
3. **Integration Testing**: Test multi-service workflows with real implementations
4. **Performance Testing**: Benchmark protocol implementations and identify bottlenecks
5. **End-to-End Testing**: Verify complete system workflows
6. **Test Infrastructure**: Setup robust test environments and utilities

**Key Testing Principles:**

- **Protocol-First**: Test contracts, not implementations
- **Comprehensive Coverage**: Unit, integration, performance, and E2E tests
- **Realistic Mocking**: Stateful mocks that behave like real implementations
- **Performance Awareness**: Benchmark implementations and prevent regressions
- **Workflow Testing**: Verify complete business workflows work correctly

These testing strategies ensure robust, reliable protocol-based applications that meet performance requirements and maintain correctness across all service boundaries.

---

*For implementation examples, see the [Developer Guide](developer-guide/README.md). For specific protocol documentation, see the [API Reference](api-reference/).*
