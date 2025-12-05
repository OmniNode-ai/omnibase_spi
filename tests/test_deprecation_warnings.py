"""
Tests for legacy protocol deprecation warnings.

Validates that:
- Importing legacy module triggers DeprecationWarning
- Warning message includes removal version (0.5.0)
- Warning message includes migration guidance
- Each legacy protocol class is accessible after import
"""

from __future__ import annotations

import importlib
import sys
import warnings
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType


@pytest.fixture
def clear_legacy_modules() -> None:
    """Clear cached legacy module imports to ensure fresh import behavior.

    This fixture removes all cached imports of the legacy module and its
    submodules from sys.modules, allowing tests to observe import-time
    behavior like deprecation warnings.
    """
    modules_to_remove = [
        key
        for key in sys.modules
        if key.startswith("omnibase_spi.protocols.nodes.legacy")
    ]
    for module_name in modules_to_remove:
        del sys.modules[module_name]


class TestLegacyModuleDeprecationWarning:
    """Tests for legacy module import deprecation warning."""

    def _import_legacy_module_fresh(self) -> ModuleType:
        """Import the legacy module fresh, clearing any cached import.

        Returns:
            The freshly imported legacy module.
        """
        # Remove cached module and submodules to ensure fresh import
        modules_to_remove = [
            key
            for key in sys.modules
            if key.startswith("omnibase_spi.protocols.nodes.legacy")
        ]
        for module_name in modules_to_remove:
            del sys.modules[module_name]

        # Now import fresh
        import omnibase_spi.protocols.nodes.legacy as legacy_module

        return legacy_module

    def test_legacy_module_import_triggers_deprecation_warning(
        self, clear_legacy_modules: None
    ) -> None:
        """Importing the legacy module should trigger a DeprecationWarning."""

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            import omnibase_spi.protocols.nodes.legacy  # noqa: F401

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected at least one DeprecationWarning"

    def test_deprecation_warning_includes_version(
        self, clear_legacy_modules: None
    ) -> None:
        """Deprecation warning should include the removal version (0.5.0)."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            import omnibase_spi.protocols.nodes.legacy  # noqa: F401

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected at least one DeprecationWarning"

            # Check that at least one warning mentions v0.5.0
            version_mentioned = any(
                "0.5.0" in str(w.message) for w in deprecation_warnings
            )
            assert version_mentioned, (
                f"Expected warning to mention '0.5.0'. "
                f"Warnings: {[str(w.message) for w in deprecation_warnings]}"
            )

    def test_deprecation_warning_includes_migration_guidance(
        self, clear_legacy_modules: None
    ) -> None:
        """Deprecation warning should include migration guidance."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            import omnibase_spi.protocols.nodes.legacy  # noqa: F401

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected at least one DeprecationWarning"

            # Check that migration guidance is provided
            # The warning should mention the standard module path
            guidance_mentioned = any(
                "omnibase_spi.protocols.nodes" in str(w.message)
                for w in deprecation_warnings
            )
            assert guidance_mentioned, (
                f"Expected warning to include migration guidance mentioning "
                f"'omnibase_spi.protocols.nodes'. "
                f"Warnings: {[str(w.message) for w in deprecation_warnings]}"
            )

    def test_deprecation_warning_message_content(
        self, clear_legacy_modules: None
    ) -> None:
        """Verify the full deprecation warning message content."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            import omnibase_spi.protocols.nodes.legacy  # noqa: F401

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected at least one DeprecationWarning"

            # Get the main warning message
            warning_message = str(deprecation_warnings[0].message)

            # Verify key components
            assert (
                "deprecated" in warning_message.lower()
            ), f"Expected 'deprecated' in message: {warning_message}"
            assert (
                "0.5.0" in warning_message
            ), f"Expected '0.5.0' in message: {warning_message}"
            assert (
                "legacy" in warning_message.lower()
            ), f"Expected 'legacy' in message: {warning_message}"


class TestLegacyProtocolDeprecationWarnings:
    """Tests for individual legacy protocol deprecation warnings."""

    def test_compute_node_legacy_deprecation_warning(
        self, clear_legacy_modules: None
    ) -> None:
        """Importing ProtocolComputeNodeLegacy should trigger deprecation warning."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            from omnibase_spi.protocols.nodes.legacy import (  # noqa: F401
                ProtocolComputeNodeLegacy,
            )

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected DeprecationWarning when importing ProtocolComputeNodeLegacy"

            # Verify the protocol is accessible
            assert ProtocolComputeNodeLegacy is not None

    def test_effect_node_legacy_deprecation_warning(
        self, clear_legacy_modules: None
    ) -> None:
        """Importing ProtocolEffectNodeLegacy should trigger deprecation warning."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            from omnibase_spi.protocols.nodes.legacy import (  # noqa: F401
                ProtocolEffectNodeLegacy,
            )

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected DeprecationWarning when importing ProtocolEffectNodeLegacy"

            # Verify the protocol is accessible
            assert ProtocolEffectNodeLegacy is not None

    def test_reducer_node_legacy_deprecation_warning(
        self, clear_legacy_modules: None
    ) -> None:
        """Importing ProtocolReducerNodeLegacy should trigger deprecation warning."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            from omnibase_spi.protocols.nodes.legacy import (  # noqa: F401
                ProtocolReducerNodeLegacy,
            )

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected DeprecationWarning when importing ProtocolReducerNodeLegacy"

            # Verify the protocol is accessible
            assert ProtocolReducerNodeLegacy is not None

    def test_orchestrator_node_legacy_deprecation_warning(
        self, clear_legacy_modules: None
    ) -> None:
        """Importing ProtocolOrchestratorNodeLegacy should trigger deprecation warning."""
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            from omnibase_spi.protocols.nodes.legacy import (  # noqa: F401
                ProtocolOrchestratorNodeLegacy,
            )

            # Find deprecation warnings
            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected DeprecationWarning when importing ProtocolOrchestratorNodeLegacy"

            # Verify the protocol is accessible
            assert ProtocolOrchestratorNodeLegacy is not None


