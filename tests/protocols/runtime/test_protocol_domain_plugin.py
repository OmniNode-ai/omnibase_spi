# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for ProtocolDomainPlugin, ModelDomainPluginConfig, ModelDomainPluginResult.

Validates:
- ProtocolDomainPlugin is properly runtime_checkable
- Protocol defines required lifecycle methods
- Compliant/non-compliant isinstance checks work
- ModelDomainPluginConfig constructs correctly
- ModelDomainPluginResult factory methods work
- Imports are available from both direct module and package paths
"""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from omnibase_spi.protocols.runtime.protocol_domain_plugin import (
    ModelDomainPluginConfig,
    ModelDomainPluginResult,
    ProtocolDomainPlugin,
)

# ---------------------------------------------------------------------------
# Helpers: compliant and non-compliant implementations
# ---------------------------------------------------------------------------


class CompliantPlugin:
    """A class that fully implements ProtocolDomainPlugin."""

    @property
    def plugin_id(self) -> str:
        return "test-plugin"

    @property
    def display_name(self) -> str:
        return "Test Plugin"

    def should_activate(self, config: ModelDomainPluginConfig) -> bool:
        return True

    async def initialize(self, config: ModelDomainPluginConfig) -> ModelDomainPluginResult:
        return ModelDomainPluginResult.succeeded(self.plugin_id)

    async def wire_handlers(self, config: ModelDomainPluginConfig) -> ModelDomainPluginResult:
        return ModelDomainPluginResult.succeeded(self.plugin_id)

    async def wire_dispatchers(self, config: ModelDomainPluginConfig) -> ModelDomainPluginResult:
        return ModelDomainPluginResult.succeeded(self.plugin_id)

    async def start_consumers(self, config: ModelDomainPluginConfig) -> ModelDomainPluginResult:
        return ModelDomainPluginResult.succeeded(self.plugin_id)

    async def shutdown(self, config: ModelDomainPluginConfig) -> ModelDomainPluginResult:
        return ModelDomainPluginResult.succeeded(self.plugin_id)


class PartialPlugin:
    """A class missing some required ProtocolDomainPlugin methods."""

    @property
    def plugin_id(self) -> str:
        return "partial"

    async def initialize(self, config: ModelDomainPluginConfig) -> ModelDomainPluginResult:
        return ModelDomainPluginResult.succeeded(self.plugin_id)


class EmptyClass:
    """A class with none of the required methods."""


# ---------------------------------------------------------------------------
# Tests: ProtocolDomainPlugin protocol shape
# ---------------------------------------------------------------------------


class TestProtocolDomainPluginShape:
    """Verify protocol is properly defined and runtime_checkable."""

    def test_is_runtime_checkable(self) -> None:
        """ProtocolDomainPlugin should be decorated with @runtime_checkable."""
        assert hasattr(ProtocolDomainPlugin, "_is_runtime_protocol") or hasattr(
            ProtocolDomainPlugin, "__runtime_protocol__"
        )

    def test_is_protocol(self) -> None:
        """ProtocolDomainPlugin should be a Protocol class."""
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
        """Protocol cannot be directly instantiated."""
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
# Tests: ModelDomainPluginConfig
# ---------------------------------------------------------------------------


class TestModelDomainPluginConfig:
    """Verify ModelDomainPluginConfig construction and fields."""

    def _make_config(self) -> ModelDomainPluginConfig:
        return ModelDomainPluginConfig(
            container=MagicMock(),
            event_bus=MagicMock(),
            correlation_id=uuid4(),
            input_topic="requests",
            output_topic="responses",
            consumer_group="test-group",
        )

    def test_basic_construction(self) -> None:
        cfg = self._make_config()
        assert cfg.input_topic == "requests"
        assert cfg.output_topic == "responses"
        assert cfg.consumer_group == "test-group"

    def test_optional_fields_default_none(self) -> None:
        cfg = self._make_config()
        assert cfg.dispatch_engine is None
        assert cfg.node_identity is None
        assert cfg.kafka_bootstrap_servers is None
        assert cfg.output_topic_map is None

    def test_optional_fields_can_be_set(self) -> None:
        cfg = self._make_config()
        cfg.dispatch_engine = MagicMock()
        cfg.node_identity = MagicMock()
        cfg.kafka_bootstrap_servers = "localhost:9092"
        cfg.output_topic_map = {"MyEvent": "topic.v1"}
        assert cfg.dispatch_engine is not None
        assert cfg.node_identity is not None
        assert cfg.kafka_bootstrap_servers == "localhost:9092"
        assert cfg.output_topic_map == {"MyEvent": "topic.v1"}


# ---------------------------------------------------------------------------
# Tests: ModelDomainPluginResult
# ---------------------------------------------------------------------------


class TestModelDomainPluginResult:
    """Verify ModelDomainPluginResult factory methods and __bool__."""

    def test_succeeded_factory(self) -> None:
        r = ModelDomainPluginResult.succeeded("my-plugin")
        assert r.success is True
        assert r.plugin_id == "my-plugin"
        assert bool(r) is True

    def test_failed_factory(self) -> None:
        r = ModelDomainPluginResult.failed("my-plugin", error_message="boom")
        assert r.success is False
        assert r.error_message == "boom"
        assert bool(r) is False

    def test_skipped_factory(self) -> None:
        r = ModelDomainPluginResult.skipped("my-plugin", reason="env not set")
        assert r.success is True
        assert "skipped" in r.message
        assert bool(r) is True

    def test_get_error_message_or_default_with_error(self) -> None:
        r = ModelDomainPluginResult.failed("p", error_message="oops")
        assert r.get_error_message_or_default() == "oops"

    def test_get_error_message_or_default_without_error(self) -> None:
        r = ModelDomainPluginResult.succeeded("p")
        assert r.get_error_message_or_default("fallback") == "fallback"

    def test_resources_created_defaults_empty(self) -> None:
        r = ModelDomainPluginResult(plugin_id="p", success=True)
        assert r.resources_created == []

    def test_services_registered_defaults_empty(self) -> None:
        r = ModelDomainPluginResult(plugin_id="p", success=True)
        assert r.services_registered == []

    def test_unsubscribe_callbacks_defaults_empty(self) -> None:
        r = ModelDomainPluginResult(plugin_id="p", success=True)
        assert r.unsubscribe_callbacks == []


# ---------------------------------------------------------------------------
# Tests: lifecycle method async nature
# ---------------------------------------------------------------------------


class TestCompliantPluginLifecycle:
    """Verify lifecycle methods are async and return correct types."""

    def _make_config(self) -> ModelDomainPluginConfig:
        return ModelDomainPluginConfig(
            container=MagicMock(),
            event_bus=MagicMock(),
            correlation_id=uuid4(),
            input_topic="in",
            output_topic="out",
            consumer_group="grp",
        )

    @pytest.mark.asyncio
    async def test_initialize_returns_result(self) -> None:
        plugin = CompliantPlugin()
        result = await plugin.initialize(self._make_config())
        assert isinstance(result, ModelDomainPluginResult)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_wire_handlers_returns_result(self) -> None:
        plugin = CompliantPlugin()
        result = await plugin.wire_handlers(self._make_config())
        assert isinstance(result, ModelDomainPluginResult)

    @pytest.mark.asyncio
    async def test_shutdown_returns_result(self) -> None:
        plugin = CompliantPlugin()
        result = await plugin.shutdown(self._make_config())
        assert isinstance(result, ModelDomainPluginResult)
        assert result.success is True

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

    def test_model_config_importable_from_module(self) -> None:
        from omnibase_spi.protocols.runtime.protocol_domain_plugin import (
            ModelDomainPluginConfig as Cfg,
        )
        assert Cfg is ModelDomainPluginConfig

    def test_model_result_importable_from_module(self) -> None:
        from omnibase_spi.protocols.runtime.protocol_domain_plugin import (
            ModelDomainPluginResult as Res,
        )
        assert Res is ModelDomainPluginResult
