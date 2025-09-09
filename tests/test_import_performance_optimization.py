"""
Comprehensive Import Performance and Validation Tests

Tests for import performance optimization, lazy loading validation, circular import prevention,
and comprehensive import validation for the omnibase-spi package.

Test Coverage:
    - Import performance benchmarking
    - Lazy loading functionality validation
    - Circular import detection and prevention
    - Root-level protocol availability validation
    - Import regression prevention
    - Memory usage optimization validation
    - Protocol access performance measurement
"""

import importlib
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set
from unittest.mock import patch

import pytest


class TestImportPerformance:
    """Test suite for import performance optimization."""

    def test_root_import_performance_baseline(self) -> None:
        """Test that root import meets performance requirements."""
        # Remove any existing omnibase_spi modules for clean test
        self._reset_omnibase_modules()

        # Measure import time
        start_time = time.perf_counter()
        import omnibase_spi

        import_time = (time.perf_counter() - start_time) * 1000

        # Performance assertions
        assert (
            import_time < 100
        ), f"Root import time {import_time:.2f}ms exceeds 100ms threshold"

        # Check that protocols are available
        protocols = [attr for attr in dir(omnibase_spi) if attr.startswith("Protocol")]
        assert (
            len(protocols) >= 10
        ), f"Expected at least 10 protocols, got {len(protocols)}"

        # Memory usage check
        omnibase_modules = [m for m in sys.modules if "omnibase_spi" in m]
        assert (
            len(omnibase_modules) < 50
        ), f"Too many modules loaded: {len(omnibase_modules)}"

    def test_lazy_loading_functionality(self) -> None:
        """Test that lazy loading works correctly."""
        self._reset_omnibase_modules()

        # Import the root module
        import omnibase_spi

        # Initially, protocol modules should not be loaded
        initial_modules = set(sys.modules.keys())

        # Access a protocol - this should trigger lazy loading
        protocol_logger = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]
        assert protocol_logger is not None

        # Check that the protocol module was loaded
        loaded_modules = set(sys.modules.keys()) - initial_modules
        logger_modules = [m for m in loaded_modules if "protocol_logger" in m]
        assert (
            len(logger_modules) > 0
        ), "Protocol logger module should be loaded after access"

    def test_protocol_access_performance(self) -> None:
        """Test performance of individual protocol access."""
        self._reset_omnibase_modules()
        import omnibase_spi

        # Test protocols to measure
        test_protocols = ["ProtocolLogger", "ProtocolEventBus", "ProtocolMCPRegistry"]

        for protocol_name in test_protocols:
            # First access (lazy loading)
            start_time = time.perf_counter()
            protocol = getattr(omnibase_spi, protocol_name)
            first_access_time = (time.perf_counter() - start_time) * 1000

            # Second access (should be cached)
            start_time = time.perf_counter()
            protocol_cached = getattr(omnibase_spi, protocol_name)
            cached_access_time = (time.perf_counter() - start_time) * 1000

            # Assertions
            assert protocol is not None
            assert protocol is protocol_cached, "Should return same cached instance"
            assert (
                first_access_time < 10
            ), f"First access to {protocol_name} too slow: {first_access_time:.2f}ms"
            assert (
                cached_access_time < 0.1
            ), f"Cached access to {protocol_name} too slow: {cached_access_time:.2f}ms"

    def test_import_performance_regression(self) -> None:
        """Test that import performance doesn't regress."""
        # Run multiple iterations to get stable measurements
        import_times = []

        for _ in range(5):
            self._reset_omnibase_modules()

            start_time = time.perf_counter()
            import omnibase_spi

            import_time = (time.perf_counter() - start_time) * 1000
            import_times.append(import_time)

        # Calculate statistics
        avg_time = sum(import_times) / len(import_times)
        max_time = max(import_times)

        # Performance regression checks
        assert avg_time < 80, f"Average import time {avg_time:.2f}ms exceeds threshold"
        assert max_time < 150, f"Maximum import time {max_time:.2f}ms exceeds threshold"

        # Variance should be reasonable
        variance = max_time - min(import_times)
        assert variance < 50, f"Import time variance {variance:.2f}ms too high"

    @staticmethod
    def _reset_omnibase_modules() -> None:
        """Remove all omnibase_spi modules from sys.modules."""
        modules_to_remove = [mod for mod in sys.modules if "omnibase_spi" in mod]
        for mod in modules_to_remove:
            del sys.modules[mod]


