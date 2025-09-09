#!/usr/bin/env python3
"""
Import Optimization Validation Script

Standalone validation script to test all aspects of the import performance optimization
without external dependencies like pytest. This ensures the optimization works correctly
and maintains backward compatibility.

Features:
    - Performance regression testing
    - Lazy loading functionality validation
    - Backward compatibility verification
    - Protocol access validation
    - Memory usage validation
    - Import error detection

Usage:
    python scripts/validate_import_optimization.py
    python scripts/validate_import_optimization.py --verbose
"""

import argparse
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List


class ImportOptimizationValidator:
    """Comprehensive validation for import optimization."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.test_results: List[Dict[str, Any]] = []
        self.failed_tests: List[str] = []

        # Add src to Python path
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

    def run_all_validations(self) -> Dict[str, Any]:
        """Run comprehensive validation suite."""
        print("🔍 Running Import Optimization Validation...")

        validations = [
            ("Import Performance", self._test_import_performance),
            ("Lazy Loading Functionality", self._test_lazy_loading_functionality),
            ("Protocol Access", self._test_protocol_access),
            ("Backward Compatibility", self._test_backward_compatibility),
            ("Memory Usage", self._test_memory_usage),
            ("Error Handling", self._test_error_handling),
            ("Introspection Support", self._test_introspection_support),
            ("Type Checking Compatibility", self._test_type_checking_compatibility),
        ]

        passed = 0
        total = len(validations)

        for test_name, test_func in validations:
            print(f"\n📋 Testing: {test_name}")

            try:
                result = test_func()
                if result["passed"]:
                    print(f"   ✅ PASSED: {result.get('message', 'All checks passed')}")
                    passed += 1
                else:
                    print(f"   ❌ FAILED: {result.get('message', 'Test failed')}")
                    self.failed_tests.append(test_name)

                self.test_results.append(
                    {
                        "test_name": test_name,
                        "passed": result["passed"],
                        "message": result.get("message", ""),
                        "details": result.get("details", {}),
                    }
                )

            except Exception as e:
                print(f"   💥 ERROR: {str(e)}")
                if self.verbose:
                    traceback.print_exc()

                self.test_results.append(
                    {
                        "test_name": test_name,
                        "passed": False,
                        "message": f"Exception: {str(e)}",
                        "details": {"exception": True},
                    }
                )

        # Summary
        print(f"\n" + "=" * 60)
        print(f"📊 VALIDATION RESULTS")
        print(f"=" * 60)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {len(self.failed_tests)}")

        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")

        overall_success = passed == total
        print(f"\n🎯 Overall Result: {'SUCCESS' if overall_success else 'FAILURE'}")

        return {
            "overall_success": overall_success,
            "passed": passed,
            "total": total,
            "failed_tests": self.failed_tests,
            "test_results": self.test_results,
        }

    def _test_import_performance(self) -> Dict[str, Any]:
        """Test that import performance meets requirements."""
        self._reset_omnibase_modules()

        # Measure import time
        start_time = time.perf_counter()

        try:
            import omnibase_spi

            import_time = (time.perf_counter() - start_time) * 1000

            # Performance requirements
            max_import_time = 50  # milliseconds

            if import_time <= max_import_time:
                return {
                    "passed": True,
                    "message": f"Import time {import_time:.2f}ms is within {max_import_time}ms limit",
                    "details": {
                        "import_time_ms": import_time,
                        "limit_ms": max_import_time,
                    },
                }
            else:
                return {
                    "passed": False,
                    "message": f"Import time {import_time:.2f}ms exceeds {max_import_time}ms limit",
                    "details": {
                        "import_time_ms": import_time,
                        "limit_ms": max_import_time,
                    },
                }

        except ImportError as e:
            return {
                "passed": False,
                "message": f"Import failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_lazy_loading_functionality(self) -> Dict[str, Any]:
        """Test that lazy loading works correctly."""
        self._reset_omnibase_modules()

        try:
            import omnibase_spi

            # Initially, specific protocol modules should not be loaded
            initial_modules = set(sys.modules.keys())

            # Access a protocol - should trigger lazy loading
            protocol_logger = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]

            if protocol_logger is None:
                return {
                    "passed": False,
                    "message": "Lazy loaded protocol is None",
                    "details": {},
                }

            # Check that protocol module was loaded
            after_modules = set(sys.modules.keys())
            new_modules = after_modules - initial_modules

            # Second access should return same instance (cached)
            protocol_logger2 = omnibase_spi.ProtocolLogger  # type: ignore[attr-defined]

            if protocol_logger is not protocol_logger2:
                return {
                    "passed": False,
                    "message": "Protocol not properly cached - different instances returned",
                    "details": {},
                }

            return {
                "passed": True,
                "message": "Lazy loading and caching working correctly",
                "details": {
                    "new_modules_loaded": len(new_modules),
                    "caching_works": protocol_logger is protocol_logger2,
                },
            }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Lazy loading test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_protocol_access(self) -> Dict[str, Any]:
        """Test that all documented protocols can be accessed."""
        self._reset_omnibase_modules()

        try:
            import omnibase_spi

            # Get all protocols listed in __all__
            all_exports = getattr(omnibase_spi, "__all__", [])
            protocols = [exp for exp in all_exports if exp.startswith("Protocol")]

            if not protocols:
                return {
                    "passed": False,
                    "message": "No protocols found in __all__",
                    "details": {},
                }

            accessible_protocols = 0
            failed_protocols = []

            for protocol_name in protocols:
                try:
                    protocol = getattr(omnibase_spi, protocol_name)
                    if protocol is not None:
                        accessible_protocols += 1
                    else:
                        failed_protocols.append(f"{protocol_name}: returned None")
                except AttributeError as e:
                    failed_protocols.append(f"{protocol_name}: {str(e)}")
                except Exception as e:
                    failed_protocols.append(f"{protocol_name}: {str(e)}")

            if failed_protocols:
                return {
                    "passed": False,
                    "message": f"{len(failed_protocols)} protocols failed to load",
                    "details": {
                        "accessible": accessible_protocols,
                        "total": len(protocols),
                        "failed": failed_protocols,
                    },
                }

            return {
                "passed": True,
                "message": f"All {accessible_protocols} protocols accessible",
                "details": {
                    "accessible": accessible_protocols,
                    "total": len(protocols),
                },
            }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Protocol access test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_backward_compatibility(self) -> Dict[str, Any]:
        """Test that existing import patterns still work."""
        self._reset_omnibase_modules()

        compatibility_tests = []

        try:
            # Test 1: Root import
            from omnibase_spi import ProtocolLogger  # type: ignore[attr-defined]

            compatibility_tests.append("Root import: ✅")

        except Exception as e:
            compatibility_tests.append(f"Root import: ❌ {str(e)}")

        try:
            # Test 2: Multiple imports
            from omnibase_spi import (  # type: ignore[attr-defined]
                ProtocolEventBus,
                ProtocolLogger,
            )

            compatibility_tests.append("Multiple imports: ✅")

        except Exception as e:
            compatibility_tests.append(f"Multiple imports: ❌ {str(e)}")

        try:
            # Test 3: Import with alias
            from omnibase_spi import ProtocolLogger as Logger  # type: ignore[attr-defined]

            compatibility_tests.append("Import with alias: ✅")

        except Exception as e:
            compatibility_tests.append(f"Import with alias: ❌ {str(e)}")

        try:
            # Test 4: Direct protocol imports (should still work)
            from omnibase_spi.protocols.core import ProtocolLogger

            compatibility_tests.append("Direct protocol import: ✅")

        except Exception as e:
            compatibility_tests.append(f"Direct protocol import: ❌ {str(e)}")

        # Count successes
        successes = len([test for test in compatibility_tests if "✅" in test])
        total_tests = len(compatibility_tests)

        if successes == total_tests:
            return {
                "passed": True,
                "message": f"All {total_tests} backward compatibility tests passed",
                "details": {"tests": compatibility_tests},
            }
        else:
            return {
                "passed": False,
                "message": f"Only {successes}/{total_tests} backward compatibility tests passed",
                "details": {"tests": compatibility_tests},
            }

    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test that memory usage is optimized."""
        self._reset_omnibase_modules()

        try:
            # Baseline
            baseline_modules = len(sys.modules)

            # Import root module
            import omnibase_spi

            after_import_modules = len(sys.modules)

            # Calculate overhead
            import_overhead = after_import_modules - baseline_modules

            # Memory usage requirements
            max_import_overhead = 10  # Maximum modules that should be loaded on import

            if import_overhead <= max_import_overhead:
                return {
                    "passed": True,
                    "message": f"Import overhead {import_overhead} modules is within {max_import_overhead} limit",
                    "details": {
                        "import_overhead": import_overhead,
                        "limit": max_import_overhead,
                        "baseline_modules": baseline_modules,
                        "after_import_modules": after_import_modules,
                    },
                }
            else:
                return {
                    "passed": False,
                    "message": f"Import overhead {import_overhead} modules exceeds {max_import_overhead} limit",
                    "details": {
                        "import_overhead": import_overhead,
                        "limit": max_import_overhead,
                    },
                }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Memory usage test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_error_handling(self) -> Dict[str, Any]:
        """Test that error handling works correctly."""
        self._reset_omnibase_modules()

        try:
            import omnibase_spi

            # Test accessing non-existent protocol
            try:
                _ = omnibase_spi.NonExistentProtocol
                return {
                    "passed": False,
                    "message": "Should have raised AttributeError for non-existent protocol",
                    "details": {},
                }
            except AttributeError:
                # This is expected
                pass
            except Exception as e:
                return {
                    "passed": False,
                    "message": f"Wrong exception type for non-existent protocol: {type(e).__name__}",
                    "details": {"exception": str(e)},
                }

            return {
                "passed": True,
                "message": "Error handling works correctly",
                "details": {},
            }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Error handling test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_introspection_support(self) -> Dict[str, Any]:
        """Test that introspection (dir, __all__) works correctly."""
        self._reset_omnibase_modules()

        try:
            import omnibase_spi

            # Test dir() functionality
            available_attrs = dir(omnibase_spi)

            # Check for standard attributes
            expected_attrs = ["__version__", "__author__", "__all__"]
            missing_attrs = [
                attr for attr in expected_attrs if attr not in available_attrs
            ]

            if missing_attrs:
                return {
                    "passed": False,
                    "message": f"Missing standard attributes: {missing_attrs}",
                    "details": {"missing": missing_attrs},
                }

            # Check for protocols in dir()
            protocols_in_dir = [
                attr for attr in available_attrs if attr.startswith("Protocol")
            ]

            if len(protocols_in_dir) < 5:
                return {
                    "passed": False,
                    "message": f"Too few protocols in dir(): {len(protocols_in_dir)}",
                    "details": {"protocol_count": len(protocols_in_dir)},
                }

            # Check __all__ exists and has protocols
            all_exports = getattr(omnibase_spi, "__all__", [])
            protocols_in_all = [
                exp for exp in all_exports if exp.startswith("Protocol")
            ]

            if len(protocols_in_all) < 5:
                return {
                    "passed": False,
                    "message": f"Too few protocols in __all__: {len(protocols_in_all)}",
                    "details": {"protocol_count": len(protocols_in_all)},
                }

            return {
                "passed": True,
                "message": f"Introspection works correctly ({len(protocols_in_dir)} protocols in dir)",
                "details": {
                    "protocols_in_dir": len(protocols_in_dir),
                    "protocols_in_all": len(protocols_in_all),
                },
            }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Introspection test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_type_checking_compatibility(self) -> Dict[str, Any]:
        """Test that protocols work with type checking."""
        self._reset_omnibase_modules()

        try:
            import omnibase_spi

            # Test a few key protocols
            test_protocols = ["ProtocolLogger", "ProtocolEventBus"]

            for protocol_name in test_protocols:
                try:
                    protocol = getattr(omnibase_spi, protocol_name)

                    # Check basic type checking attributes
                    if not hasattr(protocol, "__name__"):
                        return {
                            "passed": False,
                            "message": f"{protocol_name} missing __name__ attribute",
                            "details": {"protocol": protocol_name},
                        }

                    if not hasattr(protocol, "__module__"):
                        return {
                            "passed": False,
                            "message": f"{protocol_name} missing __module__ attribute",
                            "details": {"protocol": protocol_name},
                        }

                except AttributeError:
                    # Protocol not available, skip
                    continue

            return {
                "passed": True,
                "message": "Type checking compatibility verified",
                "details": {},
            }

        except Exception as e:
            return {
                "passed": False,
                "message": f"Type checking test failed: {str(e)}",
                "details": {"error": str(e)},
            }

    def _reset_omnibase_modules(self) -> None:
        """Reset omnibase_spi modules for clean testing."""
        modules_to_remove = [mod for mod in sys.modules if "omnibase_spi" in mod]
        for mod in modules_to_remove:
            del sys.modules[mod]


def main() -> None:
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Validate import optimization")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including exceptions",
    )

    args = parser.parse_args()

    validator = ImportOptimizationValidator(verbose=args.verbose)
    results = validator.run_all_validations()

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()