class TestLegacyProtocolsAreRuntimeCheckable:
    """Tests to verify legacy protocols maintain runtime_checkable status."""

    def test_compute_node_legacy_is_runtime_checkable(self) -> None:
        """ProtocolComputeNodeLegacy should be runtime_checkable."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolComputeNodeLegacy

            assert hasattr(
                ProtocolComputeNodeLegacy, "_is_runtime_protocol"
            ) or hasattr(ProtocolComputeNodeLegacy, "__runtime_protocol__")

    def test_effect_node_legacy_is_runtime_checkable(self) -> None:
        """ProtocolEffectNodeLegacy should be runtime_checkable."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolEffectNodeLegacy

            assert hasattr(ProtocolEffectNodeLegacy, "_is_runtime_protocol") or hasattr(
                ProtocolEffectNodeLegacy, "__runtime_protocol__"
            )

    def test_reducer_node_legacy_is_runtime_checkable(self) -> None:
        """ProtocolReducerNodeLegacy should be runtime_checkable."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolReducerNodeLegacy

            assert hasattr(
                ProtocolReducerNodeLegacy, "_is_runtime_protocol"
            ) or hasattr(ProtocolReducerNodeLegacy, "__runtime_protocol__")

    def test_orchestrator_node_legacy_is_runtime_checkable(self) -> None:
        """ProtocolOrchestratorNodeLegacy should be runtime_checkable."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import (
                ProtocolOrchestratorNodeLegacy,
            )

            assert hasattr(
                ProtocolOrchestratorNodeLegacy, "_is_runtime_protocol"
            ) or hasattr(ProtocolOrchestratorNodeLegacy, "__runtime_protocol__")


class TestLegacyProtocolDocstrings:
    """Tests to verify legacy protocols have deprecation info in docstrings."""

    def test_compute_node_legacy_docstring_mentions_deprecation(self) -> None:
        """ProtocolComputeNodeLegacy docstring should mention deprecation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolComputeNodeLegacy

            docstring = ProtocolComputeNodeLegacy.__doc__ or ""
            assert (
                "deprecated" in docstring.lower()
            ), f"Expected 'deprecated' in docstring: {docstring}"
            assert "0.5.0" in docstring, f"Expected '0.5.0' in docstring: {docstring}"

    def test_effect_node_legacy_docstring_mentions_deprecation(self) -> None:
        """ProtocolEffectNodeLegacy docstring should mention deprecation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolEffectNodeLegacy

            docstring = ProtocolEffectNodeLegacy.__doc__ or ""
            assert (
                "deprecated" in docstring.lower()
            ), f"Expected 'deprecated' in docstring: {docstring}"
            assert "0.5.0" in docstring, f"Expected '0.5.0' in docstring: {docstring}"

    def test_reducer_node_legacy_docstring_mentions_deprecation(self) -> None:
        """ProtocolReducerNodeLegacy docstring should mention deprecation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolReducerNodeLegacy

            docstring = ProtocolReducerNodeLegacy.__doc__ or ""
            assert (
                "deprecated" in docstring.lower()
            ), f"Expected 'deprecated' in docstring: {docstring}"
            assert "0.5.0" in docstring, f"Expected '0.5.0' in docstring: {docstring}"

    def test_orchestrator_node_legacy_docstring_mentions_deprecation(self) -> None:
        """ProtocolOrchestratorNodeLegacy docstring should mention deprecation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import (
                ProtocolOrchestratorNodeLegacy,
            )

            docstring = ProtocolOrchestratorNodeLegacy.__doc__ or ""
            assert (
                "deprecated" in docstring.lower()
            ), f"Expected 'deprecated' in docstring: {docstring}"
            assert "0.5.0" in docstring, f"Expected '0.5.0' in docstring: {docstring}"