class TestLazyLoading:
    """Test suite for lazy loading functionality."""

    def test_lazy_loading_mechanism(self) -> None:
        """Test that __getattr__ lazy loading works correctly."""
        TestImportPerformance._reset_omnibase_modules()

        # Import root module
        import omnibase_spi

        # Test that __getattr__ is called for lazy loading
        with patch("omnibase_spi._load_protocol") as mock_load:
            mock_load.return_value = "MockProtocol"

            # Access a protocol
            result = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]

            # Verify lazy loading was called
            mock_load.assert_called_once_with("ProtocolLogger")
            assert result == "MockProtocol"  # type: ignore[comparison-overlap]

    def test_protocol_caching(self) -> None:
        """Test that protocols are cached after first load."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        # Clear any existing cache
        if hasattr(omnibase_spi, "_protocol_cache"):
            omnibase_spi._protocol_cache.clear()

        # First access
        protocol1 = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]

        # Second access should return same instance
        protocol2 = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]

        assert (
            protocol1 is protocol2
        ), "Protocol should be cached and return same instance"

    def test_invalid_protocol_access(self) -> None:
        """Test handling of invalid protocol access."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        # Test accessing non-existent protocol
        with pytest.raises(
            AttributeError, match="has no attribute 'NonExistentProtocol'"
        ):
            _ = omnibase_spi.NonExistentProtocol

    def test_dir_functionality(self) -> None:
        """Test that __dir__ works correctly for introspection."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        available_attrs = dir(omnibase_spi)

        # Check that standard attributes are present
        assert "__version__" in available_attrs
        assert "__author__" in available_attrs

        # Check that protocols are listed
        protocols = [attr for attr in available_attrs if attr.startswith("Protocol")]
        assert (
            len(protocols) >= 10
        ), f"Expected at least 10 protocols in dir(), got {len(protocols)}"

        # Check that all listed protocols are accessible
        for protocol_name in protocols[:5]:  # Test first 5 protocols
            protocol = getattr(omnibase_spi, protocol_name)
            assert (
                protocol is not None
            ), f"Listed protocol {protocol_name} should be accessible"


class TestImportValidation:
    """Test suite for comprehensive import validation."""

    def test_all_root_exports_are_valid(self) -> None:
        """Test that all protocols listed in __all__ can be imported."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        # Get all exported protocols
        all_exports = omnibase_spi.__all__
        protocols = [exp for exp in all_exports if exp.startswith("Protocol")]

        # Test each protocol can be accessed
        for protocol_name in protocols:
            try:
                protocol = getattr(omnibase_spi, protocol_name)
                assert (
                    protocol is not None
                ), f"Protocol {protocol_name} should not be None"

                # Check that it's a protocol (has Protocol in the name or is callable)
                assert hasattr(protocol, "__name__") or callable(
                    protocol
                ), f"{protocol_name} should be a protocol class"

            except Exception as e:
                pytest.fail(f"Failed to access protocol {protocol_name}: {e}")

    def test_protocol_type_checking_compatibility(self) -> None:
        """Test that protocols work with type checking tools."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        # Test a few key protocols
        key_protocols = ["ProtocolLogger", "ProtocolEventBus", "ProtocolMCPRegistry"]

        for protocol_name in key_protocols:
            protocol = getattr(omnibase_spi, protocol_name)

            # Check that protocol has proper attributes for type checking
            assert hasattr(
                protocol, "__name__"
            ), f"{protocol_name} should have __name__"
            assert hasattr(
                protocol, "__module__"
            ), f"{protocol_name} should have __module__"

            # For Protocol classes, check they have the runtime_checkable decorator
            if hasattr(protocol, "_is_protocol"):
                assert (
                    protocol._is_protocol
                ), f"{protocol_name} should be marked as protocol"

    def test_backward_compatibility(self) -> None:
        """Test that new lazy loading maintains backward compatibility."""
        TestImportPerformance._reset_omnibase_modules()

        # Test that old import patterns still work
        try:
            # Standard import pattern
            from omnibase_spi import ProtocolLogger  # type: ignore[attr-defined]

            assert ProtocolLogger is not None

            # Multiple imports
            from omnibase_spi import (  # type: ignore[attr-defined]
                ProtocolEventBus,
                ProtocolLogger,
            )

            assert ProtocolLogger is not None
            assert ProtocolEventBus is not None

            # Import with alias
            from omnibase_spi import ProtocolLogger as Logger  # type: ignore[attr-defined]

            assert Logger is not None

        except ImportError as e:
            pytest.fail(f"Backward compatibility broken: {e}")

    def test_direct_protocol_imports_still_work(self) -> None:
        """Test that direct protocol imports (recommended approach) still work."""
        TestImportPerformance._reset_omnibase_modules()

        # Test direct imports from protocol modules
        try:
            from omnibase_spi.protocols.core import ProtocolLogger

            assert ProtocolLogger is not None

            from omnibase_spi.protocols.workflow_orchestration import (
                ProtocolWorkflowEventBus,
            )

            assert ProtocolWorkflowEventBus is not None

            from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

            assert ProtocolMCPRegistry is not None

        except ImportError as e:
            pytest.fail(f"Direct protocol import failed: {e}")


class TestCircularImportPrevention:
    """Test suite for circular import detection and prevention."""

    def test_no_circular_imports_in_protocol_structure(self) -> None:
        """Test that there are no circular imports in the protocol structure."""
        # This test uses static analysis to detect potential circular imports
        from omnibase_spi.scripts.import_performance_analyzer import (
            ImportPerformanceAnalyzer,
        )

        analyzer = ImportPerformanceAnalyzer()
        circular_results = analyzer._detect_circular_imports()

        assert not circular_results[
            "has_circular_imports"
        ], f"Circular imports detected: {circular_results['circular_imports']}"

    def test_root_init_does_not_create_cycles(self) -> None:
        """Test that the root __init__.py doesn't create circular import cycles."""
        TestImportPerformance._reset_omnibase_modules()

        # Import root module
        import omnibase_spi

        # Test accessing multiple protocols doesn't cause issues
        protocols_to_test = [
            "ProtocolLogger",
            "ProtocolEventBus",
            "ProtocolMCPRegistry",
        ]

        for protocol_name in protocols_to_test:
            try:
                protocol = getattr(omnibase_spi, protocol_name)
                assert protocol is not None
            except ImportError as e:
                if "circular import" in str(e).lower():
                    pytest.fail(
                        f"Circular import detected when accessing {protocol_name}: {e}"
                    )
                else:
                    pytest.fail(f"Import error accessing {protocol_name}: {e}")


