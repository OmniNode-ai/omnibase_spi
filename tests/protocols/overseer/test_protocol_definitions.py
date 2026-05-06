# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for overseer protocol definitions.

Validates that ProtocolCodeRepository, ProtocolArtifactStore, and
ProtocolNotificationService:
- Are importable from omnibase_spi.protocols.overseer
- Are runtime-checkable
- Accept structural subtype implementations via isinstance
- Expose the expected method signatures
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

from omnibase_spi.protocols.overseer import (
    ProtocolArtifactStore,
    ProtocolCodeRepository,
    ProtocolNotificationService,
)

# ---------------------------------------------------------------------------
# Minimal concrete stubs (structural subtypes — no inheritance required)
# ---------------------------------------------------------------------------


class _StubCodeRepository:
    """Minimal structural implementation of ProtocolCodeRepository."""

    async def connect(self) -> bool:
        return True

    async def health_check(self) -> Any:
        return object()

    async def get_capabilities(self) -> list[str]:
        return ["read", "write", "admin"]

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass

    async def get_pr(self, repo: str, pr_number: int) -> Any:
        return object()

    async def list_prs(
        self, repo: str, state: str = "open", limit: int = 50
    ) -> list[Any]:
        return []

    async def get_ci_status(self, repo: str, ref: str) -> Any:
        return object()

    async def get_diff(self, repo: str, base: str, head: str) -> Any:
        return object()

    async def push_branch(
        self,
        repo: str,
        branch_name: str,
        from_ref: str = "main",
    ) -> Any:
        return object()

    async def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
    ) -> Any:
        return object()

    async def admin_merge(
        self,
        repo: str,
        pr_number: int,
        method: str = "squash",
    ) -> Any:
        return object()

    async def force_push(
        self,
        repo: str,
        branch_name: str,
        target_ref: str,
    ) -> Any:
        return object()

    async def delete_branch(self, repo: str, branch_name: str) -> bool:
        return True

    async def rebase(
        self,
        repo: str,
        branch_name: str,
        onto: str = "main",
    ) -> Any:
        return object()


class _StubArtifactStore:
    """Minimal structural implementation of ProtocolArtifactStore."""

    async def connect(self) -> bool:
        return True

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        return key

    async def get(self, key: str) -> bytes:
        return b""

    async def delete(self, key: str) -> bool:
        return True

    async def exists(self, key: str) -> bool:
        return False

    async def list(self, prefix: str = "", limit: int = 1000) -> list[str]:
        return []

    async def get_metadata(self, key: str) -> dict[str, str]:
        return {}


