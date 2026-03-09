"""Unit tests for ProtocolFSMSurfaceAdapter."""

from __future__ import annotations

import inspect
import sys

import pytest

pytestmark = pytest.mark.unit


class _Compliant:
    async def render(
        self, state: object, snapshot: object, surface: str
    ) -> dict[str, object]:
        return {}

    async def supported_surfaces(self) -> list[str]:
        return []


class _MissingRender:
    async def supported_surfaces(self) -> list[str]:
        return []


class _MissingSupportedSurfaces:
    async def render(
        self, state: object, snapshot: object, surface: str
    ) -> dict[str, object]:
        return {}


class _Empty:
    pass


class TestProtocolFSMSurfaceAdapterRuntimeStructure:
    def test_compliant_passes_isinstance(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        assert isinstance(_Compliant(), ProtocolFSMSurfaceAdapter)

    def test_missing_render_fails_isinstance(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        assert not isinstance(_MissingRender(), ProtocolFSMSurfaceAdapter)

    def test_missing_supported_surfaces_fails_isinstance(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        assert not isinstance(_MissingSupportedSurfaces(), ProtocolFSMSurfaceAdapter)

    def test_empty_class_fails_isinstance(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        assert not isinstance(_Empty(), ProtocolFSMSurfaceAdapter)


class TestProtocolFSMSurfaceAdapterMethodShape:
    def test_render_is_async(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        assert inspect.iscoroutinefunction(ProtocolFSMSurfaceAdapter.render)

    def test_supported_surfaces_is_async(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        assert inspect.iscoroutinefunction(ProtocolFSMSurfaceAdapter.supported_surfaces)

    def test_render_has_state_snapshot_surface_params(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        params = list(inspect.signature(ProtocolFSMSurfaceAdapter.render).parameters)
        assert "state" in params
        assert "snapshot" in params
        assert "surface" in params

    def test_protocol_compliant_stub_assignable(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter import (
            ProtocolFSMSurfaceAdapter,
        )

        adapter: ProtocolFSMSurfaceAdapter = _Compliant()  # type: ignore[assignment]
        assert adapter is not None


class TestProtocolFSMSurfaceAdapterImportBoundary:
    def test_importable_from_workflow_orchestration_submodule(self) -> None:
        from omnibase_spi.protocols.workflow_orchestration import (
            ProtocolFSMSurfaceAdapter,  # noqa: F401
        )

    def test_importable_from_root_protocols(self) -> None:
        from omnibase_spi.protocols import ProtocolFSMSurfaceAdapter  # noqa: F401

    def test_protocol_module_does_not_import_core_at_runtime(self) -> None:
        # Remove cached module if already imported so we get a fresh load
        mod_key = (
            "omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter"
        )
        sys.modules.pop(mod_key, None)

        import omnibase_spi.protocols.workflow_orchestration.protocol_fsm_surface_adapter  # noqa: F401

        core_model_path = (
            "omnibase_core.models.contracts.subcontracts.model_fsm_state_definition"
        )
        assert core_model_path not in sys.modules, (
            f"Importing ProtocolFSMSurfaceAdapter pulled '{core_model_path}' "
            "into sys.modules at runtime. Move the import under TYPE_CHECKING."
        )
