# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for ProtocolDomainPlugin.

Validates:
- ProtocolDomainPlugin is properly runtime_checkable
- Protocol defines required lifecycle methods
- Compliant/non-compliant isinstance checks work
- Imports are available from both direct module and package paths

Note: ModelDomainPluginConfig and ModelDomainPluginResult live in omnibase_infra
(moving to omnibase_core in a follow-up). Tests for those models belong in
omnibase_infra, not here.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from omnibase_spi.protocols.runtime.protocol_domain_plugin import ProtocolDomainPlugin

# ---------------------------------------------------------------------------
# Helpers: compliant and non-compliant implementations using MagicMock config
# ---------------------------------------------------------------------------


class CompliantPlugin:
    """A class that fully implements ProtocolDomainPlugin."""

    @property
    def plugin_id(self) -> str:
        return "test-plugin"

    @property
    def display_name(self) -> str:
        return "Test Plugin"

    def should_activate(self, config: Any) -> bool:
        return True

    async def initialize(self, config: Any) -> MagicMock:
        return MagicMock(success=True)

    async def wire_handlers(self, config: Any) -> MagicMock:
        return MagicMock(success=True)

    async def wire_dispatchers(self, config: Any) -> MagicMock:
        return MagicMock(success=True)

    async def start_consumers(self, config: Any) -> MagicMock:
        return MagicMock(success=True)

    async def shutdown(self, config: Any) -> MagicMock:
        return MagicMock(success=True)


class PartialPlugin:
    """A class missing some required ProtocolDomainPlugin methods."""

    @property
    def plugin_id(self) -> str:
        return "partial"

    async def initialize(self, config: Any) -> MagicMock:
        return MagicMock(success=True)


class EmptyClass:
    """A class with none of the required methods."""


# ---------------------------------------------------------------------------
# Tests: ProtocolDomainPlugin protocol shape
# ---------------------------------------------------------------------------


class TestProtocolDomainPluginShape:
    """Verify protocol is properly defined and runtime_checkable."""

    def test_is_runtime_checkable(self) -> None:
        assert hasattr(ProtocolDomainPlugin, "_is_runtime_protocol") or hasattr(
            ProtocolDomainPlugin, "__runtime_protocol__"
        )

    def test_is_protocol(self) -> None:
        from typing import Protocol

        assert any(
            base is Protocol or getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolDomainPlugin.__mro__
        )

    def test_has_plugin_id_property(self) -> None:
        assert "plugin_id" in dir(ProtocolDomainPlugin)

    def test_has_display_name_property(self) -> None:
        assert "display_name" in dir(ProtocolDomainPlugin)

    def test_has_should_activate(self) -> None:
        assert "should_activate" in dir(ProtocolDomainPlugin)

    def test_has_initialize(self) -> None:
        assert "initialize" in dir(ProtocolDomainPlugin)

    def test_has_wire_handlers(self) -> None:
        assert "wire_handlers" in dir(ProtocolDomainPlugin)

    def test_has_wire_dispatchers(self) -> None:
        assert "wire_dispatchers" in dir(ProtocolDomainPlugin)

    def test_has_start_consumers(self) -> None:
        assert "start_consumers" in dir(ProtocolDomainPlugin)

    def test_has_shutdown(self) -> None:
        assert "shutdown" in dir(ProtocolDomainPlugin)

    def test_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            ProtocolDomainPlugin()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Tests: isinstance compliance checks
# ---------------------------------------------------------------------------


class TestProtocolDomainPluginCompliance:
    """Verify isinstance checks for protocol compliance."""

    def test_compliant_class_passes(self) -> None:
        plugin = CompliantPlugin()
        assert isinstance(plugin, ProtocolDomainPlugin)

    def test_partial_class_fails(self) -> None:
        plugin = PartialPlugin()
        assert not isinstance(plugin, ProtocolDomainPlugin)

    def test_empty_class_fails(self) -> None:
        obj = EmptyClass()
        assert not isinstance(obj, ProtocolDomainPlugin)


# ---------------------------------------------------------------------------
# Tests: lifecycle method async nature
# ---------------------------------------------------------------------------


class TestCompliantPluginLifecycle:
    """Verify lifecycle methods are async and sync as declared."""

    def test_should_activate_is_sync(self) -> None:
        import inspect

        assert not inspect.iscoroutinefunction(CompliantPlugin.should_activate)

    def test_initialize_is_async(self) -> None:
        import inspect

        assert inspect.iscoroutinefunction(CompliantPlugin.initialize)

    def test_shutdown_is_async(self) -> None:
        import inspect

        assert inspect.iscoroutinefunction(CompliantPlugin.shutdown)


# ---------------------------------------------------------------------------
# Tests: Import paths
# ---------------------------------------------------------------------------


class TestImportPaths:
    """Verify imports work from multiple canonical paths."""

    def test_import_from_module(self) -> None:
        from omnibase_spi.protocols.runtime.protocol_domain_plugin import (
            ProtocolDomainPlugin as Direct,
        )

        assert Direct is ProtocolDomainPlugin

    def test_import_from_package(self) -> None:
        from omnibase_spi.protocols.runtime import (
            ProtocolDomainPlugin as Pkg,
        )

        assert Pkg is ProtocolDomainPlugin

    def test_import_from_protocols_init(self) -> None:
        from omnibase_spi.protocols import ProtocolDomainPlugin as Root

        assert Root is ProtocolDomainPlugin
