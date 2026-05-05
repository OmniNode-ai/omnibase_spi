# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Semantics tests for ``ProtocolSecretStore`` (OMN-10556).

These tests lock the protocol's behavioral contract so downstream
implementations (Infisical wrapper, env adapter, fake) cannot drift:

* ``get_secret`` is *nullable lookup* — missing keys yield ``None``, not an
  exception.
* ``set_secret`` / ``delete_secret`` may raise ``RuntimeError`` for read-only
  implementations; this is part of the public contract.
* ``runtime_checkable`` ``isinstance`` confirms attribute presence; the
  ``await``-based assertions below confirm async-signature compatibility,
  which ``isinstance`` cannot.
* ``get_secrets_batch`` is intentionally absent.
"""

from __future__ import annotations

import pytest

from omnibase_spi.protocols.services.protocol_secret_store import (
    ProtocolSecretStore,
)


class _StubReadOnlySecretStore:
    """Minimal in-test stub. Read-only — set/delete raise RuntimeError."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        self._data: dict[str, str] = dict(data or {})

    async def get_secret(self, key: str) -> str | None:
        return self._data.get(key)

    async def set_secret(self, key: str, value: str) -> bool:
        raise RuntimeError("stub is read-only")

    async def delete_secret(self, key: str) -> bool:
        raise RuntimeError("stub is read-only")

    async def list_keys(self, prefix: str | None = None) -> list[str]:
        if prefix is None:
            return sorted(self._data.keys())
        return sorted(k for k in self._data if k.startswith(prefix))

    async def health_check(self) -> bool:
        return True

    async def close(self, timeout_seconds: float = 30.0) -> None:
        return None


@pytest.mark.unit
def test_stub_satisfies_runtime_checkable_protocol() -> None:
    assert isinstance(_StubReadOnlySecretStore(), ProtocolSecretStore)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_secret_returns_none_on_miss_not_exception() -> None:
    store = _StubReadOnlySecretStore({"present": "value"})
    assert await store.get_secret("absent") is None
    assert await store.get_secret("present") == "value"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_set_secret_may_raise_runtime_error_for_read_only_impls() -> None:
    store = _StubReadOnlySecretStore()
    with pytest.raises(RuntimeError):
        await store.set_secret("k", "v")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_secret_may_raise_runtime_error_for_read_only_impls() -> None:
    store = _StubReadOnlySecretStore({"k": "v"})
    with pytest.raises(RuntimeError):
        await store.delete_secret("k")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_keys_accepts_none_prefix() -> None:
    store = _StubReadOnlySecretStore({"a": "1", "b": "2"})
    keys = await store.list_keys(prefix=None)
    assert keys == ["a", "b"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_keys_filters_by_prefix() -> None:
    store = _StubReadOnlySecretStore(
        {"llm/openai": "k1", "db/pg": "k2", "llm/anthropic": "k3"}
    )
    keys = await store.list_keys(prefix="llm/")
    assert keys == ["llm/anthropic", "llm/openai"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_returns_bool() -> None:
    store = _StubReadOnlySecretStore()
    result = await store.health_check()
    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_close_accepts_default_timeout_and_returns_none() -> None:
    store = _StubReadOnlySecretStore()
    await store.close()
    await store.close(timeout_seconds=5.0)


@pytest.mark.unit
def test_protocol_does_not_define_get_secrets_batch() -> None:
    """Batch retrieval is a performance concern, not part of the protocol."""
    assert not hasattr(ProtocolSecretStore, "get_secrets_batch")
