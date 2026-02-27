"""
Unit tests for the NodeProjectionEffect pattern (OMN-2382).

This module validates the three-abstraction projection pattern:
  1. ModelProjectionIntent (omnibase_core) — carries routing metadata + envelope
  2. NodeProjectionEffect — generic dispatcher pattern (reference impl in test)
  3. ProtocolProjectionView (omnibase_spi) — SPI contract for view implementations

The tests use an inline reference implementation of ``NodeProjectionEffect``
that demonstrates how a consuming package (e.g. omnibase_infra) would build
the concrete generic effect node on top of the two SPI abstractions.

Tests cover:
- Routing: intent.projector_key dispatches to the correct registered projector
- Unknown projector: returns ContractProjectionResult(success=False, error="Unknown projector: X")
  NOT an exception — structured error for unknown projector key
- ProtocolProjectionView compliance via isinstance check
- ProtocolNodeProjectionEffect compliance for the reference implementation
- ProjectorError propagation from registered projectors
- Multi-projector registry isolation

Related: OMN-2382
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import ClassVar
from uuid import uuid4

import pytest
from pydantic import BaseModel

from omnibase_core.models.projectors.model_projection_intent import (
    ModelProjectionIntent,
)
from omnibase_spi.contracts.projections.contract_projection_result import (
    ContractProjectionResult,
)
from omnibase_spi.effects.node_projection_effect import ProtocolNodeProjectionEffect
from omnibase_spi.exceptions import ProjectorError
from omnibase_spi.protocols.projections.protocol_projection_view import (
    ProtocolProjectionView,
)

# ---------------------------------------------------------------------------
# Reference Implementation: NodeProjectionEffect
#
# This is the "template" that a consuming package (e.g. omnibase_infra) would
# build. It demonstrates the complete pattern:
#   - Registry-based dispatch via projector_key
#   - Structured error (not exception) for unknown projectors
#   - Satisfies ProtocolNodeProjectionEffect
# ---------------------------------------------------------------------------


def _run_coroutine_sync(coro: object) -> object:
    """Bridge async coroutine to synchronous call."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        return asyncio.run(coro)  # type: ignore[arg-type]

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)  # type: ignore[arg-type]
        return future.result()


class _ReferenceNodeProjectionEffect:
    """Reference implementation of NodeProjectionEffect for testing.

    Demonstrates the three-abstraction pattern. A consuming package would
    implement this class (or an equivalent) as a concrete EFFECT node.

    This class satisfies both:
    - ProtocolNodeProjectionEffect (synchronous execute() returning ContractProjectionResult)
    - The registry dispatch pattern from OMN-2382
    """

    synchronous_execution: ClassVar[bool] = True

    def __init__(
        self,
        registry: dict[str, ProtocolProjectionView],
    ) -> None:
        self._registry = dict(registry)

    def execute(self, intent: object) -> ContractProjectionResult:
        """Dispatch intent to registered projector by projector_key.

        Returns ContractProjectionResult(success=False, error="Unknown projector: X")
        for unknown projector keys. Does NOT raise for unknown keys.
        """
        from omnibase_core.models.projectors.model_projection_intent import (
            ModelProjectionIntent,
        )

        if not isinstance(intent, ModelProjectionIntent):
            raise ValueError(
                f"execute() expects ModelProjectionIntent, got {type(intent).__name__}"
            )

        projector = self._registry.get(intent.projector_key)
        if projector is None:
            return ContractProjectionResult(
                success=False,
                artifact_ref=None,
                error=f"Unknown projector: {intent.projector_key}",
            )

        try:
            return projector.project_intent(intent)
        except ProjectorError:
            raise
        except Exception as exc:
            raise ProjectorError(
                f"Projector {intent.projector_key!r} raised: {exc}",
                context={"projector_key": intent.projector_key, "error": str(exc)},
            ) from exc


# ---------------------------------------------------------------------------
# Minimal stubs for test projectors (ProtocolProjectionView implementations)
# ---------------------------------------------------------------------------


class _SimpleEnvelope(BaseModel):
    """Minimal event envelope for tests."""

    envelope_id: str
    entity_id: str