class TestLegacyProtocolMigrationInfo:
    """Tests to verify legacy protocols provide migration information."""

    def test_compute_node_legacy_docstring_has_migration_guide(self) -> None:
        """ProtocolComputeNodeLegacy docstring should include migration guidance."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolComputeNodeLegacy

            docstring = ProtocolComputeNodeLegacy.__doc__ or ""
            # Check for migration keywords
            has_migration_info = (
                "migrate" in docstring.lower()
                or "migration" in docstring.lower()
                or "ProtocolComputeNode" in docstring
            )
            assert (
                has_migration_info
            ), f"Expected migration info in docstring: {docstring}"

    def test_effect_node_legacy_docstring_has_migration_guide(self) -> None:
        """ProtocolEffectNodeLegacy docstring should include migration guidance."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolEffectNodeLegacy

            docstring = ProtocolEffectNodeLegacy.__doc__ or ""
            has_migration_info = (
                "migrate" in docstring.lower()
                or "migration" in docstring.lower()
                or "ProtocolEffectNode" in docstring
            )
            assert (
                has_migration_info
            ), f"Expected migration info in docstring: {docstring}"

    def test_reducer_node_legacy_docstring_has_migration_guide(self) -> None:
        """ProtocolReducerNodeLegacy docstring should include migration guidance."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import ProtocolReducerNodeLegacy

            docstring = ProtocolReducerNodeLegacy.__doc__ or ""
            has_migration_info = (
                "migrate" in docstring.lower()
                or "migration" in docstring.lower()
                or "ProtocolReducerNode" in docstring
            )
            assert (
                has_migration_info
            ), f"Expected migration info in docstring: {docstring}"

    def test_orchestrator_node_legacy_docstring_has_migration_guide(self) -> None:
        """ProtocolOrchestratorNodeLegacy docstring should include migration guidance."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes.legacy import (
                ProtocolOrchestratorNodeLegacy,
            )

            docstring = ProtocolOrchestratorNodeLegacy.__doc__ or ""
            has_migration_info = (
                "migrate" in docstring.lower()
                or "migration" in docstring.lower()
                or "ProtocolOrchestratorNode" in docstring
            )
            assert (
                has_migration_info
            ), f"Expected migration info in docstring: {docstring}"


class TestLegacyModuleReimport:
    """Tests for module reimport behavior."""

    def test_reimport_with_importlib_triggers_warning(
        self, clear_legacy_modules: None
    ) -> None:
        """Reimporting the module with importlib.reload should trigger warning."""
        # Initial import
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            import omnibase_spi.protocols.nodes.legacy as legacy_module

        # Reload should trigger warning again
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            importlib.reload(legacy_module)

            deprecation_warnings = [
                w for w in caught_warnings if issubclass(w.category, DeprecationWarning)
            ]
            assert (
                len(deprecation_warnings) >= 1
            ), "Expected DeprecationWarning on module reload"


class TestLegacyProtocolAllExports:
    """Tests for __all__ exports from legacy module."""

    def test_all_legacy_protocols_in_module_all(self) -> None:
        """All legacy protocols should be listed in __all__."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes import legacy

            expected_exports = [
                "ProtocolComputeNodeLegacy",
                "ProtocolEffectNodeLegacy",
                "ProtocolOrchestratorNodeLegacy",
                "ProtocolReducerNodeLegacy",
            ]
            for export in expected_exports:
                assert export in legacy.__all__, f"Expected {export} in __all__"

    def test_all_exports_are_accessible(self) -> None:
        """All items in __all__ should be accessible as module attributes."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from omnibase_spi.protocols.nodes import legacy

            for export in legacy.__all__:
                assert hasattr(legacy, export), f"Expected {export} to be accessible"
                attr = getattr(legacy, export)
                assert attr is not None, f"Expected {export} to not be None"
