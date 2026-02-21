"""
Unit tests for ProtocolNodeProjectionEffect and ContractProjectionResult.

Validates:
- ContractProjectionResult is a frozen Pydantic model with the required fields.
- ProtocolEffect is @runtime_checkable and defines a synchronous execute().
- ProtocolNodeProjectionEffect extends ProtocolEffect and is @runtime_checkable.
- isinstance() checks work correctly for compliant and non-compliant classes.
- execute() is synchronous (not async) on compliant implementations.
- Failures are signalled via exceptions, not via success=False results.
- Export surface: all types are reachable from the expected import paths.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.projections.contract_projection_result import (
    ContractProjectionResult,
)
from omnibase_spi.effects.node_projection_effect import ProtocolNodeProjectionEffect
from omnibase_spi.exceptions import ProjectorError
from omnibase_spi.protocols.effects.protocol_effect import ProtocolEffect

# ---------------------------------------------------------------------------
# Minimal compliant implementations for testing
# ---------------------------------------------------------------------------


class _SuccessEffect:
    """Minimal compliant ProtocolNodeProjectionEffect — always succeeds."""

    def execute(self, intent: object) -> ContractProjectionResult:
        """Write projection and return success result."""
        return ContractProjectionResult(success=True, artifact_ref="ref-001")


class _NoOpEffect:
    """Compliant effect that returns success=False for an idempotent skip."""

    def execute(self, intent: object) -> ContractProjectionResult:
        """Return no-op result without raising."""
        return ContractProjectionResult(
            success=False,
            artifact_ref=None,
            error="Sequence already applied; skipped.",
        )


class _FailingEffect:
    """Compliant effect that raises ProjectorError on failure."""

    def execute(self, intent: object) -> ContractProjectionResult:
        """Raise ProjectorError on infrastructure failure."""
        raise ProjectorError(
            "Persistence layer unavailable",
            context={"operation": "execute", "entity_id": "e1"},
        )


class _AsyncEffect:
    """NON-compliant — uses async execute(), violates synchronous contract."""

    async def execute(  # type: ignore[override]
        self, intent: object
    ) -> ContractProjectionResult:
        """Async execute — violates the synchronous contract."""
        return ContractProjectionResult(success=True, artifact_ref="async-ref")


class _NoExecuteEffect:
    """NON-compliant — missing execute() entirely."""

    def other_method(self) -> None:
        """Some unrelated method."""
        ...


# ---------------------------------------------------------------------------
# ContractProjectionResult tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractProjectionResult:
    """Tests for the ContractProjectionResult Pydantic model."""

    def test_success_construction(self) -> None:
        """Construct a successful result with an artifact reference."""
        result = ContractProjectionResult(success=True, artifact_ref="proj-123")

        assert result.success is True
        assert result.artifact_ref == "proj-123"
        assert result.error is None

    def test_noop_construction(self) -> None:
        """Construct a no-op result (success=False, no artifact ref)."""
        result = ContractProjectionResult(
            success=False,
            artifact_ref=None,
            error="Sequence already applied.",
        )

        assert result.success is False
        assert result.artifact_ref is None
        assert result.error == "Sequence already applied."

    def test_defaults(self) -> None:
        """artifact_ref and error default to None."""
        result = ContractProjectionResult(success=True)

        assert result.artifact_ref is None
        assert result.error is None

    def test_frozen_model(self) -> None:
        """ContractProjectionResult instances are immutable (frozen=True)."""
        result = ContractProjectionResult(success=True, artifact_ref="ref-001")

        with pytest.raises((ValidationError, TypeError)):
            result.success = False  # type: ignore[misc]

    def test_extra_fields_ignored(self) -> None:
        """Extra fields are silently ignored (extra='ignore')."""
        result = ContractProjectionResult(
            success=True,
            artifact_ref="ref-999",
            unexpected_field="should be ignored",  # type: ignore[call-arg]
        )
        assert result.success is True
        assert not hasattr(result, "unexpected_field")

    def test_success_field_is_required(self) -> None:
        """Omitting success raises a ValidationError."""
        with pytest.raises(ValidationError):
            ContractProjectionResult()  # type: ignore[call-arg]

    def test_artifact_ref_optional(self) -> None:
        """artifact_ref accepts None explicitly."""
        result = ContractProjectionResult(success=True, artifact_ref=None)
        assert result.artifact_ref is None

    def test_error_optional(self) -> None:
        """error accepts None explicitly."""
        result = ContractProjectionResult(success=False, error=None)
        assert result.error is None

    def test_model_config_frozen(self) -> None:
        """model_config has frozen=True."""
        config = ContractProjectionResult.model_config
        assert config.get("frozen") is True

    def test_model_config_extra_ignore(self) -> None:
        """model_config has extra='ignore'."""
        config = ContractProjectionResult.model_config
        assert config.get("extra") == "ignore"

    def test_from_attributes(self) -> None:
        """model_config has from_attributes=True."""
        config = ContractProjectionResult.model_config
        assert config.get("from_attributes") is True

    def test_equality(self) -> None:
        """Two ContractProjectionResult instances with same values are equal."""
        r1 = ContractProjectionResult(success=True, artifact_ref="x")
        r2 = ContractProjectionResult(success=True, artifact_ref="x")
        assert r1 == r2

    def test_inequality(self) -> None:
        """Different artifact_ref values produce unequal results."""
        r1 = ContractProjectionResult(success=True, artifact_ref="x")
        r2 = ContractProjectionResult(success=True, artifact_ref="y")
        assert r1 != r2


# ---------------------------------------------------------------------------
# ProtocolEffect tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolEffect:
    """Tests for the ProtocolEffect protocol."""

    def test_is_runtime_checkable(self) -> None:
        """ProtocolEffect must be decorated with @runtime_checkable."""
        assert hasattr(ProtocolEffect, "_is_runtime_protocol") or hasattr(
            ProtocolEffect, "__runtime_protocol__"
        )

    def test_defines_execute_method(self) -> None:
        """ProtocolEffect must define an execute method."""
        assert "execute" in dir(ProtocolEffect)

    def test_cannot_be_instantiated(self) -> None:
        """ProtocolEffect should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEffect()  # type: ignore[misc]

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class with a synchronous execute() satisfies ProtocolEffect."""
        effect = _SuccessEffect()
        assert isinstance(effect, ProtocolEffect)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class missing execute() does not satisfy ProtocolEffect."""
        non_effect = _NoExecuteEffect()
        assert not isinstance(non_effect, ProtocolEffect)


