# Quick Start Guide

## Overview

Get up and running with omnibase-spi in under 10 minutes. This guide walks you through installation, basic usage, and your first protocol implementation.

## Prerequisites

- **Python**: 3.11, 3.12, or 3.13
- **Poetry**: For dependency management ([install here](https://python-poetry.org/docs/#installation))
- **Git**: For version control

## Installation

### 1. Install omnibase-spi

```bash
# Option A: Install from PyPI (when available)
pip install omnibase-spi

# Option B: Install from source
git clone <omnibase-spi-repo>
cd omnibase-spi
poetry install
```

### 2. Verify Installation

```bash
# Test basic import
python -c "from omnibase_spi.protocols.core import ProtocolLogger; print('✅ Installation successful')"

# Check available protocols
python -c "from omnibase_spi.protocols import *; print('✅ All protocols imported')"
```

## 5-Minute Example: User Service

Let's create a simple user service to demonstrate the key concepts.

### Step 1: Use Existing Protocols

```python
# main.py
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from omnibase_spi.protocols.core import ProtocolLogger
from omnibase_spi.protocols.types.core_types import LogLevel, ContextValue

# First, let's create a simple user data structure
class User:
    def __init__(self, id: UUID, email: str, name: str, created_at: datetime):
        self.id = id
        self.email = email
        self.name = name
        self.created_at = created_at

# Simple in-memory user storage using protocol interfaces
class InMemoryUserService:
    """Simple user service implementation."""

    def __init__(self, logger: ProtocolLogger):
        self.users: dict[UUID, User] = {}
        self.logger = logger

    async def create_user(self, email: str, name: str) -> User:
        """Create a new user."""
        # Validate input
        if not email or "@" not in email:
            await self.logger.error(
                "Invalid email provided",
                context={"email": email, "name": name}
            )
            raise ValueError("Valid email required")

        if not name or len(name.strip()) == 0:
            await self.logger.error(
                "Empty name provided",
                context={"email": email, "name": name}
            )
            raise ValueError("Name cannot be empty")

        # Check for duplicate email
        for user in self.users.values():
            if user.email == email:
                await self.logger.warning(
                    "Duplicate email attempt",
                    context={"email": email}
                )
                raise ValueError(f"User with email {email} already exists")

        # Create user
        user = User(
            id=uuid4(),
            email=email,
            name=name,
            created_at=datetime.now()
        )

        self.users[user.id] = user

        await self.logger.info(
            "User created successfully",
            context={
                "user_id": str(user.id),
                "email": user.email,
                "name": user.name
            }
        )

        return user

    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        user = self.users.get(user_id)

        if user:
            await self.logger.debug(
                "User retrieved",
                context={"user_id": str(user_id), "found": True}
            )
        else:
            await self.logger.debug(
                "User not found",
                context={"user_id": str(user_id), "found": False}
            )

        return user

    async def list_users(self) -> list[User]:
        """List all users."""
        users = list(self.users.values())

        await self.logger.info(
            "Users listed",
            context={"count": len(users)}
        )

        return users

# Simple logger implementation for demonstration
class SimpleLogger(ProtocolLogger):
    """Simple console logger implementation."""

    async def log(
        self,
        level: LogLevel,
        message: str,
        context: dict[str, ContextValue]
    ) -> None:
        """Log message with context."""
        timestamp = datetime.now().isoformat()
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        print(f"[{timestamp}] {level}: {message} | {context_str}")

    async def debug(self, message: str, context: dict[str, ContextValue]) -> None:
        await self.log("DEBUG", message, context)

    async def info(self, message: str, context: dict[str, ContextValue]) -> None:
        await self.log("INFO", message, context)

    async def warning(self, message: str, context: dict[str, ContextValue]) -> None:
        await self.log("WARNING", message, context)

    async def error(self, message: str, context: dict[str, ContextValue]) -> None:
        await self.log("ERROR", message, context)

# Demo application
async def main():
    """Demonstrate basic user service functionality."""
    # Create logger
    logger = SimpleLogger()

    # Create user service
    user_service = InMemoryUserService(logger)

    print("🚀 Starting User Service Demo")
    print("-" * 40)

    try:
        # Create some users
        print("\n📝 Creating users...")
        alice = await user_service.create_user("alice@example.com", "Alice Smith")
        bob = await user_service.create_user("bob@example.com", "Bob Johnson")

        # List users
        print("\n📋 Listing all users...")
        users = await user_service.list_users()
        for user in users:
            print(f"  - {user.name} ({user.email}) - ID: {user.id}")

        # Get specific user
        print("\n🔍 Getting Alice's details...")
        retrieved_alice = await user_service.get_user(alice.id)
        if retrieved_alice:
            print(f"  Found: {retrieved_alice.name} - {retrieved_alice.email}")

        # Try to create duplicate user (will fail)
        print("\n❌ Attempting to create duplicate user...")
        try:
            await user_service.create_user("alice@example.com", "Alice Duplicate")
        except ValueError as e:
            print(f"  Expected error: {e}")

        # Try invalid data (will fail)
        print("\n❌ Attempting invalid user creation...")
        try:
            await user_service.create_user("invalid-email", "Test User")
        except ValueError as e:
            print(f"  Expected error: {e}")

        print("\n✅ Demo completed successfully!")

    except Exception as e:
        print(f"\n💥 Demo failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Step 2: Run the Example

```bash
# Run the demo
python main.py
```

Expected output:
```
🚀 Starting User Service Demo
----------------------------------------

📝 Creating users...
[2024-01-15T10:30:15] INFO: User created successfully | user_id=123e4567-..., email=alice@example.com, name=Alice Smith
[2024-01-15T10:30:15] INFO: User created successfully | user_id=987f6543-..., email=bob@example.com, name=Bob Johnson

📋 Listing all users...
[2024-01-15T10:30:15] INFO: Users listed | count=2
  - Alice Smith (alice@example.com) - ID: 123e4567-...
  - Bob Johnson (bob@example.com) - ID: 987f6543-...

🔍 Getting Alice's details...
[2024-01-15T10:30:15] DEBUG: User retrieved | user_id=123e4567-..., found=True
  Found: Alice Smith - alice@example.com

❌ Attempting to create duplicate user...
[2024-01-15T10:30:15] WARNING: Duplicate email attempt | email=alice@example.com
  Expected error: User with email alice@example.com already exists

❌ Attempting invalid user creation...
[2024-01-15T10:30:15] ERROR: Invalid email provided | email=invalid-email, name=Test User
  Expected error: Valid email required

✅ Demo completed successfully!
```

## Understanding the Example

### 1. Protocol Usage
```python
# We used the existing logger protocol
from omnibase_spi.protocols.core import ProtocolLogger

# Our service accepts any logger implementation
def __init__(self, logger: ProtocolLogger):
    self.logger = logger  # Can be any logger implementation
```

**Key Benefits:**
- **Dependency Inversion**: Service depends on interface, not implementation
- **Testability**: Easy to mock logger for testing
- **Flexibility**: Swap logger implementations without changing service code

### 2. Type Safety
```python
# Type-safe context values
context: dict[str, ContextValue] = {
    "user_id": str(user.id),    # str - allowed
    "email": user.email,        # str - allowed  
    "count": len(users)         # int - allowed
    # "user_obj": user          # User - not allowed (not ContextValue)
}
```

**Key Benefits:**
- **Compile-time Safety**: mypy catches type errors
- **Runtime Safety**: Constrained types prevent injection attacks
- **Clear Contracts**: Types serve as documentation

### 3. Error Handling
```python
# Structured error handling with logging
if not email or "@" not in email:
    await self.logger.error("Invalid email provided", context={...})
    raise ValueError("Valid email required")
```

**Key Benefits:**
- **Observability**: All errors are logged with context
- **Debugging**: Rich context for troubleshooting
- **Monitoring**: Structured logs enable alerting

## Next Steps

### Explore More Protocols

Try using other protocols from omnibase-spi:

```python
# Caching example
from omnibase_spi.protocols.core import ProtocolCacheService

class CachedUserService:
    def __init__(
        self,
        user_service: InMemoryUserService,
        cache: ProtocolCacheService
    ):
        self.user_service = user_service
        self.cache = cache

    async def get_user_cached(self, user_id: UUID) -> Optional[User]:
        # Try cache first
        cached_user = await self.cache.get(f"user:{user_id}")
        if cached_user:
            return cached_user

        # Get from service and cache
        user = await self.user_service.get_user(user_id)
        if user:
            await self.cache.set(f"user:{user_id}", user, ttl_seconds=300)

        return user
```

### Create Your Own Protocol

```python
# Define your own protocol
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProtocolEmailService(Protocol):
    """Protocol for email operations."""

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_address: Optional[str] = None
    ) -> bool:
        """Send email message."""
        ...

    async def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        body: str
    ) -> dict[str, bool]:
        """Send email to multiple recipients."""
        ...

