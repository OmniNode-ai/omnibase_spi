# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Unit tests for ProtocolPrimitiveEffectExecutorV2 SPI protocol (OMN-4220).

Validates:
- ProtocolPrimitiveEffectExecutorV2 is @runtime_checkable
- ProtocolHttpRequestContract is @runtime_checkable
- ProtocolHttpResponseContract is @runtime_checkable
- execute_http() and execute_kafka_produce() are async (SPI005 compliant)
- isinstance() checks work correctly for compliant/non-compliant classes
- Zero upstream deps: only stdlib imports used in the module under test
- Export from omnibase_spi.protocols and omnibase_spi top-level package
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from omnibase_spi.protocols.primitive_effect_executor import (
    ProtocolHttpRequestContract,
    ProtocolHttpResponseContract,
    ProtocolPrimitiveEffectExecutorV2,
)

# Path to the module under test (used for zero-dep AST check)
_MODULE_PATH = (
    Path(__file__).parent.parent.parent.parent.parent
    / "src"
    / "omnibase_spi"
    / "protocols"
    / "primitive_effect_executor.py"
)


# ---------------------------------------------------------------------------
# Minimal compliant implementations for isinstance checks
# ---------------------------------------------------------------------------


class ConcreteHttpRequest:
    """Minimal implementation of ProtocolHttpRequestContract."""

    @property
    def method(self) -> str:
        return "POST"

    @property
    def url(self) -> str:
        return "https://example.com/api"

    @property
    def headers(self) -> dict[str, str] | None:
        return {"Content-Type": "application/json"}

    @property
    def body(self) -> bytes | None:
        return b'{"key": "value"}'

    @property
    def timeout_seconds(self) -> float | None:
        return 10.0


class ConcreteHttpResponse:
    """Minimal implementation of ProtocolHttpResponseContract."""

    @property
    def status_code(self) -> int:
        return 200

    @property
    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    @property
    def body(self) -> bytes:
        return b'{"result": "ok"}'


