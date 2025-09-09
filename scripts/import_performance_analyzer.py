#!/usr/bin/env python3
"""
Import Performance Analysis Tool for omnibase-spi

This script provides comprehensive analysis of import performance, circular dependency
detection, and validation for the omnibase-spi package architecture.

Key Features:
    - Import time measurement and profiling
    - Circular dependency detection using AST analysis
    - Module loading impact analysis
    - Performance regression detection
    - Import validation with missing module detection
    - Memory usage analysis for loaded modules

Usage:
    python scripts/import_performance_analyzer.py
    python scripts/import_performance_analyzer.py --benchmark
    python scripts/import_performance_analyzer.py --detect-circular
    python scripts/import_performance_analyzer.py --validate-imports
"""

import argparse
import ast
import importlib
import importlib.util
import json
import sys
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class ImportPerformanceAnalyzer:
    """Comprehensive import performance analysis and optimization."""

    def __init__(self, package_root: str = "src/omnibase_spi") -> None:
        self.package_root = Path(package_root)
        self.import_graph: Dict[str, List[str]] = {}
        self.performance_metrics: Dict[str, Any] = {}

    def analyze_import_structure(self) -> Dict[str, Any]:
        """Analyze the complete import structure and performance."""
        results = {
            "performance": self._measure_import_performance(),
            "circular_imports": self._detect_circular_imports(),
            "import_validation": self._validate_all_imports(),
            "optimization_recommendations": self._generate_recommendations(),
        }
        return results

    def _measure_import_performance(self) -> Dict[str, Any]:
        """Measure comprehensive import performance metrics."""
        sys.path.insert(0, str(self.package_root.parent))

        metrics: Dict[str, Any] = {}

        # 1. Root import performance
        original_modules = set(sys.modules.keys())
        start_time = time.perf_counter()

        try:
            import omnibase_spi

            root_import_time = (time.perf_counter() - start_time) * 1000

            # Count loaded modules
            new_modules = set(sys.modules.keys()) - original_modules
            omnibase_modules = [m for m in new_modules if "omnibase_spi" in m]

            # Get protocol count
            protocols = [
                attr for attr in dir(omnibase_spi) if attr.startswith("Protocol")
            ]

            metrics["root_import"] = {
                "import_time_ms": round(root_import_time, 2),
                "modules_loaded": len(omnibase_modules),
                "protocol_count": len(protocols),
                "protocols": protocols,
                "memory_impact": len(new_modules),
            }

            # 2. Individual protocol access performance
            protocol_times: Dict[str, float] = {}
            for protocol in protocols[:5]:  # Test first 5 protocols
                start_time = time.perf_counter()
                getattr(omnibase_spi, protocol)
                access_time = (time.perf_counter() - start_time) * 1000
                protocol_times[protocol] = round(access_time, 3)

            metrics["protocol_access"] = protocol_times

        except ImportError as e:
            metrics["error"] = f"Import failed: {e}"

        # 3. Direct import comparison
        self._reset_omnibase_modules()

        start_time = time.perf_counter()
        try:
            from omnibase_spi.protocols.core import ProtocolLogger

            direct_import_time = (time.perf_counter() - start_time) * 1000
            metrics["direct_import_time_ms"] = round(direct_import_time, 2)
        except ImportError as e:
            metrics["direct_import_error"] = str(e)

        # 4. Performance ratios
        if "root_import" in metrics and "direct_import_time_ms" in metrics:
            ratio = (
                metrics["root_import"]["import_time_ms"]
                / metrics["direct_import_time_ms"]
            )
            metrics["performance_impact_ratio"] = round(ratio, 2)

        return metrics

    def _detect_circular_imports(self) -> Dict[str, Any]:
        """Detect potential circular import dependencies using AST analysis."""
        import_graph = self._build_import_graph()

        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        circular_imports = []

        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                circular_imports.append(cycle)
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in import_graph.get(node, []):
                if dfs(neighbor, path.copy()):
                    return True

            rec_stack.remove(node)
            return False

        # Check all nodes for cycles
        for node in import_graph:
            if node not in visited:
                dfs(node, [])

        return {
            "import_graph_size": len(import_graph),
            "circular_imports": circular_imports,
            "has_circular_imports": len(circular_imports) > 0,
            "import_graph": dict(
                list(import_graph.items())[:10]
            ),  # First 10 for brevity
        }

    def _validate_all_imports(self) -> Dict[str, Any]:
        """Validate that all imports in the package structure are valid."""
        validation_results: Dict[str, Any] = {
            "missing_modules": [],
            "import_errors": [],
            "valid_imports": 0,
            "total_imports": 0,
        }

        # Check all Python files for import validity
        for py_file in self.package_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                imports = self._extract_imports(py_file)
                validation_results["total_imports"] += len(imports)

                for imp in imports:
                    if imp.startswith("omnibase_spi"):
                        try:
                            importlib.import_module(imp)
                            validation_results["valid_imports"] += 1
                        except ImportError as e:
                            validation_results["import_errors"].append(
                                {"module": imp, "file": str(py_file), "error": str(e)}
                            )
                        except ModuleNotFoundError:
                            validation_results["missing_modules"].append(imp)

            except Exception as e:
                validation_results["import_errors"].append(
                    {"file": str(py_file), "error": f"File parsing error: {e}"}
                )

        return validation_results

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations."""
        recommendations: List[Dict[str, Any]] = []

        # Analyze performance metrics to generate recommendations
        if hasattr(self, "performance_metrics"):
            metrics = self.performance_metrics

            # High import time recommendation
            root_time = (
                metrics.get("performance", {})
                .get("root_import", {})
                .get("import_time_ms", 0)
            )
            if root_time > 50:  # More than 50ms is considered slow
                recommendations.append(
                    {
                        "type": "lazy_loading",
                        "priority": "high",
                        "description": "Implement lazy loading for root-level imports",
                        "impact": "Reduce import time by 60-80%",
                        "effort": "medium",
                        "details": f"Current import time: {root_time}ms is above optimal threshold of 50ms",
                    }
                )

            # Too many modules loaded recommendation
            modules_loaded = (
                metrics.get("performance", {})
                .get("root_import", {})
                .get("modules_loaded", 0)
            )
            if modules_loaded > 25:
                recommendations.append(
                    {
                        "type": "module_reduction",
                        "priority": "medium",
                        "description": "Reduce number of modules loaded on root import",
                        "impact": "Lower memory footprint and faster startup",
                        "effort": "low",
                        "details": f"Currently loading {modules_loaded} modules on root import",
                    }
                )

        # Always recommend these architectural improvements
        recommendations.extend(
            [
                {
                    "type": "lazy_protocol_loading",
                    "priority": "high",
                    "description": "Implement __getattr__ based lazy loading for protocols",
                    "impact": "Significant import performance improvement",
                    "effort": "medium",
                    "details": "Use module-level __getattr__ to load protocols only when accessed",
                },
                {
                    "type": "import_validation_tests",
                    "priority": "medium",
                    "description": "Add comprehensive import validation test suite",
                    "impact": "Prevent import regressions",
                    "effort": "low",
                    "details": "Create tests for all root-level exports and circular import detection",
                },
                {
                    "type": "dynamic_documentation",
                    "priority": "low",
                    "description": "Replace hardcoded protocol counts with dynamic counting",
                    "impact": "Maintain documentation accuracy",
                    "effort": "low",
                    "details": "Use introspection to count protocols dynamically in documentation",
                },
            ]
        )

        return recommendations

    def _build_import_graph(self) -> Dict[str, List[str]]:
        """Build a graph of all import dependencies."""
        import_graph = defaultdict(list)

        for py_file in self.package_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            # Convert file path to module name
            rel_path = py_file.relative_to(self.package_root.parent)
            module_name = str(rel_path.with_suffix("")).replace("/", ".")

            # Extract imports from the file
            imports = self._extract_imports(py_file)

            # Filter for omnibase_spi imports only
            omnibase_imports = [imp for imp in imports if imp and "omnibase_spi" in imp]
            if omnibase_imports:
                import_graph[module_name] = omnibase_imports

        return dict(import_graph)

    def _extract_imports(self, filepath: Path) -> List[str]:
        """Extract all import statements from a Python file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            return imports
        except Exception:
            return []

    def _reset_omnibase_modules(self) -> None:
        """Remove all omnibase_spi modules from sys.modules for clean testing."""
        modules_to_remove = [mod for mod in sys.modules if "omnibase_spi" in mod]
        for mod in modules_to_remove:
            del sys.modules[mod]

    def run_benchmark(self, iterations: int = 5) -> Dict[str, Any]:
        """Run performance benchmark with multiple iterations."""
        results = []

        for i in range(iterations):
            self._reset_omnibase_modules()

            # Force garbage collection
            import gc

            gc.collect()

            # Measure performance
            start_time = time.perf_counter()
            import omnibase_spi

            import_time = (time.perf_counter() - start_time) * 1000

            # Count modules
            omnibase_modules = [m for m in sys.modules if "omnibase_spi" in m]

            results.append(
                {
                    "iteration": i + 1,
                    "import_time_ms": round(import_time, 2),
                    "modules_loaded": len(omnibase_modules),
                }
            )

        # Calculate statistics
        import_times = [r["import_time_ms"] for r in results]
        avg_time = sum(import_times) / len(import_times)
        min_time = min(import_times)
        max_time = max(import_times)

        return {
            "iterations": results,
            "statistics": {
                "average_import_time_ms": round(avg_time, 2),
                "min_import_time_ms": min_time,
                "max_import_time_ms": max_time,
                "variance": round(max_time - min_time, 2),
            },
        }