def _make_intent(
    projector_key: str = "node_state_projector",
    event_type: str = "node.created.v1",
    entity_id: str = "entity-abc",
) -> ModelProjectionIntent:
    """Create a ModelProjectionIntent for tests."""
    return ModelProjectionIntent(
        projector_key=projector_key,
        event_type=event_type,
        envelope=_SimpleEnvelope(envelope_id="env-1", entity_id=entity_id),
        correlation_id=uuid4(),
    )


class _SuccessView:
    """View that always returns success."""

    synchronous_execution: ClassVar[bool] = True
    call_count: int = 0

    def __init__(self, key: str = "node_state_projector") -> None:
        self._key = key
        self.call_count = 0
        self.last_intent: ModelProjectionIntent | None = None

    @property
    def projector_key(self) -> str:
        return self._key

    def project_intent(self, intent: ModelProjectionIntent) -> ContractProjectionResult:
        self.call_count += 1
        self.last_intent = intent
        return ContractProjectionResult(
            success=True, artifact_ref=f"ref-{intent.projector_key}"
        )


class _SkippedView:
    """View that always returns success=False (skipped)."""

    synchronous_execution: ClassVar[bool] = True

    @property
    def projector_key(self) -> str:
        return "skip_projector"

    def project_intent(self, intent: ModelProjectionIntent) -> ContractProjectionResult:
        return ContractProjectionResult(
            success=False,
            error="Projection skipped: event type not consumed.",
        )


class _FailingView:
    """View that raises ProjectorError."""

    synchronous_execution: ClassVar[bool] = True

    @property
    def projector_key(self) -> str:
        return "fail_projector"

    def project_intent(self, intent: ModelProjectionIntent) -> ContractProjectionResult:
        raise ProjectorError(
            "DB write failed",
            context={"projector_key": "fail_projector", "operation": "project_intent"},
        )


# ---------------------------------------------------------------------------
# Tests: ProtocolProjectionView protocol compliance
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolProjectionView:
    """ProtocolProjectionView is runtime_checkable and correctly classifies implementations."""

    def test_success_view_satisfies_protocol(self) -> None:
        """_SuccessView with projector_key + project_intent satisfies isinstance."""
        view = _SuccessView()
        assert isinstance(view, ProtocolProjectionView)

    def test_skipped_view_satisfies_protocol(self) -> None:
        """_SkippedView satisfies ProtocolProjectionView."""
        assert isinstance(_SkippedView(), ProtocolProjectionView)

    def test_failing_view_satisfies_protocol(self) -> None:
        """_FailingView satisfies ProtocolProjectionView."""
        assert isinstance(_FailingView(), ProtocolProjectionView)

    def test_missing_project_intent_fails_isinstance(self) -> None:
        """Class without project_intent() does NOT satisfy ProtocolProjectionView."""

        class _NoProjectIntent:
            synchronous_execution: ClassVar[bool] = True

            @property
            def projector_key(self) -> str:
                return "x"

        assert not isinstance(_NoProjectIntent(), ProtocolProjectionView)

    def test_missing_projector_key_fails_isinstance(self) -> None:
        """Class without projector_key property does NOT satisfy ProtocolProjectionView."""

        class _NoKey:
            synchronous_execution: ClassVar[bool] = True

            def project_intent(
                self, intent: ModelProjectionIntent
            ) -> ContractProjectionResult:
                return ContractProjectionResult(success=True)

        assert not isinstance(_NoKey(), ProtocolProjectionView)

    def test_is_runtime_checkable(self) -> None:
        """ProtocolProjectionView is @runtime_checkable."""
        assert hasattr(ProtocolProjectionView, "_is_runtime_protocol") or hasattr(
            ProtocolProjectionView, "__runtime_protocol__"
        )

    def test_has_synchronous_execution_class_var(self) -> None:
        """ProtocolProjectionView documents synchronous_execution ClassVar."""
        # The ClassVar is declared on the protocol — concrete views must set it.
        assert "synchronous_execution" in ProtocolProjectionView.__annotations__

    def test_compliant_view_satisfies_protocol_node_projection_effect_contract(
        self,
    ) -> None:
        """Reference NodeProjectionEffect (using ProtocolProjectionView registry) satisfies
        ProtocolNodeProjectionEffect — the two protocols compose correctly.
        """
        registry: dict[str, ProtocolProjectionView] = {
            "node_state_projector": _SuccessView("node_state_projector"),
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)
        assert isinstance(effect, ProtocolNodeProjectionEffect)