class ConcreteEffectExecutor:
    """Minimal implementation of ProtocolPrimitiveEffectExecutorV2."""

    async def execute_http(
        self,
        request: ProtocolHttpRequestContract,
    ) -> ProtocolHttpResponseContract:
        return ConcreteHttpResponse()

    async def execute_kafka_produce(
        self,
        topic: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        pass


class MissingExecuteHttpExecutor:
    """Only implements execute_kafka_produce — missing execute_http."""

    async def execute_kafka_produce(
        self,
        topic: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        pass


class MissingKafkaExecutor:
    """Only implements execute_http — missing execute_kafka_produce."""

    async def execute_http(
        self,
        request: ProtocolHttpRequestContract,
    ) -> ProtocolHttpResponseContract:
        return ConcreteHttpResponse()


class EmptyClass:
    """Neither method implemented."""

    pass


# ---------------------------------------------------------------------------
# Tests: ProtocolHttpRequestContract
# ---------------------------------------------------------------------------


class TestProtocolHttpRequestContract:
    """Tests for ProtocolHttpRequestContract protocol."""

    @pytest.mark.unit
    def test_is_runtime_checkable(self) -> None:
        """ProtocolHttpRequestContract must be @runtime_checkable."""
        req = ConcreteHttpRequest()
        assert isinstance(req, ProtocolHttpRequestContract)

    @pytest.mark.unit
    def test_non_compliant_fails_isinstance(self) -> None:
        """Object missing required properties fails isinstance check."""
        assert not isinstance(EmptyClass(), ProtocolHttpRequestContract)

    @pytest.mark.unit
    def test_protocol_cannot_be_instantiated_directly(self) -> None:
        """Protocol cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProtocolHttpRequestContract()  # type: ignore[misc]

    @pytest.mark.unit
    def test_compliant_impl_has_all_required_properties(self) -> None:
        """Compliant implementation exposes all required contract properties."""
        req = ConcreteHttpRequest()
        assert req.method == "POST"
        assert req.url == "https://example.com/api"
        assert req.headers is not None
        assert req.body is not None
        assert req.timeout_seconds == 10.0

    @pytest.mark.unit
    def test_optional_fields_can_be_none(self) -> None:
        """headers, body, and timeout_seconds are optional (can be None)."""

        class MinimalRequest:
            @property
            def method(self) -> str:
                return "GET"

            @property
            def url(self) -> str:
                return "https://example.com"

            @property
            def headers(self) -> dict[str, str] | None:
                return None

            @property
            def body(self) -> bytes | None:
                return None

            @property
            def timeout_seconds(self) -> float | None:
                return None

        req = MinimalRequest()
        assert isinstance(req, ProtocolHttpRequestContract)
        assert req.headers is None
        assert req.body is None
        assert req.timeout_seconds is None


# ---------------------------------------------------------------------------
# Tests: ProtocolHttpResponseContract
# ---------------------------------------------------------------------------


class TestProtocolHttpResponseContract:
    """Tests for ProtocolHttpResponseContract protocol."""

    @pytest.mark.unit
    def test_is_runtime_checkable(self) -> None:
        """ProtocolHttpResponseContract must be @runtime_checkable."""
        resp = ConcreteHttpResponse()
        assert isinstance(resp, ProtocolHttpResponseContract)

    @pytest.mark.unit
    def test_non_compliant_fails_isinstance(self) -> None:
        """Object missing required properties fails isinstance check."""
        assert not isinstance(EmptyClass(), ProtocolHttpResponseContract)

    @pytest.mark.unit
    def test_protocol_cannot_be_instantiated_directly(self) -> None:
        """Protocol cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProtocolHttpResponseContract()  # type: ignore[misc]

    @pytest.mark.unit
    def test_compliant_impl_has_all_required_properties(self) -> None:
        """Compliant implementation exposes all required contract properties."""
        resp = ConcreteHttpResponse()
        assert resp.status_code == 200
        assert isinstance(resp.headers, dict)
        assert isinstance(resp.body, bytes)


# ---------------------------------------------------------------------------
# Tests: ProtocolPrimitiveEffectExecutorV2
# ---------------------------------------------------------------------------


class TestProtocolPrimitiveEffectExecutorV2:
    """Tests for ProtocolPrimitiveEffectExecutorV2 protocol."""

    @pytest.mark.unit
    def test_is_runtime_checkable(self) -> None:
        """ProtocolPrimitiveEffectExecutorV2 must be @runtime_checkable."""
        executor = ConcreteEffectExecutor()
        assert isinstance(executor, ProtocolPrimitiveEffectExecutorV2)

    @pytest.mark.unit
    def test_missing_execute_http_fails_isinstance(self) -> None:
        """Object missing execute_http() fails isinstance check."""
        assert not isinstance(
            MissingExecuteHttpExecutor(), ProtocolPrimitiveEffectExecutorV2
        )

    @pytest.mark.unit
    def test_missing_kafka_produce_fails_isinstance(self) -> None:
        """Object missing execute_kafka_produce() fails isinstance check."""
        assert not isinstance(MissingKafkaExecutor(), ProtocolPrimitiveEffectExecutorV2)

    @pytest.mark.unit
    def test_empty_class_fails_isinstance(self) -> None:
        """Empty class with no methods fails isinstance check."""
        assert not isinstance(EmptyClass(), ProtocolPrimitiveEffectExecutorV2)

    @pytest.mark.unit
    def test_protocol_cannot_be_instantiated_directly(self) -> None:
        """Protocol cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProtocolPrimitiveEffectExecutorV2()  # type: ignore[misc]

    @pytest.mark.unit
    def test_execute_http_is_async(self) -> None:
        """execute_http() must be a coroutine function."""
        executor = ConcreteEffectExecutor()
        assert inspect.iscoroutinefunction(executor.execute_http)

    @pytest.mark.unit
    def test_execute_kafka_produce_is_async(self) -> None:
        """execute_kafka_produce() must be a coroutine function."""
        executor = ConcreteEffectExecutor()
        assert inspect.iscoroutinefunction(executor.execute_kafka_produce)

    @pytest.mark.unit
    def test_protocol_attrs_contain_required_methods(self) -> None:
        """Protocol.__protocol_attrs__ must contain both required methods."""
        attrs = ProtocolPrimitiveEffectExecutorV2.__protocol_attrs__
        assert "execute_http" in attrs
        assert "execute_kafka_produce" in attrs


# ---------------------------------------------------------------------------
# Tests: zero upstream dependency check (AST-level)
# ---------------------------------------------------------------------------


class TestZeroDependencyConstraint:
    """Verify module under test has zero imports from L2+ libraries."""

    @pytest.mark.unit
    def test_no_omnibase_core_imports(self) -> None:
        """Module must not import from omnibase_core."""
        source = _MODULE_PATH.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("omnibase_core"), (
                        f"Forbidden import: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not module.startswith("omnibase_core"), (
                    f"Forbidden import from: {module}"
                )

    @pytest.mark.unit
    def test_no_omnibase_infra_imports(self) -> None:
        """Module must not import from omnibase_infra."""
        source = _MODULE_PATH.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("omnibase_infra"), (
                        f"Forbidden import: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not module.startswith("omnibase_infra"), (
                    f"Forbidden import from: {module}"
                )

    @pytest.mark.unit
    def test_only_stdlib_imports(self) -> None:
        """Module imports must be from stdlib only (typing and __future__)."""
        allowed_modules = {"__future__", "typing"}
        source = _MODULE_PATH.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                top_level = module.split(".")[0]
                assert top_level in allowed_modules, (
                    f"Non-stdlib import detected: {module!r}. "
                    f"Only {allowed_modules} are allowed."
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split(".")[0]
                    assert top_level in allowed_modules, (
                        f"Non-stdlib import detected: {alias.name!r}."
                    )


# ---------------------------------------------------------------------------
# Tests: public API export checks
# ---------------------------------------------------------------------------


class TestPublicAPIExports:
    """Verify the protocol is exported from expected package locations."""

    @pytest.mark.unit
    def test_import_from_protocols_module(self) -> None:
        """ProtocolPrimitiveEffectExecutorV2 can be imported from omnibase_spi.protocols."""
        from omnibase_spi.protocols import ProtocolPrimitiveEffectExecutorV2 as PEE

        assert PEE is not None
        assert PEE is ProtocolPrimitiveEffectExecutorV2

    @pytest.mark.unit
    def test_import_http_request_contract_from_protocols(self) -> None:
        """ProtocolHttpRequestContract can be imported from omnibase_spi.protocols."""
        from omnibase_spi.protocols import ProtocolHttpRequestContract as HRC

        assert HRC is not None
        assert HRC is ProtocolHttpRequestContract

    @pytest.mark.unit
    def test_import_http_response_contract_from_protocols(self) -> None:
        """ProtocolHttpResponseContract can be imported from omnibase_spi.protocols."""
        from omnibase_spi.protocols import ProtocolHttpResponseContract as HReC

        assert HReC is not None
        assert HReC is ProtocolHttpResponseContract

    @pytest.mark.unit
    def test_import_from_top_level_package(self) -> None:
        """ProtocolPrimitiveEffectExecutorV2 can be imported from omnibase_spi top-level."""
        import omnibase_spi

        pee = omnibase_spi.ProtocolPrimitiveEffectExecutorV2  # type: ignore[attr-defined]
        assert pee is ProtocolPrimitiveEffectExecutorV2

    @pytest.mark.unit
    def test_in_protocols_all(self) -> None:
        """ProtocolPrimitiveEffectExecutorV2 appears in omnibase_spi.protocols.__all__."""
        import omnibase_spi.protocols as proto_mod

        assert "ProtocolPrimitiveEffectExecutorV2" in proto_mod.__all__
        assert "ProtocolHttpRequestContract" in proto_mod.__all__
        assert "ProtocolHttpResponseContract" in proto_mod.__all__