class _StubNotificationService:
    """Minimal structural implementation of ProtocolNotificationService."""

    async def connect(self) -> bool:
        return True

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass

    async def send(
        self,
        channel: str,
        title: str,
        body: str,
        level: str = "info",
        metadata: dict[str, str] | None = None,
    ) -> bool:
        return True

    async def send_batch(
        self,
        channel: str,
        notifications: list[dict[str, Any]],
    ) -> int:
        return len(notifications)

    async def health_check(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------


def test_protocol_code_repository_importable() -> None:
    """ProtocolCodeRepository is importable from omnibase_spi.protocols.overseer."""
    assert ProtocolCodeRepository is not None


def test_protocol_artifact_store_importable() -> None:
    """ProtocolArtifactStore is importable from omnibase_spi.protocols.overseer."""
    assert ProtocolArtifactStore is not None


def test_protocol_notification_service_importable() -> None:
    """ProtocolNotificationService is importable from omnibase_spi.protocols.overseer."""
    assert ProtocolNotificationService is not None


# ---------------------------------------------------------------------------
# Runtime-checkable tests
# ---------------------------------------------------------------------------


def test_code_repository_is_runtime_checkable() -> None:
    """ProtocolCodeRepository accepts structural subtypes via isinstance."""
    stub = _StubCodeRepository()
    assert isinstance(stub, ProtocolCodeRepository)


def test_artifact_store_is_runtime_checkable() -> None:
    """ProtocolArtifactStore accepts structural subtypes via isinstance."""
    stub = _StubArtifactStore()
    assert isinstance(stub, ProtocolArtifactStore)


def test_notification_service_is_runtime_checkable() -> None:
    """ProtocolNotificationService accepts structural subtypes via isinstance."""
    stub = _StubNotificationService()
    assert isinstance(stub, ProtocolNotificationService)


def test_non_conforming_object_rejected_by_code_repository() -> None:
    """Objects missing required methods do not satisfy ProtocolCodeRepository."""
    assert not isinstance(object(), ProtocolCodeRepository)


def test_non_conforming_object_rejected_by_artifact_store() -> None:
    """Objects missing required methods do not satisfy ProtocolArtifactStore."""
    assert not isinstance(object(), ProtocolArtifactStore)


def test_non_conforming_object_rejected_by_notification_service() -> None:
    """Objects missing required methods do not satisfy ProtocolNotificationService."""
    assert not isinstance(object(), ProtocolNotificationService)


# ---------------------------------------------------------------------------
# Method-presence tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method_name",
    [
        "connect",
        "health_check",
        "get_capabilities",
        "close",
        "get_pr",
        "list_prs",
        "get_ci_status",
        "get_diff",
        "push_branch",
        "create_pr",
        "admin_merge",
        "force_push",
        "delete_branch",
        "rebase",
    ],
)
def test_code_repository_has_method(method_name: str) -> None:
    """ProtocolCodeRepository declares all required methods."""
    assert hasattr(ProtocolCodeRepository, method_name), (
        f"ProtocolCodeRepository is missing method: {method_name}"
    )
    assert callable(getattr(ProtocolCodeRepository, method_name))


@pytest.mark.parametrize(
    "method_name",
    [
        "connect",
        "close",
        "put",
        "get",
        "delete",
        "exists",
        "list",
        "get_metadata",
    ],
)
def test_artifact_store_has_method(method_name: str) -> None:
    """ProtocolArtifactStore declares all required methods."""
    assert hasattr(ProtocolArtifactStore, method_name), (
        f"ProtocolArtifactStore is missing method: {method_name}"
    )
    assert callable(getattr(ProtocolArtifactStore, method_name))


@pytest.mark.parametrize(
    "method_name",
    [
        "connect",
        "close",
        "send",
        "send_batch",
        "health_check",
    ],
)
def test_notification_service_has_method(method_name: str) -> None:
    """ProtocolNotificationService declares all required methods."""
    assert hasattr(ProtocolNotificationService, method_name), (
        f"ProtocolNotificationService is missing method: {method_name}"
    )
    assert callable(getattr(ProtocolNotificationService, method_name))


# ---------------------------------------------------------------------------
# Async-method tests
# ---------------------------------------------------------------------------


def test_code_repository_methods_are_async() -> None:
    """All ProtocolCodeRepository methods are coroutine functions."""
    stub = _StubCodeRepository()
    for name in [
        "connect",
        "health_check",
        "get_capabilities",
        "close",
        "get_pr",
        "list_prs",
        "get_ci_status",
        "get_diff",
        "push_branch",
        "create_pr",
        "admin_merge",
        "force_push",
        "delete_branch",
        "rebase",
    ]:
        assert inspect.iscoroutinefunction(getattr(stub, name)), (
            f"_StubCodeRepository.{name} is not async"
        )


def test_artifact_store_methods_are_async() -> None:
    """All ProtocolArtifactStore methods are coroutine functions."""
    stub = _StubArtifactStore()
    for name in [
        "connect",
        "close",
        "put",
        "get",
        "delete",
        "exists",
        "list",
        "get_metadata",
    ]:
        assert inspect.iscoroutinefunction(getattr(stub, name)), (
            f"_StubArtifactStore.{name} is not async"
        )


def test_notification_service_methods_are_async() -> None:
    """All ProtocolNotificationService methods are coroutine functions."""
    stub = _StubNotificationService()
    for name in ["connect", "close", "send", "send_batch", "health_check"]:
        assert inspect.iscoroutinefunction(getattr(stub, name)), (
            f"_StubNotificationService.{name} is not async"
        )
