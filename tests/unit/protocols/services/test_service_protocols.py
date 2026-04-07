# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Tests for service lifecycle protocols [OMN-7576].

Validates that ProtocolTicketService, ProtocolSecretStore, and ProtocolCodeHost:
- Are runtime checkable
- Accept isinstance checks against conforming implementations
- Are importable from both package and module paths
"""

from __future__ import annotations

import pytest

from omnibase_spi.protocols.services import (
    ProtocolCodeHost,
    ProtocolExternalService,
    ProtocolSecretStore,
    ProtocolTicketService,
)

# ---------------------------------------------------------------------------
# Stub implementations for isinstance checks
# ---------------------------------------------------------------------------


class _StubTicketService:
    async def create_ticket(
        self,
        title: str,
        description: str,
        labels: list[str] | None = None,
        assignee: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        return "OMN-0001"

    async def get_ticket(self, ticket_id: str) -> dict:
        return {}

    async def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        return True

    async def add_comment(self, ticket_id: str, body: str) -> str:
        return "comment-1"

    async def list_tickets(
        self, filters: dict | None = None, limit: int = 50
    ) -> list[dict]:
        return []

    async def get_ticket_status(self, ticket_id: str) -> str:
        return "open"

    async def health_check(self) -> bool:
        return True

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass


class _StubSecretStore:
    async def get_secret(self, key: str) -> str | None:
        return "secret-value"

    async def set_secret(self, key: str, value: str) -> bool:
        return True

    async def delete_secret(self, key: str) -> bool:
        return True

    async def list_keys(self, prefix: str | None = None) -> list[str]:
        return []

    async def health_check(self) -> bool:
        return True

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass


class _StubExternalService:
    async def connect(self) -> bool:
        return True

    async def health_check(self) -> object:
        return object()

    async def get_capabilities(self) -> list[str]:
        return ["read", "write"]

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass


class _StubCodeHost:
    async def create_pull_request(
        self,
        repo: str,
        head: str,
        base: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
        reviewers: list[str] | None = None,
        metadata: dict | None = None,
    ) -> str:
        return "https://github.com/org/repo/pull/1"

    async def get_pull_request(self, repo: str, pr_number: int) -> dict:
        return {}

    async def merge_pull_request(
        self, repo: str, pr_number: int, method: str = "squash"
    ) -> bool:
        return True

    async def add_pr_comment(self, repo: str, pr_number: int, body: str) -> str:
        return "comment-1"

    async def get_ci_status(self, repo: str, ref: str) -> dict:
        return {"state": "success"}

    async def list_pull_requests(
        self, repo: str, state: str = "open", limit: int = 50
    ) -> list[dict]:
        return []

    async def health_check(self) -> bool:
        return True

    async def close(self, timeout_seconds: float = 30.0) -> None:
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolExternalService:
    """ProtocolExternalService runtime checkability and structure."""

    def test_isinstance_check(self) -> None:
        assert isinstance(_StubExternalService(), ProtocolExternalService)

    def test_is_protocol(self) -> None:
        assert any(
            getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolExternalService.__mro__
        )

    def test_has_connect(self) -> None:
        assert hasattr(ProtocolExternalService, "connect")

    def test_has_health_check(self) -> None:
        assert hasattr(ProtocolExternalService, "health_check")

    def test_has_get_capabilities(self) -> None:
        assert hasattr(ProtocolExternalService, "get_capabilities")

    def test_has_close(self) -> None:
        assert hasattr(ProtocolExternalService, "close")

    def test_import_from_module(self) -> None:
        from omnibase_spi.protocols.services.protocol_external_service import (
            ProtocolExternalService as Direct,
        )

        assert Direct is ProtocolExternalService


@pytest.mark.unit
class TestProtocolTicketService:
    """ProtocolTicketService runtime checkability and structure."""

    def test_isinstance_check(self) -> None:
        assert isinstance(_StubTicketService(), ProtocolTicketService)

    def test_is_protocol(self) -> None:
        assert any(
            getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolTicketService.__mro__
        )

    def test_has_create_ticket(self) -> None:
        assert hasattr(ProtocolTicketService, "create_ticket")

    def test_has_health_check(self) -> None:
        assert hasattr(ProtocolTicketService, "health_check")

    def test_has_close(self) -> None:
        assert hasattr(ProtocolTicketService, "close")

    def test_import_from_module(self) -> None:
        from omnibase_spi.protocols.services.protocol_ticket_service import (
            ProtocolTicketService as Direct,
        )

        assert Direct is ProtocolTicketService


@pytest.mark.unit
class TestProtocolSecretStore:
    """ProtocolSecretStore runtime checkability and structure."""

    def test_isinstance_check(self) -> None:
        assert isinstance(_StubSecretStore(), ProtocolSecretStore)

    def test_is_protocol(self) -> None:
        assert any(
            getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolSecretStore.__mro__
        )

    def test_has_get_secret(self) -> None:
        assert hasattr(ProtocolSecretStore, "get_secret")

    def test_has_set_secret(self) -> None:
        assert hasattr(ProtocolSecretStore, "set_secret")

    def test_has_list_keys(self) -> None:
        assert hasattr(ProtocolSecretStore, "list_keys")

    def test_has_health_check(self) -> None:
        assert hasattr(ProtocolSecretStore, "health_check")

    def test_import_from_module(self) -> None:
        from omnibase_spi.protocols.services.protocol_secret_store import (
            ProtocolSecretStore as Direct,
        )

        assert Direct is ProtocolSecretStore


@pytest.mark.unit
class TestProtocolCodeHost:
    """ProtocolCodeHost runtime checkability and structure."""

    def test_isinstance_check(self) -> None:
        assert isinstance(_StubCodeHost(), ProtocolCodeHost)

    def test_is_protocol(self) -> None:
        assert any(
            getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolCodeHost.__mro__
        )

    def test_has_create_pull_request(self) -> None:
        assert hasattr(ProtocolCodeHost, "create_pull_request")

    def test_has_merge_pull_request(self) -> None:
        assert hasattr(ProtocolCodeHost, "merge_pull_request")

    def test_has_get_ci_status(self) -> None:
        assert hasattr(ProtocolCodeHost, "get_ci_status")

    def test_has_health_check(self) -> None:
        assert hasattr(ProtocolCodeHost, "health_check")

    def test_import_from_module(self) -> None:
        from omnibase_spi.protocols.services.protocol_code_host import (
            ProtocolCodeHost as Direct,
        )

        assert Direct is ProtocolCodeHost