# Implement the protocol
class SMTPEmailService(ProtocolEmailService):
    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    async def send_email(self, to: str, subject: str, body: str, from_address=None):
        print(f"📧 Sending email to {to}: {subject}")
        # SMTP implementation here
        return True

    async def send_bulk_email(self, recipients: list[str], subject: str, body: str):
        results = {}
        for recipient in recipients:
            results[recipient] = await self.send_email(recipient, subject, body)
        return results

# Use in your user service
class UserServiceWithEmail:
    def __init__(
        self,
        user_service: InMemoryUserService,
        email_service: ProtocolEmailService
    ):
        self.user_service = user_service
        self.email_service = email_service

    async def create_user_with_welcome_email(self, email: str, name: str) -> User:
        # Create user
        user = await self.user_service.create_user(email, name)

        # Send welcome email
        await self.email_service.send_email(
            to=user.email,
            subject="Welcome!",
            body=f"Hello {user.name}, welcome to our service!"
        )

        return user
```

### Advanced Patterns

Explore advanced patterns like:

1. **Event-Driven Architecture**: Use workflow orchestration protocols
2. **Multi-Subsystem Coordination**: Integrate MCP protocols  
3. **Distributed Computing**: Leverage node registry protocols
4. **Event Sourcing**: Build with event bus protocols

## Common Patterns

### Dependency Injection

```python
# Simple dependency injection container
class ServiceContainer:
    def __init__(self):
        self.services = {}

    def register(self, protocol: type, implementation):
        """Register service implementation."""
        self.services[protocol] = implementation

    def get(self, protocol: type):
        """Get service implementation."""
        return self.services[protocol]