# ---------------------------------------------------------------------------
# Tests: Unknown projector → structured error, NOT exception
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNodeProjectionEffectPatternUnknownProjector:
    """Unknown projector_key returns structured ContractProjectionResult, not exception."""

    def test_unknown_projector_returns_success_false(self) -> None:
        """Unknown projector_key returns ContractProjectionResult(success=False)."""
        effect = _ReferenceNodeProjectionEffect(registry={})
        result = effect.execute(_make_intent(projector_key="nonexistent"))

        assert isinstance(result, ContractProjectionResult)
        assert result.success is False

    def test_unknown_projector_error_contains_key(self) -> None:
        """Error message contains the unknown projector_key."""
        effect = _ReferenceNodeProjectionEffect(registry={})
        result = effect.execute(_make_intent(projector_key="ghost_projector"))

        assert result.error is not None
        assert "ghost_projector" in result.error

    def test_unknown_projector_error_starts_with_unknown_projector(self) -> None:
        """Error message starts with 'Unknown projector:'."""
        effect = _ReferenceNodeProjectionEffect(registry={})
        result = effect.execute(_make_intent(projector_key="mystery"))

        assert result.error is not None
        assert result.error.startswith("Unknown projector:")

    def test_unknown_projector_does_not_raise(self) -> None:
        """Unknown projector does NOT raise any exception."""
        effect = _ReferenceNodeProjectionEffect(registry={})

        try:
            result = effect.execute(_make_intent(projector_key="totally_unknown"))
        except Exception as exc:  # noqa: BLE001
            pytest.fail(
                f"execute() raised {type(exc).__name__} for unknown projector: {exc}"
            )

        assert isinstance(result, ContractProjectionResult)

    def test_key_absent_from_partial_registry_returns_structured_error(self) -> None:
        """Key absent from non-empty registry returns structured error."""
        registry: dict[str, ProtocolProjectionView] = {
            "projector_a": _SuccessView("projector_a"),
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)
        result = effect.execute(_make_intent(projector_key="projector_b"))

        assert result.success is False
        assert result.error is not None
        assert "projector_b" in result.error


# ---------------------------------------------------------------------------
# Tests: Routing to correct projector
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNodeProjectionEffectPatternRouting:
    """execute() routes intent.projector_key to the correct registered projector."""

    def test_routes_to_registered_projector(self) -> None:
        """Intent with registered projector_key dispatches to that projector."""
        view = _SuccessView("node_state_projector")
        registry: dict[str, ProtocolProjectionView] = {"node_state_projector": view}
        effect = _ReferenceNodeProjectionEffect(registry=registry)

        result = effect.execute(_make_intent(projector_key="node_state_projector"))

        assert result.success is True
        assert view.call_count == 1

    def test_projector_receives_correct_intent(self) -> None:
        """The registered projector receives the original intent object."""
        view = _SuccessView("node_state_projector")
        registry: dict[str, ProtocolProjectionView] = {"node_state_projector": view}
        effect = _ReferenceNodeProjectionEffect(registry=registry)

        intent = _make_intent(
            projector_key="node_state_projector",
            event_type="node.created.v1",
        )
        effect.execute(intent)

        assert view.last_intent is intent
        assert view.last_intent.event_type == "node.created.v1"

    def test_correct_projector_called_in_multi_projector_registry(self) -> None:
        """With multiple projectors, only the matching one is invoked."""
        view_a = _SuccessView("projector_a")
        view_b = _SuccessView("projector_b")
        registry: dict[str, ProtocolProjectionView] = {
            "projector_a": view_a,
            "projector_b": view_b,
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)

        effect.execute(_make_intent(projector_key="projector_b"))

        assert view_b.call_count == 1
        assert view_a.call_count == 0

    def test_routes_each_key_to_its_own_projector(self) -> None:
        """Different projector_keys each route to their own projector."""
        view_x = _SuccessView("projector_x")
        view_y = _SuccessView("projector_y")
        registry: dict[str, ProtocolProjectionView] = {
            "projector_x": view_x,
            "projector_y": view_y,
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)

        effect.execute(_make_intent(projector_key="projector_x"))
        effect.execute(_make_intent(projector_key="projector_y"))

        assert view_x.call_count == 1
        assert view_y.call_count == 1

    def test_success_result_has_correct_type(self) -> None:
        """Successful projection returns ContractProjectionResult."""
        registry: dict[str, ProtocolProjectionView] = {
            "p": _SuccessView("p"),
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)
        result = effect.execute(_make_intent(projector_key="p"))

        assert isinstance(result, ContractProjectionResult)
        assert result.success is True