# ---------------------------------------------------------------------------
# ProtocolNodeProjectionEffect protocol tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolNodeProjectionEffectProtocol:
    """Tests for the ProtocolNodeProjectionEffect protocol definition."""

    def test_is_runtime_checkable(self) -> None:
        """ProtocolNodeProjectionEffect must be decorated with @runtime_checkable."""
        assert hasattr(ProtocolNodeProjectionEffect, "_is_runtime_protocol") or hasattr(
            ProtocolNodeProjectionEffect, "__runtime_protocol__"
        )

    def test_has_protocol_prefix(self) -> None:
        """Protocol class name must start with 'Protocol'."""
        assert ProtocolNodeProjectionEffect.__name__.startswith("Protocol")

    def test_defines_execute_method(self) -> None:
        """ProtocolNodeProjectionEffect must define an execute method."""
        assert "execute" in dir(ProtocolNodeProjectionEffect)

    def test_cannot_be_instantiated(self) -> None:
        """ProtocolNodeProjectionEffect should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolNodeProjectionEffect()  # type: ignore[misc]

    def test_is_subprotocol_of_protocol_effect(self) -> None:
        """ProtocolNodeProjectionEffect must extend ProtocolEffect."""
        assert issubclass(ProtocolNodeProjectionEffect, ProtocolEffect)

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class with a synchronous execute() satisfies ProtocolNodeProjectionEffect."""
        effect = _SuccessEffect()
        assert isinstance(effect, ProtocolNodeProjectionEffect)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class without execute() fails ProtocolNodeProjectionEffect isinstance check."""
        non_effect = _NoExecuteEffect()
        assert not isinstance(non_effect, ProtocolNodeProjectionEffect)


# ---------------------------------------------------------------------------
# Synchronous contract tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolNodeProjectionEffectSynchronousContract:
    """Verify that execute() is and must be synchronous."""

    def test_success_effect_execute_is_not_coroutine(self) -> None:
        """execute() on a compliant implementation must not return a coroutine."""
        effect = _SuccessEffect()
        result = effect.execute(object())
        # If execute() were async the result would be a coroutine, not ContractProjectionResult
        assert not inspect.iscoroutine(result), (
            "execute() returned a coroutine — it must be synchronous"
        )

    def test_success_effect_execute_is_not_async_method(self) -> None:
        """The execute method itself must not be an async function."""
        assert not inspect.iscoroutinefunction(_SuccessEffect.execute)

    def test_failing_effect_execute_is_not_async_method(self) -> None:
        """Even raising effects must use a synchronous execute()."""
        assert not inspect.iscoroutinefunction(_FailingEffect.execute)

    def test_async_effect_isinstance_behaviour_documented(self) -> None:
        """Document that @runtime_checkable cannot distinguish sync vs async execute().

        Python's @runtime_checkable only checks method *presence*, not
        async vs sync.  This test documents the known limitation: isinstance()
        passes for async implementations.  Enforcement of sync/async is a
        type-checker and code-review responsibility.
        """
        # Async effect has an 'execute' attribute, so isinstance passes.
        async_effect = _AsyncEffect()
        assert isinstance(async_effect, ProtocolEffect)

    def test_execute_returns_contract_projection_result(self) -> None:
        """execute() must return a ContractProjectionResult on success."""
        effect = _SuccessEffect()
        result = effect.execute({"entity_id": "e1", "domain": "orders"})

        assert isinstance(result, ContractProjectionResult)
        assert result.success is True
        assert result.artifact_ref == "ref-001"


# ---------------------------------------------------------------------------
# Error-raising behaviour tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolNodeProjectionEffectErrorHandling:
    """Verify that execute() raises on infrastructure failure."""

    def test_failing_effect_raises_projector_error(self) -> None:
        """execute() must raise ProjectorError on infrastructure failure."""
        effect = _FailingEffect()

        with pytest.raises(ProjectorError) as exc_info:
            effect.execute({"entity_id": "e1", "domain": "orders"})

        assert "Persistence layer unavailable" in str(exc_info.value)
        assert exc_info.value.context["operation"] == "execute"

    def test_noop_effect_returns_success_false_without_raising(self) -> None:
        """For idempotent skips, success=False is acceptable without raising."""
        effect = _NoOpEffect()
        result = effect.execute({"entity_id": "e1", "domain": "orders"})

        assert isinstance(result, ContractProjectionResult)
        assert result.success is False
        assert result.artifact_ref is None
        assert result.error is not None


# ---------------------------------------------------------------------------
# Import surface tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestImportSurface:
    """Verify that new types are reachable from the expected import paths."""

    def test_contract_projection_result_importable_from_contracts_projections(
        self,
    ) -> None:
        """ContractProjectionResult is importable from omnibase_spi.contracts.projections."""
        from omnibase_spi.contracts.projections import (
            ContractProjectionResult as CPR,
        )

        assert CPR is ContractProjectionResult

    def test_protocol_node_projection_effect_importable_from_effects(self) -> None:
        """ProtocolNodeProjectionEffect is importable from omnibase_spi.effects."""
        from omnibase_spi.effects import (
            ProtocolNodeProjectionEffect as PNPE,
        )

        assert PNPE is ProtocolNodeProjectionEffect

    def test_protocol_effect_importable_from_protocols_effects(self) -> None:
        """ProtocolEffect is importable from omnibase_spi.protocols.effects."""
        from omnibase_spi.protocols.effects import ProtocolEffect as PE

        assert PE is ProtocolEffect

    def test_protocol_effect_in_protocols_all(self) -> None:
        """ProtocolEffect appears in omnibase_spi.protocols.__all__."""
        from omnibase_spi import protocols

        assert "ProtocolEffect" in protocols.__all__

    def test_protocol_node_projection_effect_importable_from_root(self) -> None:
        """ProtocolNodeProjectionEffect is lazily importable from omnibase_spi root."""
        import omnibase_spi

        pnpe = omnibase_spi.ProtocolNodeProjectionEffect
        assert pnpe is ProtocolNodeProjectionEffect

    def test_contract_projection_result_importable_from_root(self) -> None:
        """ContractProjectionResult is lazily importable from omnibase_spi root."""
        import omnibase_spi

        cpr = omnibase_spi.ContractProjectionResult
        assert cpr is ContractProjectionResult

    def test_protocol_effect_importable_from_root(self) -> None:
        """ProtocolEffect is lazily importable from omnibase_spi root."""
        import omnibase_spi

        pe = omnibase_spi.ProtocolEffect
        assert pe is ProtocolEffect


# ---------------------------------------------------------------------------
# Cross-reference: both protocols satisfied
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCrossProtocolCompliance:
    """Ensure compliant implementations satisfy both ProtocolEffect and ProtocolNodeProjectionEffect."""

    def test_success_effect_satisfies_protocol_effect(self) -> None:
        """_SuccessEffect satisfies ProtocolEffect."""
        assert isinstance(_SuccessEffect(), ProtocolEffect)

    def test_success_effect_satisfies_protocol_node_projection_effect(self) -> None:
        """_SuccessEffect satisfies ProtocolNodeProjectionEffect."""
        assert isinstance(_SuccessEffect(), ProtocolNodeProjectionEffect)

    def test_noop_effect_satisfies_both_protocols(self) -> None:
        """_NoOpEffect satisfies both ProtocolEffect and ProtocolNodeProjectionEffect."""
        noop = _NoOpEffect()
        assert isinstance(noop, ProtocolEffect)
        assert isinstance(noop, ProtocolNodeProjectionEffect)

    def test_failing_effect_satisfies_both_protocols(self) -> None:
        """_FailingEffect satisfies both protocols even though it raises."""
        failing = _FailingEffect()
        assert isinstance(failing, ProtocolEffect)
        assert isinstance(failing, ProtocolNodeProjectionEffect)


# ---------------------------------------------------------------------------
# Regression: existing ProtocolPrimitiveEffectExecutor unaffected
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNoRegressionOnPrimitiveEffectExecutor:
    """Ensure that adding ProtocolEffect does not break existing SPI exports."""

    def test_primitive_effect_executor_still_importable(self) -> None:
        """ProtocolPrimitiveEffectExecutor remains importable after the change."""
        from omnibase_spi.protocols.effects import ProtocolPrimitiveEffectExecutor

        assert ProtocolPrimitiveEffectExecutor is not None

    def test_literal_effect_id_still_importable(self) -> None:
        """LiteralEffectId remains importable after the change."""
        from omnibase_spi.protocols.effects import LiteralEffectId

        assert LiteralEffectId is not None

    def test_protocol_effect_and_primitive_executor_coexist(self) -> None:
        """Both ProtocolEffect and ProtocolPrimitiveEffectExecutor are in effects.__all__."""
        from omnibase_spi.protocols import effects

        assert "ProtocolEffect" in effects.__all__
        assert "ProtocolPrimitiveEffectExecutor" in effects.__all__


# ---------------------------------------------------------------------------
# End-to-end: intent-to-result flow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEndToEndProjectionFlow:
    """Simulate the runtime calling ProtocolNodeProjectionEffect.execute(intent)."""

    def test_runtime_can_call_execute_and_get_result(self) -> None:
        """Simulate runtime calling effect.execute(intent) with a dict intent."""
        intent: dict[str, Any] = {
            "entity_id": "order-42",
            "domain": "orders",
            "payload": {"status": "shipped"},
            "sequence": 100,
        }

        effect = _SuccessEffect()
        result = effect.execute(intent)

        assert isinstance(result, ContractProjectionResult)
        assert result.success is True
        assert result.artifact_ref == "ref-001"

    def test_runtime_aborts_on_projector_error(self) -> None:
        """Simulate runtime receiving ProjectorError and aborting Kafka publish."""
        intent: dict[str, Any] = {"entity_id": "order-99", "domain": "orders"}

        effect = _FailingEffect()
        kafka_published = False

        with pytest.raises(ProjectorError):
            effect.execute(intent)
            # This line is never reached — the raise prevents Kafka publish
            kafka_published = True  # pragma: no cover

        assert not kafka_published, "Kafka MUST NOT be published after ProjectorError"

    def test_runtime_skips_kafka_on_noop(self) -> None:
        """Simulate runtime skipping Kafka publish when success=False."""
        intent: dict[str, Any] = {"entity_id": "order-42", "domain": "orders"}

        effect = _NoOpEffect()
        result = effect.execute(intent)

        kafka_published = result.success  # runtime only publishes on success

        assert not kafka_published, "Kafka MUST NOT be published for a no-op write"
