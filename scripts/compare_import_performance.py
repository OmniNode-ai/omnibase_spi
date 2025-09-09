#!/usr/bin/env python3
"""
Import Performance Comparison Tool

Compares the performance of the current eager loading implementation
with the proposed lazy loading optimization for omnibase-spi.

This script provides before/after analysis to validate the optimization
and ensure that performance improvements are measurable and significant.

Usage:
    python scripts/compare_import_performance.py
    python scripts/compare_import_performance.py --detailed
    python scripts/compare_import_performance.py --save-results results.json
"""

import argparse
import importlib.util
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


class ImportPerformanceComparator:
    """Compare import performance between current and optimized implementations."""

    def __init__(self) -> None:
        self.project_root = Path.cwd()
        self.src_path = self.project_root / "src"
        self.init_file = self.src_path / "omnibase_spi" / "__init__.py"
        self.lazy_file = self.src_path / "omnibase_spi" / "__init__.py.lazy"
        self.backup_file = self.src_path / "omnibase_spi" / "__init__.py.backup"

    def run_comparison(self, iterations: int = 10) -> Dict[str, Any]:
        """Run comprehensive performance comparison."""
        results = {
            "metadata": {
                "iterations": iterations,
                "python_version": sys.version_info[:3],
                "platform": sys.platform,
            },
            "current_implementation": {},
            "optimized_implementation": {},
            "comparison": {},
        }

        print("🔍 Running Import Performance Comparison...")
        print(f"   Iterations: {iterations}")
        print(f"   Python: {sys.version_info[:3]}")

        # Test current implementation
        print("\n📊 Testing Current Implementation (Eager Loading)...")
        if self.init_file.exists():
            results["current_implementation"] = self._benchmark_implementation(
                "current", iterations, use_lazy=False
            )
        else:
            print("   ⚠️  Current __init__.py not found")

        # Test optimized implementation
        print("\n🚀 Testing Optimized Implementation (Lazy Loading)...")
        if self.lazy_file.exists():
            results["optimized_implementation"] = self._benchmark_implementation(
                "optimized", iterations, use_lazy=True
            )
        else:
            print("   ⚠️  Lazy __init__.py.lazy not found")

        # Generate comparison
        results["comparison"] = self._generate_comparison(
            results.get("current_implementation", {}),
            results.get("optimized_implementation", {}),
        )

        return results

    def _benchmark_implementation(
        self, name: str, iterations: int, use_lazy: bool
    ) -> Dict[str, Any]:
        """Benchmark a specific implementation."""
        # Backup and switch implementations
        original_backed_up = self._switch_to_implementation(use_lazy)

        try:
            # Run benchmark
            benchmark_results = self._run_benchmark_iterations(iterations)

            # Add implementation metadata
            benchmark_results["implementation"] = {
                "name": name,
                "type": "lazy_loading" if use_lazy else "eager_loading",
                "file_used": "__init__.py.lazy" if use_lazy else "__init__.py",
            }

            return benchmark_results

        finally:
            # Restore original implementation
            self._restore_original_implementation(original_backed_up)

    def _switch_to_implementation(self, use_lazy: bool) -> bool:
        """Switch to the specified implementation, return True if backup was made."""
        # Backup current implementation if it exists
        backed_up = False
        if self.init_file.exists():
            shutil.copy2(self.init_file, self.backup_file)
            backed_up = True

        if use_lazy:
            # Copy lazy implementation to active position
            if self.lazy_file.exists():
                shutil.copy2(self.lazy_file, self.init_file)
            else:
                raise FileNotFoundError("Lazy implementation file not found")
        else:
            # Use current implementation (already in place or restore from backup)
            if not self.init_file.exists() and self.backup_file.exists():
                shutil.copy2(self.backup_file, self.init_file)

        return backed_up

    def _restore_original_implementation(self, was_backed_up: bool) -> None:
        """Restore the original implementation."""
        if was_backed_up and self.backup_file.exists():
            shutil.copy2(self.backup_file, self.init_file)
            self.backup_file.unlink()  # Remove backup

    def _run_benchmark_iterations(self, iterations: int) -> Dict[str, Any]:
        """Run benchmark iterations for current implementation."""
        sys.path.insert(0, str(self.src_path))

        results: Dict[str, Any] = {
            "iterations": [],
            "statistics": {},
            "memory_analysis": {},
            "protocol_analysis": {},
        }

        for i in range(iterations):
            iteration_result = self._run_single_iteration(i + 1)
            results["iterations"].append(iteration_result)

        # Calculate statistics
        results["statistics"] = self._calculate_statistics(results["iterations"])

        # Run additional analysis on final iteration
        self._reset_modules()
        results["memory_analysis"] = self._analyze_memory_usage()
        results["protocol_analysis"] = self._analyze_protocol_access()

        return results

    def _run_single_iteration(self, iteration_num: int) -> Dict[str, Any]:
        """Run a single benchmark iteration."""
        self._reset_modules()

        # Force garbage collection
        import gc

        gc.collect()

        # Measure import time
        start_time = time.perf_counter()

        try:
            import omnibase_spi

            import_time = (time.perf_counter() - start_time) * 1000

            # Count loaded modules
            omnibase_modules = [m for m in sys.modules if "omnibase_spi" in m]
            total_modules = len(sys.modules)

            # Check protocol availability
            protocols = [
                attr for attr in dir(omnibase_spi) if attr.startswith("Protocol")
            ]

            return {
                "iteration": iteration_num,
                "import_time_ms": round(import_time, 3),
                "omnibase_modules_loaded": len(omnibase_modules),
                "total_modules_loaded": total_modules,
                "protocol_count": len(protocols),
                "import_successful": True,
            }

        except Exception as e:
            return {
                "iteration": iteration_num,
                "import_time_ms": None,
                "import_successful": False,
                "error": str(e),
            }

    def _analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        self._reset_modules()

        # Baseline module count
        baseline_modules = len(sys.modules)

        # Import omnibase_spi
        import omnibase_spi

        after_import_modules = len(sys.modules)

        # Access a few protocols to trigger any lazy loading
        protocols_to_test = [
            "ProtocolLogger",
            "ProtocolEventBus",
            "ProtocolMCPRegistry",
        ]
        accessed_protocols = 0

        for protocol_name in protocols_to_test:
            try:
                _ = getattr(omnibase_spi, protocol_name)
                accessed_protocols += 1
            except AttributeError:
                pass  # Protocol not available in this implementation

        after_access_modules = len(sys.modules)

        return {
            "baseline_modules": baseline_modules,
            "after_import_modules": after_import_modules,
            "after_protocol_access_modules": after_access_modules,
            "import_overhead": after_import_modules - baseline_modules,
            "protocol_access_overhead": after_access_modules - after_import_modules,
            "protocols_tested": len(protocols_to_test),
            "protocols_accessible": accessed_protocols,
        }

    def _analyze_protocol_access(self) -> Dict[str, Any]:
        """Analyze protocol access performance."""
        self._reset_modules()
        import omnibase_spi

        protocols_to_test = [
            "ProtocolLogger",
            "ProtocolEventBus",
            "ProtocolMCPRegistry",
        ]
        access_results: Dict[str, Dict[str, Any]] = {}

        for protocol_name in protocols_to_test:
            try:
                # First access (may trigger lazy loading)
                start_time = time.perf_counter()
                protocol1 = getattr(omnibase_spi, protocol_name)
                first_access_time = (time.perf_counter() - start_time) * 1000

                # Second access (should be cached)
                start_time = time.perf_counter()
                protocol2 = getattr(omnibase_spi, protocol_name)
                second_access_time = (time.perf_counter() - start_time) * 1000

                access_results[protocol_name] = {
                    "first_access_ms": round(first_access_time, 3),
                    "second_access_ms": round(second_access_time, 3),
                    "is_cached": protocol1 is protocol2,
                    "accessible": True,
                }

            except AttributeError:
                access_results[protocol_name] = {
                    "accessible": False,
                    "error": f"Protocol {protocol_name} not available",
                }

        return access_results

    def _calculate_statistics(self, iterations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistical measures from iteration results."""
        successful_iterations = [
            it for it in iterations if it.get("import_successful", False)
        ]

        if not successful_iterations:
            return {"error": "No successful iterations"}

        import_times = [it["import_time_ms"] for it in successful_iterations]
        module_counts = [it["omnibase_modules_loaded"] for it in successful_iterations]

        return {
            "successful_iterations": len(successful_iterations),
            "failed_iterations": len(iterations) - len(successful_iterations),
            "import_time": {
                "mean": round(sum(import_times) / len(import_times), 3),
                "min": round(min(import_times), 3),
                "max": round(max(import_times), 3),
                "variance": round(max(import_times) - min(import_times), 3),
            },
            "module_loading": {
                "mean": round(sum(module_counts) / len(module_counts), 1),
                "min": min(module_counts),
                "max": max(module_counts),
            },
        }

    def _generate_comparison(
        self, current: Dict[str, Any], optimized: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comparison analysis between implementations."""
        if not current or not optimized:
            return {"error": "Missing implementation data for comparison"}

        comparison: Dict[str, Any] = {}

        # Import time comparison
        current_stats = current.get("statistics", {})
        optimized_stats = optimized.get("statistics", {})

        if "import_time" in current_stats and "import_time" in optimized_stats:
            current_time = current_stats["import_time"]["mean"]
            optimized_time = optimized_stats["import_time"]["mean"]

            improvement = ((current_time - optimized_time) / current_time) * 100
            speedup = (
                current_time / optimized_time if optimized_time > 0 else float("inf")
            )

            comparison["import_performance"] = {
                "current_mean_ms": current_time,
                "optimized_mean_ms": optimized_time,
                "improvement_percent": round(improvement, 1),
                "speedup_factor": round(speedup, 2),
                "absolute_savings_ms": round(current_time - optimized_time, 2),
            }

        # Memory usage comparison
        current_memory = current.get("memory_analysis", {})
        optimized_memory = optimized.get("memory_analysis", {})

        if (
            "import_overhead" in current_memory
            and "import_overhead" in optimized_memory
        ):
            current_overhead = current_memory["import_overhead"]
            optimized_overhead = optimized_memory["import_overhead"]

            memory_improvement = (
                (current_overhead - optimized_overhead) / current_overhead
            ) * 100

            comparison["memory_usage"] = {
                "current_modules_loaded": current_overhead,
                "optimized_modules_loaded": optimized_overhead,
                "memory_reduction_percent": round(memory_improvement, 1),
                "modules_saved": current_overhead - optimized_overhead,
            }

        # Overall assessment
        comparison["assessment"] = self._generate_assessment(comparison)

        return comparison

    def _generate_assessment(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment of the optimization."""
        assessment: Dict[str, Any] = {
            "optimization_successful": False,
            "key_improvements": [],
            "potential_concerns": [],
            "recommendation": "",
        }

        # Check import performance improvement
        if "import_performance" in comparison:
            perf = comparison["import_performance"]
            improvement = perf.get("improvement_percent", 0)

            if improvement > 10:
                assessment["optimization_successful"] = True
                assessment["key_improvements"].append(
                    f"Import time improved by {improvement}%"
                )
            elif improvement < -5:
                assessment["potential_concerns"].append(
                    "Import time regression detected"
                )

        # Check memory usage improvement
        if "memory_usage" in comparison:
            memory = comparison["memory_usage"]
            memory_reduction = memory.get("memory_reduction_percent", 0)

            if memory_reduction > 5:
                assessment["key_improvements"].append(
                    f"Memory usage reduced by {memory_reduction}%"
                )
            elif memory_reduction < -5:
                assessment["potential_concerns"].append("Memory usage increased")

        # Generate recommendation
        if (
            assessment["optimization_successful"]
            and not assessment["potential_concerns"]
        ):
            assessment["recommendation"] = "RECOMMEND: Apply lazy loading optimization"
        elif (
            assessment["key_improvements"] and len(assessment["potential_concerns"]) < 2
        ):
            assessment["recommendation"] = "CONSIDER: Benefits outweigh concerns"
        else:
            assessment["recommendation"] = "CAUTION: Review concerns before applying"

        return assessment

    def _reset_modules(self) -> None:
        """Reset omnibase_spi modules for clean testing."""
        modules_to_remove = [mod for mod in sys.modules if "omnibase_spi" in mod]
        for mod in modules_to_remove:
            del sys.modules[mod]


def print_results(results: Dict[str, Any]) -> None:
    """Print formatted results."""
    print("\n" + "=" * 80)
    print("📊 IMPORT PERFORMANCE COMPARISON RESULTS")
    print("=" * 80)

    # Metadata
    metadata = results.get("metadata", {})
    print(f"\n🔧 Test Configuration:")
    print(f"   Iterations: {metadata.get('iterations', 'N/A')}")
    print(f"   Python Version: {metadata.get('python_version', 'N/A')}")
    print(f"   Platform: {metadata.get('platform', 'N/A')}")

    # Current implementation results
    current = results.get("current_implementation", {})
    if current:
        print(f"\n📈 Current Implementation (Eager Loading):")
        stats = current.get("statistics", {})
        if "import_time" in stats:
            time_stats = stats["import_time"]
            print(
                f"   Import Time: {time_stats['mean']}ms (min: {time_stats['min']}ms, max: {time_stats['max']}ms)"
            )

        memory = current.get("memory_analysis", {})
        if "import_overhead" in memory:
            print(f"   Modules Loaded: {memory['import_overhead']}")

    # Optimized implementation results
    optimized = results.get("optimized_implementation", {})
    if optimized:
        print(f"\n🚀 Optimized Implementation (Lazy Loading):")
        stats = optimized.get("statistics", {})
        if "import_time" in stats:
            time_stats = stats["import_time"]
            print(
                f"   Import Time: {time_stats['mean']}ms (min: {time_stats['min']}ms, max: {time_stats['max']}ms)"
            )

        memory = optimized.get("memory_analysis", {})
        if "import_overhead" in memory:
            print(f"   Modules Loaded: {memory['import_overhead']}")

    # Comparison
    comparison = results.get("comparison", {})
    if comparison:
        print(f"\n⚖️  Performance Comparison:")

        if "import_performance" in comparison:
            perf = comparison["import_performance"]
            print(
                f"   Import Time Improvement: {perf.get('improvement_percent', 'N/A')}%"
            )
            print(f"   Speedup Factor: {perf.get('speedup_factor', 'N/A')}x")
            print(f"   Time Saved: {perf.get('absolute_savings_ms', 'N/A')}ms")

        if "memory_usage" in comparison:
            memory = comparison["memory_usage"]
            print(
                f"   Memory Reduction: {memory.get('memory_reduction_percent', 'N/A')}%"
            )
            print(f"   Modules Saved: {memory.get('modules_saved', 'N/A')}")

        # Assessment
        assessment = comparison.get("assessment", {})
        if assessment:
            print(f"\n🎯 Assessment:")
            print(
                f"   Optimization Successful: {assessment.get('optimization_successful', False)}"
            )

            improvements = assessment.get("key_improvements", [])
            if improvements:
                print(f"   Key Improvements:")
                for improvement in improvements:
                    print(f"     ✅ {improvement}")

            concerns = assessment.get("potential_concerns", [])
            if concerns:
                print(f"   Potential Concerns:")
                for concern in concerns:
                    print(f"     ⚠️  {concern}")

            recommendation = assessment.get("recommendation", "")
            if recommendation:
                print(f"   Recommendation: {recommendation}")


def main() -> None:
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Compare import performance implementations"
    )
    parser.add_argument(
        "--iterations", type=int, default=10, help="Number of benchmark iterations"
    )
    parser.add_argument("--detailed", action="store_true", help="Show detailed results")
    parser.add_argument("--save-results", type=str, help="Save results to JSON file")

    args = parser.parse_args()

    comparator = ImportPerformanceComparator()

    try:
        results = comparator.run_comparison(args.iterations)

        print_results(results)

        if args.detailed:
            print(f"\n📋 Detailed Results:")
            print(json.dumps(results, indent=2))

        if args.save_results:
            with open(args.save_results, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {args.save_results}")

    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