# Setup container
container = ServiceContainer()
container.register(ProtocolLogger, SimpleLogger())
container.register(ProtocolEmailService, SMTPEmailService("smtp.example.com", 587))

# Use container
logger = container.get(ProtocolLogger)
email_service = container.get(ProtocolEmailService)
user_service = InMemoryUserService(logger)
```

### Testing with Protocols

```python
import pytest
from unittest.mock import AsyncMock

# Mock implementation for testing
class MockLogger(ProtocolLogger):
    def __init__(self):
        self.logs = []

    async def log(self, level: LogLevel, message: str, context: dict):
        self.logs.append({"level": level, "message": message, "context": context})

    async def info(self, message: str, context: dict):
        await self.log("INFO", message, context)

    async def error(self, message: str, context: dict):
        await self.log("ERROR", message, context)

# Test with mock
@pytest.mark.asyncio
async def test_user_creation():
    mock_logger = MockLogger()
    service = InMemoryUserService(mock_logger)

    user = await service.create_user("test@example.com", "Test User")

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert len(mock_logger.logs) == 1
    assert mock_logger.logs[0]["level"] == "INFO"
    assert "User created successfully" in mock_logger.logs[0]["message"]
```

## Troubleshooting

### Common Issues

#### Import Errors
```python
# ❌ Wrong import
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger

# ✅ Correct import  
from omnibase_spi.protocols.core import ProtocolLogger
```

#### Type Checking Errors
```python
# ❌ Using Any defeats type safety
async def process_data(self, data: Any) -> Any:
    ...

# ✅ Use specific types
async def process_user(self, user_data: dict[str, str]) -> User:
    ...
```

#### Protocol Compliance Issues
```python
# ❌ Missing @runtime_checkable
class ProtocolMyService(Protocol):  # Won't work with isinstance()
    async def do_something(self) -> None: ...

# ✅ Include @runtime_checkable
@runtime_checkable
class ProtocolMyService(Protocol):
    async def do_something(self) -> None: ...
```

### Getting Help

1. **Documentation**: Check the [Developer Guide](developer-guide/README.md)
2. **API Reference**: See [API Reference](api-reference/README.md)  
3. **Examples**: Look at existing protocol implementations
4. **Issues**: Report bugs or ask questions on the repository

## What's Next?

Now that you've got the basics working:

1. **Read the [Developer Guide](developer-guide/README.md)** for comprehensive coverage
2. **Explore [API Reference](api-reference/README.md)** for detailed protocol documentation
3. **Check [Architecture Overview](architecture/README.md)** to understand design patterns
4. **Review [Integration Guide](integration/README.md)** for framework-specific guidance
5. **Follow [Best Practices](best-practices/README.md)** for production-ready code

## Summary

You've successfully:

✅ **Installed omnibase-spi** and verified it works  
✅ **Created a user service** using protocol interfaces  
✅ **Implemented structured logging** with type safety  
✅ **Handled errors gracefully** with proper context  
✅ **Understood key concepts** like dependency inversion and type constraints  

**Key Takeaways:**
- **Protocols define contracts** - what services should do, not how
- **Type safety prevents errors** - use specific types instead of `Any`
- **Dependency inversion enables flexibility** - depend on interfaces
- **Structured logging aids debugging** - include rich context
- **Error handling should be comprehensive** - log and raise appropriately

Ready to build more complex applications with omnibase-spi protocols!

---

*This quick start guide gets you productive immediately. For deeper understanding, continue with the [Developer Guide](developer-guide/README.md).*
