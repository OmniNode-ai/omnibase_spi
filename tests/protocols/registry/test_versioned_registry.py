"""Tests for ProtocolVersionedRegistry protocol.

This module provides:
1. Reference implementation (ReferenceVersionedRegistry) for testing
2. Comprehensive edge case tests for semver validation, version ordering, concurrency
3. Integration tests for base method delegation
"""

from __future__ import annotations

import asyncio
import re
from typing import TypeVar

import pytest

from omnibase_spi.protocols.registry import ProtocolVersionedRegistry

# Type variables for testing
K = TypeVar("K")
V = TypeVar("V")


# ========== REFERENCE IMPLEMENTATION ==========
# This is a complete, thread-safe reference implementation
# suitable for testing and serving as an example for implementers.


class ReferenceVersionedRegistry[K, V]:
    """
    Reference implementation of ProtocolVersionedRegistry for testing.

    This implementation demonstrates:
    - Proper semver validation
    - Thread-safe concurrent operations using asyncio.Lock
    - Base method delegation to version-aware methods
    - Correct version ordering (numeric, not lexicographic)

    Thread Safety:
        Uses asyncio.Lock to protect internal state. All operations
        are atomic and safe for concurrent access from multiple tasks.

    Storage Design:
        Internal storage: dict[K, dict[str, V]]
        - Outer dict maps keys to version dictionaries
        - Inner dict maps version strings to values
        - Empty inner dicts are removed after unregistering last version
    """

    def __init__(self) -> None:
        """Initialize empty versioned registry with thread-safe lock."""
        self._store: dict[K, dict[str, V]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _validate_semver(version: str) -> bool:
        """
        Validate strict semantic version format (MAJOR.MINOR.PATCH).

        Args:
            version: Version string to validate.

        Returns:
            True if version matches format, False otherwise.

        Valid Examples:
            "1.0.0", "2.1.3", "10.20.30", "0.0.1"

        Invalid Examples:
            "1.0" (missing PATCH)
            "v1.0.0" (prefix not allowed)
            "1.0.0-beta" (pre-release not supported)
            "01.0.0" (leading zeros not allowed except "0")
        """
        # Pattern: non-negative integers, no leading zeros (except "0")
        pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
        return bool(re.match(pattern, version))

    @staticmethod
    def _parse_semver(version: str) -> tuple[int, int, int]:
        """
        Parse semantic version string into (major, minor, patch) tuple.

        Args:
            version: Semantic version string (must be pre-validated).

        Returns:
            Tuple of (major, minor, patch) integers.

        Raises:
            ValueError: If version format is invalid.
        """
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid semver format: {version}")
        try:
            return int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError as e:
            raise ValueError(f"Invalid semver components: {version}") from e

    async def register_version(self, key: K, version: str, value: V) -> None:
        """Register a specific version of a key-value pair."""
        if not self._validate_semver(version):
            raise ValueError(
                f"Invalid semantic version format: {version!r}. "
                f"Expected MAJOR.MINOR.PATCH (e.g., '1.0.0')"
            )

        async with self._lock:
            if key not in self._store:
                self._store[key] = {}
            self._store[key][version] = value

    async def get_version(self, key: K, version: str) -> V:
        """Retrieve a specific version of a registered value."""
        async with self._lock:
            if key not in self._store:
                raise KeyError(f"Key not registered: {key!r}")
            if version not in self._store[key]:
                raise KeyError(f"Version {version!r} not found for key {key!r}")
            return self._store[key][version]

    async def get_latest(self, key: K) -> V:
        """Retrieve the latest version of a registered value."""
        async with self._lock:
            if key not in self._store or not self._store[key]:
                raise KeyError(f"Key not registered: {key!r}")

            # Find highest semver using numeric comparison
            latest_version = max(self._store[key].keys(), key=self._parse_semver)
            return self._store[key][latest_version]

    async def list_versions(self, key: K) -> list[str]:
        """List all registered versions for a key in ascending semver order."""
        async with self._lock:
            if key not in self._store or not self._store[key]:
                return []
            # Sort by semver tuple (numeric comparison)
            return sorted(self._store[key].keys(), key=self._parse_semver)

    async def get_all_versions(self, key: K) -> dict[str, V]:
        """Retrieve all versions of a registered key as a mapping."""
        async with self._lock:
            if key not in self._store:
                return {}
            # Return a copy to prevent external mutations
            return dict(self._store[key])

    # ===== Base Registry Methods (Async with Delegation) =====

    async def register(self, key: K, value: V) -> None:
        """
        Register a key-value pair (delegates to register_version).

        Version selection strategy:
        - New key: Use "0.0.1"
        - Existing key: Increment latest version's PATCH component
        """
        async with self._lock:
            if key in self._store and self._store[key]:
                # Key exists: increment PATCH of latest version
                latest_version = max(self._store[key].keys(), key=self._parse_semver)
                major, minor, patch = self._parse_semver(latest_version)
                new_version = f"{major}.{minor}.{patch + 1}"
            else:
                # New key: start at "0.0.1"
                new_version = "0.0.1"

        # Release lock before delegating (register_version acquires its own lock)
        await self.register_version(key, new_version, value)

    async def get(self, key: K) -> V:
        """Retrieve latest version (delegates to get_latest)."""
        return await self.get_latest(key)

    async def list_keys(self) -> list[K]:
        """List all registered keys."""
        async with self._lock:
            # Return keys that have at least one version
            return [k for k, versions in self._store.items() if versions]

    async def is_registered(self, key: K) -> bool:
        """Check if a key has any registered versions."""
        async with self._lock:
            return key in self._store and bool(self._store[key])

    async def unregister(self, key: K) -> bool:
        """Remove ALL versions of a key from the registry."""
        async with self._lock:
            if key in self._store and self._store[key]:
                del self._store[key]
                return True
            return False


# ========== FIXTURES ==========


@pytest.fixture
def registry() -> ReferenceVersionedRegistry[str, type]:
    """Create a fresh reference registry for each test."""
    return ReferenceVersionedRegistry[str, type]()


# ========== PROTOCOL CONFORMANCE TESTS ==========


@pytest.mark.asyncio
async def test_protocol_conformance() -> None:
    """Verify ReferenceVersionedRegistry conforms to ProtocolVersionedRegistry."""
    registry = ReferenceVersionedRegistry[str, str]()
    assert isinstance(registry, ProtocolVersionedRegistry)


# ========== SEMVER VALIDATION EDGE CASES ==========


@pytest.mark.asyncio
async def test_semver_valid_formats(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test valid semantic version formats are accepted."""
    valid_versions = [
        "0.0.1",  # Minimum version
        "1.0.0",  # Simple major release
        "2.1.3",  # All components non-zero
        "10.20.30",  # Multi-digit components
        "0.0.0",  # All zeros (edge case)
        "999.999.999",  # Large numbers
    ]

    for version in valid_versions:
        await registry.register_version("test-key", version, str)
        # Verify it was stored
        result = await registry.get_version("test-key", version)
        assert result is str


@pytest.mark.asyncio
async def test_semver_invalid_formats(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test invalid semantic version formats are rejected."""
    invalid_versions = [
        ("1.0", "missing PATCH component"),
        ("v1.0.0", "prefix not allowed"),
        ("1.0.0-beta", "pre-release identifier not supported"),
        ("01.0.0", "leading zero in MAJOR"),
        ("1.00.0", "leading zero in MINOR"),
        ("1.0.00", "leading zero in PATCH"),
        ("latest", "non-numeric version"),
        ("", "empty string"),
        ("1.0.0.0", "too many components"),
        ("1.-1.0", "negative component"),
        ("1.0.x", "non-numeric component"),
        ("1.0.", "trailing dot"),
        (".1.0.0", "leading dot"),
        ("1..0.0", "double dot"),
    ]

    for version, reason in invalid_versions:
        with pytest.raises(ValueError, match="Invalid semantic version format"):
            await registry.register_version("test-key", version, str)


# ========== VERSION ORDERING EDGE CASES ==========


@pytest.mark.asyncio
async def test_version_ordering_numeric_not_lexicographic(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test version ordering uses numeric comparison, not string comparison."""

    class V1:
        pass

    class V2:
        pass

    class V3:
        pass

    class V4:
        pass

    # Register versions in non-sorted order
    await registry.register_version("api", "9.9.9", V1)
    await registry.register_version("api", "10.0.0", V2)  # Should be > 9.9.9
    await registry.register_version("api", "1.0.9", V3)
    await registry.register_version("api", "1.0.10", V4)  # Should be > 1.0.9

    # Verify list_versions returns numeric sorted order
    versions = await registry.list_versions("api")
    assert versions == ["1.0.9", "1.0.10", "9.9.9", "10.0.0"]

    # Verify get_latest returns highest numeric version
    latest = await registry.get_latest("api")
    assert latest is V2  # 10.0.0 is highest


@pytest.mark.asyncio
async def test_version_ordering_patch_component(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test PATCH component ordering is numeric."""

    class V1:
        pass

    class V2:
        pass

    class V3:
        pass

    await registry.register_version("lib", "1.0.8", V1)
    await registry.register_version("lib", "1.0.9", V2)
    await registry.register_version("lib", "1.0.10", V3)

    versions = await registry.list_versions("lib")
    assert versions == ["1.0.8", "1.0.9", "1.0.10"]

    latest = await registry.get_latest("lib")
    assert latest is V3  # 1.0.10 > 1.0.9


@pytest.mark.asyncio
async def test_version_ordering_major_component_dominates(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test MAJOR component has highest precedence in ordering."""

    class V1:
        pass

    class V2:
        pass

    await registry.register_version("app", "1.999.999", V1)
    await registry.register_version("app", "2.0.0", V2)

    latest = await registry.get_latest("app")
    assert latest is V2  # 2.0.0 > 1.999.999


# ========== CONCURRENT OPERATIONS (THREAD SAFETY) ==========


@pytest.mark.asyncio
async def test_concurrent_register_version_different_versions(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test concurrent registration of different versions is safe."""

    class V1:
        pass

    class V2:
        pass

    class V3:
        pass

    # Concurrently register different versions of same key
    await asyncio.gather(
        registry.register_version("api", "1.0.0", V1),
        registry.register_version("api", "2.0.0", V2),
        registry.register_version("api", "3.0.0", V3),
    )

    # Verify all versions were stored
    assert await registry.get_version("api", "1.0.0") is V1
    assert await registry.get_version("api", "2.0.0") is V2
    assert await registry.get_version("api", "3.0.0") is V3

    # Verify list_versions is consistent
    versions = await registry.list_versions("api")
    assert versions == ["1.0.0", "2.0.0", "3.0.0"]


@pytest.mark.asyncio
async def test_concurrent_get_latest_while_registering(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test get_latest() consistency during concurrent registrations."""

    class V1:
        pass

    class V2:
        pass

    class V3:
        pass

    # Pre-register initial version
    await registry.register_version("api", "1.0.0", V1)

    # Concurrently read latest while registering new versions
    async def register_newer_versions() -> None:
        await registry.register_version("api", "2.0.0", V2)
        await asyncio.sleep(0.01)  # Simulate some delay
        await registry.register_version("api", "3.0.0", V3)

    async def read_latest_multiple_times() -> list[type]:
        results = []
        for _ in range(5):
            results.append(await registry.get_latest("api"))
            await asyncio.sleep(0.005)
        return results

    # Run concurrently
    _, read_results = await asyncio.gather(
        register_newer_versions(),
        read_latest_multiple_times(),
    )

    # Verify reads returned valid versions (V1, V2, or V3)
    valid_versions = {V1, V2, V3}
    assert all(result in valid_versions for result in read_results)

    # Final latest should be highest version
    final_latest = await registry.get_latest("api")
    assert final_latest is V3


@pytest.mark.asyncio
async def test_concurrent_list_versions_consistency(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test list_versions() returns consistent snapshot during modifications."""

    class Handler:
        pass

    # Pre-register some versions
    await registry.register_version("api", "1.0.0", Handler)

    async def register_versions() -> None:
        for patch in range(1, 6):
            await registry.register_version("api", f"1.0.{patch}", Handler)
            await asyncio.sleep(0.001)

    async def list_versions_multiple_times() -> list[list[str]]:
        results = []
        for _ in range(10):
            results.append(await registry.list_versions("api"))
            await asyncio.sleep(0.002)
        return results

    # Run concurrently
    _, list_results = await asyncio.gather(
        register_versions(),
        list_versions_multiple_times(),
    )

    # Verify all results are valid snapshots (sorted, no corruption)
    for versions_snapshot in list_results:
        # Each snapshot should be sorted
        assert versions_snapshot == sorted(
            versions_snapshot, key=ReferenceVersionedRegistry._parse_semver
        )
        # Should not be empty (at least "1.0.0" exists)
        assert len(versions_snapshot) >= 1


# ========== EMPTY REGISTRY EDGE CASES ==========


@pytest.mark.asyncio
async def test_get_latest_on_nonexistent_key(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test get_latest() raises KeyError for non-existent key."""
    with pytest.raises(KeyError, match="Key not registered"):
        await registry.get_latest("nonexistent")


@pytest.mark.asyncio
async def test_get_version_on_nonexistent_key(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test get_version() raises KeyError for non-existent key."""
    with pytest.raises(KeyError, match="Key not registered"):
        await registry.get_version("nonexistent", "1.0.0")


@pytest.mark.asyncio
async def test_get_version_on_nonexistent_version(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test get_version() raises KeyError for non-existent version."""

    class V1:
        pass

    await registry.register_version("api", "1.0.0", V1)

    with pytest.raises(KeyError, match="Version .* not found"):
        await registry.get_version("api", "2.0.0")


@pytest.mark.asyncio
async def test_list_versions_on_nonexistent_key(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test list_versions() returns empty list for non-existent key."""
    versions = await registry.list_versions("nonexistent")
    assert versions == []


@pytest.mark.asyncio
async def test_get_all_versions_on_nonexistent_key(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test get_all_versions() returns empty dict for non-existent key."""
    all_versions = await registry.get_all_versions("nonexistent")
    assert all_versions == {}


@pytest.mark.asyncio
async def test_is_registered_on_empty_registry(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test is_registered() returns False for non-existent key."""
    assert not await registry.is_registered("nonexistent")


@pytest.mark.asyncio
async def test_unregister_on_empty_registry(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test unregister() returns False for non-existent key (idempotent)."""
    result = await registry.unregister("nonexistent")
    assert result is False


# ========== BASE METHOD DELEGATION ==========


@pytest.mark.asyncio
async def test_register_creates_version_0_0_1_for_new_key(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test register() creates version "0.0.1" for new keys."""

    class Handler:
        pass

    await registry.register("new-key", Handler)

    # Verify version "0.0.1" was created
    result = await registry.get_version("new-key", "0.0.1")
    assert result is Handler

    # Verify it's the latest
    latest = await registry.get_latest("new-key")
    assert latest is Handler


@pytest.mark.asyncio
async def test_register_increments_patch_for_existing_key(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test register() increments PATCH component for existing keys."""

    class V1:
        pass

    class V2:
        pass

    class V3:
        pass

    # Register initial version
    await registry.register_version("api", "1.0.0", V1)

    # Use register() - should create "1.0.1"
    await registry.register("api", V2)
    assert await registry.get_version("api", "1.0.1") is V2

    # Use register() again - should create "1.0.2"
    await registry.register("api", V3)
    assert await registry.get_version("api", "1.0.2") is V3


@pytest.mark.asyncio
async def test_get_delegates_to_get_latest(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test get() returns same result as get_latest()."""

    class V1:
        pass

    class V2:
        pass

    await registry.register_version("api", "1.0.0", V1)
    await registry.register_version("api", "2.0.0", V2)

    latest = await registry.get_latest("api")
    via_get = await registry.get("api")

    assert latest is via_get is V2


@pytest.mark.asyncio
async def test_unregister_removes_all_versions(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test unregister() removes ALL versions of a key."""

    class V1:
        pass

    class V2:
        pass

    class V3:
        pass

    await registry.register_version("api", "1.0.0", V1)
    await registry.register_version("api", "2.0.0", V2)
    await registry.register_version("api", "3.0.0", V3)

    # Unregister should remove ALL versions
    result = await registry.unregister("api")
    assert result is True

    # Verify all versions are gone
    assert await registry.list_versions("api") == []
    assert not await registry.is_registered("api")

    with pytest.raises(KeyError):
        await registry.get_version("api", "1.0.0")


@pytest.mark.asyncio
async def test_unregister_is_idempotent(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test unregister() can be called multiple times safely."""

    class Handler:
        pass

    await registry.register_version("api", "1.0.0", Handler)

    # First unregister returns True
    assert await registry.unregister("api") is True

    # Second unregister returns False (already removed)
    assert await registry.unregister("api") is False

    # Third unregister still returns False
    assert await registry.unregister("api") is False


@pytest.mark.asyncio
async def test_list_keys_returns_keys_with_versions(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test list_keys() returns only keys with at least one version."""

    class Handler:
        pass

    await registry.register_version("api-v1", "1.0.0", Handler)
    await registry.register_version("api-v2", "2.0.0", Handler)

    keys = await registry.list_keys()
    assert set(keys) == {"api-v1", "api-v2"}

    # Unregister one key
    await registry.unregister("api-v1")

    keys = await registry.list_keys()
    assert keys == ["api-v2"]


# ========== INTEGRATION TESTS ==========


@pytest.mark.asyncio
async def test_full_lifecycle(registry: ReferenceVersionedRegistry[str, type]) -> None:
    """Test complete lifecycle: register, query, update, unregister."""

    class PolicyV1:
        pass

    class PolicyV2:
        pass

    class PolicyV3:
        pass

    # 1. Register multiple versions
    await registry.register_version("rate-limit", "1.0.0", PolicyV1)
    await registry.register_version("rate-limit", "1.1.0", PolicyV2)
    await registry.register_version("rate-limit", "2.0.0", PolicyV3)

    # 2. Query versions
    assert await registry.is_registered("rate-limit")
    assert await registry.get_version("rate-limit", "1.0.0") is PolicyV1
    assert await registry.get_latest("rate-limit") is PolicyV3

    versions = await registry.list_versions("rate-limit")
    assert versions == ["1.0.0", "1.1.0", "2.0.0"]

    all_versions = await registry.get_all_versions("rate-limit")
    assert all_versions == {
        "1.0.0": PolicyV1,
        "1.1.0": PolicyV2,
        "2.0.0": PolicyV3,
    }

    # 3. Base methods work correctly
    assert await registry.get("rate-limit") is PolicyV3  # Delegates to get_latest
    assert "rate-limit" in await registry.list_keys()

    # 4. Unregister removes all
    assert await registry.unregister("rate-limit") is True
    assert not await registry.is_registered("rate-limit")
    assert await registry.list_versions("rate-limit") == []


@pytest.mark.asyncio
async def test_mixed_concurrent_operations(
    registry: ReferenceVersionedRegistry[str, type],
) -> None:
    """Test mixed concurrent reads and writes are safe."""

    class Handler:
        pass

    # Pre-register some versions
    for major in range(1, 4):
        await registry.register_version("api", f"{major}.0.0", Handler)

    async def register_new_versions() -> None:
        for minor in range(1, 4):
            await registry.register_version("api", f"3.{minor}.0", Handler)
            await asyncio.sleep(0.001)

    async def read_operations() -> None:
        for _ in range(10):
            await registry.get_latest("api")
            await registry.list_versions("api")
            await registry.is_registered("api")
            await asyncio.sleep(0.002)

    # Run mixed operations concurrently
    await asyncio.gather(
        register_new_versions(),
        read_operations(),
        read_operations(),  # Multiple readers
    )

    # Verify final state is consistent
    versions = await registry.list_versions("api")
    assert "1.0.0" in versions
    assert "3.0.0" in versions
    assert len(versions) >= 6  # At least initial 3 + new 3