class TestDocumentationAccuracy:
    """Test suite for documentation accuracy and consistency."""

    def test_protocol_count_accuracy(self) -> None:
        """Test that documented protocol counts match actual counts."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        # Get actual protocol count
        protocols = [attr for attr in dir(omnibase_spi) if attr.startswith("Protocol")]
        actual_count = len(protocols)

        # Check if dynamic counting is available
        if hasattr(omnibase_spi, "__protocol_count__"):
            documented_count = omnibase_spi.__protocol_count__
            assert (
                actual_count == documented_count
            ), f"Documented protocol count {documented_count} doesn't match actual {actual_count}"

    def test_all_exports_match_available_protocols(self) -> None:
        """Test that __all__ exactly matches what's actually available."""
        TestImportPerformance._reset_omnibase_modules()
        import omnibase_spi

        # Get protocols from __all__
        all_protocols = [
            item for item in omnibase_spi.__all__ if item.startswith("Protocol")
        ]

        # Get actually available protocols
        available_protocols = [
            attr for attr in dir(omnibase_spi) if attr.startswith("Protocol")
        ]

        # They should match exactly
        assert set(all_protocols) == set(
            available_protocols
        ), f"__all__ protocols {set(all_protocols)} don't match available {set(available_protocols)}"


class TestPerformanceOptimization:
    """Test suite for performance optimization validation."""

    def test_memory_usage_optimization(self) -> None:
        """Test that lazy loading reduces memory usage."""
        TestImportPerformance._reset_omnibase_modules()

        # Measure modules before import
        modules_before = len(sys.modules)

        # Import root module
        import omnibase_spi

        # Measure modules after root import (should be minimal)
        modules_after_root = len(sys.modules)
        root_import_overhead = modules_after_root - modules_before

        # Access one protocol
        _ = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]

        # Measure modules after protocol access
        modules_after_protocol = len(sys.modules)
        protocol_access_overhead = modules_after_protocol - modules_after_root

        # Assertions for memory optimization
        assert (
            root_import_overhead < 10
        ), f"Root import loaded too many modules: {root_import_overhead}"
        assert (
            protocol_access_overhead < 5
        ), f"Protocol access loaded too many modules: {protocol_access_overhead}"

    def test_import_time_optimization_vs_direct_import(self) -> None:
        """Test that lazy loading provides better performance than eager loading."""
        # This test compares the optimized lazy loading with direct imports

        # Test direct import time
        TestImportPerformance._reset_omnibase_modules()
        start_time = time.perf_counter()
        from omnibase_spi.protocols.core import ProtocolLogger

        direct_import_time = (time.perf_counter() - start_time) * 1000

        # Test lazy loading root import time
        TestImportPerformance._reset_omnibase_modules()
        start_time = time.perf_counter()
        import omnibase_spi

        lazy_root_time = (time.perf_counter() - start_time) * 1000

        # Test protocol access time through lazy loading
        start_time = time.perf_counter()
        _ = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]
        lazy_access_time = (time.perf_counter() - start_time) * 1000

        # The total lazy loading time should be competitive with direct imports
        total_lazy_time = lazy_root_time + lazy_access_time

        # Allow some overhead for lazy loading mechanism
        acceptable_overhead = 2.0  # 2x overhead is acceptable for the convenience
        assert total_lazy_time < (
            direct_import_time * acceptable_overhead
        ), f"Lazy loading total time {total_lazy_time:.2f}ms exceeds acceptable overhead vs direct {direct_import_time:.2f}ms"


# Integration test to validate the complete optimization
def test_complete_optimization_integration() -> None:
    """Integration test for the complete import optimization solution."""
    TestImportPerformance._reset_omnibase_modules()

    # 1. Test fast root import
    start_time = time.perf_counter()
    import omnibase_spi

    root_import_time = (time.perf_counter() - start_time) * 1000

    assert (
        root_import_time < 50
    ), f"Root import should be fast: {root_import_time:.2f}ms"

    # 2. Test protocol availability
    protocols = [attr for attr in dir(omnibase_spi) if attr.startswith("Protocol")]
    assert len(protocols) >= 10, "Should have adequate protocol coverage"

    # 3. Test lazy loading functionality
    protocol = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]
    assert protocol is not None, "Lazy loading should work"

    # 4. Test caching
    protocol2 = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]
    assert protocol is protocol2, "Caching should work"

    # 5. Test introspection
    assert "ProtocolLogger" in dir(omnibase_spi), "Introspection should work"

    print(f"✅ Complete optimization integration test passed")
    print(f"   Root import time: {root_import_time:.2f}ms")
    print(f"   Protocols available: {len(protocols)}")
    print(f"   Lazy loading: ✅")
    print(f"   Caching: ✅")
    print(f"   Introspection: ✅")