# ---------------------------------------------------------------------------
# Tests: Skipped projection
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNodeProjectionEffectPatternSkipped:
    """When the view returns success=False, result propagates."""

    def test_skipped_view_returns_success_false(self) -> None:
        """Skipped projection view returns ContractProjectionResult(success=False)."""
        registry: dict[str, ProtocolProjectionView] = {
            "skip_projector": _SkippedView(),
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)
        result = effect.execute(_make_intent(projector_key="skip_projector"))

        assert result.success is False
        assert result.error is not None


# ---------------------------------------------------------------------------
# Tests: Infrastructure failure propagation
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNodeProjectionEffectPatternFailure:
    """ProjectorError from view propagates as-is."""

    def test_projector_error_propagates_unchanged(self) -> None:
        """ProjectorError raised by view propagates through execute()."""
        registry: dict[str, ProtocolProjectionView] = {
            "fail_projector": _FailingView(),
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)

        with pytest.raises(ProjectorError) as exc_info:
            effect.execute(_make_intent(projector_key="fail_projector"))

        assert "DB write failed" in str(exc_info.value)

    def test_projector_error_context_preserved(self) -> None:
        """ProjectorError context is preserved."""
        registry: dict[str, ProtocolProjectionView] = {
            "fail_projector": _FailingView(),
        }
        effect = _ReferenceNodeProjectionEffect(registry=registry)

        with pytest.raises(ProjectorError) as exc_info:
            effect.execute(_make_intent(projector_key="fail_projector"))

        assert exc_info.value.context.get("projector_key") == "fail_projector"


# ---------------------------------------------------------------------------
# Tests: Export surface
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolProjectionViewExportSurface:
    """ProtocolProjectionView is reachable from expected import paths."""

    def test_importable_from_protocols_projections(self) -> None:
        """ProtocolProjectionView importable from omnibase_spi.protocols.projections."""
        from omnibase_spi.protocols.projections import ProtocolProjectionView as PPV

        assert PPV is ProtocolProjectionView

    def test_importable_from_spi_root(self) -> None:
        """ProtocolProjectionView lazily importable from omnibase_spi root."""
        import omnibase_spi
        from omnibase_spi.protocols.projections import ProtocolProjectionView as PPV

        assert omnibase_spi.ProtocolProjectionView is PPV

    def test_in_projections_all(self) -> None:
        """ProtocolProjectionView is in omnibase_spi.protocols.projections.__all__."""
        from omnibase_spi.protocols import projections

        assert "ProtocolProjectionView" in projections.__all__


# ---------------------------------------------------------------------------
# Tests: No regression on existing protocols
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolProjectionViewNoRegression:
    """Adding ProtocolProjectionView does not break existing projection protocols."""

    def test_protocol_projector_still_in_all(self) -> None:
        """ProtocolProjector remains in projections.__all__."""
        from omnibase_spi.protocols import projections

        assert "ProtocolProjector" in projections.__all__

    def test_protocol_projection_reader_still_in_all(self) -> None:
        """ProtocolProjectionReader remains in projections.__all__."""
        from omnibase_spi.protocols import projections

        assert "ProtocolProjectionReader" in projections.__all__

    def test_protocol_node_projection_effect_unaffected(self) -> None:
        """ProtocolNodeProjectionEffect remains importable from effects."""
        from omnibase_spi.effects import ProtocolNodeProjectionEffect as PNPE

        assert PNPE is ProtocolNodeProjectionEffect

    def test_contract_projection_result_unaffected(self) -> None:
        """ContractProjectionResult remains importable and unchanged."""
        from omnibase_spi.contracts.projections import ContractProjectionResult as CPR

        assert CPR is ContractProjectionResult