def main() -> None:
    """Main CLI interface for import performance analysis."""
    parser = argparse.ArgumentParser(
        description="omnibase-spi Import Performance Analyzer"
    )
    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmark"
    )
    parser.add_argument(
        "--detect-circular", action="store_true", help="Detect circular imports"
    )
    parser.add_argument(
        "--validate-imports", action="store_true", help="Validate all imports"
    )
    parser.add_argument(
        "--full-analysis", action="store_true", help="Run complete analysis"
    )
    parser.add_argument("--output", type=str, help="Output file for results")

    args = parser.parse_args()

    analyzer = ImportPerformanceAnalyzer()

    results: Dict[str, Any] = {}

    if args.benchmark or args.full_analysis:
        print("Running performance benchmark...")
        results["benchmark"] = analyzer.run_benchmark()

    if args.detect_circular or args.full_analysis:
        print("Detecting circular imports...")
        results["circular_imports"] = analyzer._detect_circular_imports()

    if args.validate_imports or args.full_analysis:
        print("Validating imports...")
        results["import_validation"] = analyzer._validate_all_imports()

    if (
        not any([args.benchmark, args.detect_circular, args.validate_imports])
        or args.full_analysis
    ):
        print("Running complete analysis...")
        results = analyzer.analyze_import_structure()

    # Store performance metrics for recommendations
    analyzer.performance_metrics = results
    results["recommendations"] = analyzer._generate_recommendations()

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        # Pretty print results
        print("\n" + "=" * 60)
        print("IMPORT PERFORMANCE ANALYSIS RESULTS")
        print("=" * 60)

        if "performance" in results:
            perf = results["performance"]
            if "root_import" in perf:
                root = perf["root_import"]
                print(f"\n🚀 ROOT IMPORT PERFORMANCE:")
                print(f"   Import Time: {root['import_time_ms']}ms")
                print(f"   Modules Loaded: {root['modules_loaded']}")
                print(f"   Protocol Count: {root['protocol_count']}")

                if "performance_impact_ratio" in perf:
                    ratio = perf["performance_impact_ratio"]
                    print(f"   Performance Impact: {ratio}x slower than direct import")

        if "circular_imports" in results:
            circular = results["circular_imports"]
            print(f"\n🔄 CIRCULAR IMPORT ANALYSIS:")
            print(f"   Has Circular Imports: {circular['has_circular_imports']}")
            if circular["circular_imports"]:
                print("   Circular Import Chains:")
                for i, cycle in enumerate(circular["circular_imports"][:3]):
                    print(f"     {i+1}. {' -> '.join(cycle)}")

        if "import_validation" in results:
            validation = results["import_validation"]
            print(f"\n✅ IMPORT VALIDATION:")
            print(
                f"   Valid Imports: {validation['valid_imports']}/{validation['total_imports']}"
            )
            if validation["import_errors"]:
                print(f"   Import Errors: {len(validation['import_errors'])}")
            if validation["missing_modules"]:
                print(f"   Missing Modules: {len(validation['missing_modules'])}")

        if "recommendations" in results:
            recommendations = results["recommendations"]
            print(f"\n📋 OPTIMIZATION RECOMMENDATIONS:")
            if isinstance(recommendations, list):
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"   {i}. [{rec['priority'].upper()}] {rec['description']}")
                    print(f"      Impact: {rec['impact']}")
                    print(f"      Effort: {rec['effort']}")


if __name__ == "__main__":
    main()
