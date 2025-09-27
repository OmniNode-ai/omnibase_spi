#!/usr/bin/env python3
"""
Protocol Inheritance Analysis Tool

Analyzes protocol inheritance patterns to identify issues:
1. Circular inheritance
2. Complex multiple inheritance
3. Missing base protocols for similar signatures
4. Inconsistent Protocol usage
"""

import ast
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ProtocolInheritanceAnalyzer(ast.NodeVisitor):
    """Analyze protocol inheritance patterns in Python files."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.protocols: Dict[str, Dict] = {}
        self.inheritance_map: Dict[str, List[str]] = {}
        self.imports: Set[str] = set()
        self.runtime_checkable_protocols: Set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to identify protocols."""
        # Check if it's a protocol
        is_protocol = False
        base_protocols = []

        for base in node.bases:
            base_name = self._get_name(base)
            if base_name == "Protocol":
                is_protocol = True
            elif base_name and base_name in self.protocols:
                base_protocols.append(base_name)

        # Check for Protocol in bases or if inheriting from another protocol
        if is_protocol or base_protocols:
            # Extract method signatures
            methods = []
            properties = []

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name.startswith("__") and item.name.endswith("__"):
                        continue  # Skip magic methods

                    method_sig = self._get_method_signature(item)
                    methods.append(method_sig)
                elif isinstance(item, ast.AnnAssign) and item.target:
                    prop_name = self._get_name(item.target)
                    if prop_name:
                        properties.append(prop_name)

            # Check for @runtime_checkable decorator
            has_runtime_checkable = any(
                self._get_name(decorator) == "runtime_checkable"
                for decorator in node.decorator_list
            )

            if has_runtime_checkable:
                self.runtime_checkable_protocols.add(node.name)

            self.protocols[node.name] = {
                "methods": methods,
                "properties": properties,
                "bases": base_protocols,
                "is_protocol": is_protocol,
                "has_runtime_checkable": has_runtime_checkable,
                "line": node.lineno,
            }

            if base_protocols:
                self.inheritance_map[node.name] = base_protocols

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports for context."""
        if node.module:
            for alias in node.names:
                imported_name = alias.asname if alias.asname else alias.name
                self.imports.add(f"{node.module}.{imported_name}")
        self.generic_visit(node)

    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return ""

    def _get_method_signature(self, func_node: ast.FunctionDef) -> str:
        """Extract method signature for comparison."""
        args = []
        for arg in func_node.args.args:
            args.append(arg.arg)

        # Check if async
        is_async = isinstance(func_node, ast.AsyncFunctionDef)
        async_prefix = "async " if is_async else ""

        return f"{async_prefix}{func_node.name}({', '.join(args)})"


def analyze_inheritance_patterns(src_dir: Path) -> Dict:
    """Analyze inheritance patterns across all protocol files."""

    all_protocols = {}
    inheritance_graph = defaultdict(list)
    signature_groups = defaultdict(list)

    # Find all Python files in protocols directory
    protocol_files = list(src_dir.rglob("protocol_*.py"))

    print(f"🔍 Analyzing {len(protocol_files)} protocol files...")

    for file_path in protocol_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            analyzer = ProtocolInheritanceAnalyzer(str(file_path))
            analyzer.visit(tree)

            # Store results
            for protocol_name, info in analyzer.protocols.items():
                qualified_name = f"{file_path.stem}.{protocol_name}"
                all_protocols[qualified_name] = {
                    **info,
                    "file": str(file_path),
                    "module": file_path.stem,
                }

                # Build inheritance graph
                for base in info["bases"]:
                    inheritance_graph[qualified_name].append(f"{file_path.stem}.{base}")

                # Group by signature for duplicate detection
                method_sig = tuple(sorted(info["methods"]))
                prop_sig = tuple(sorted(info["properties"]))
                signature = (method_sig, prop_sig)
                signature_groups[signature].append(qualified_name)

        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")

    return {
        "protocols": all_protocols,
        "inheritance_graph": dict(inheritance_graph),
        "signature_groups": dict(signature_groups),
        "total_files": len(protocol_files),
    }


def detect_inheritance_issues(analysis_results: Dict) -> Dict:
    """Detect various inheritance pattern issues."""

    protocols = analysis_results["protocols"]
    inheritance_graph = analysis_results["inheritance_graph"]
    signature_groups = analysis_results["signature_groups"]

    issues = {
        "circular_inheritance": [],
        "complex_multiple_inheritance": [],
        "missing_runtime_checkable": [],
        "similar_signature_groups": [],
        "empty_protocols": [],
        "inheritance_depth_issues": [],
    }

    # 1. Detect circular inheritance
    def has_circular_dependency(
        node: str, visited: Set[str], rec_stack: Set[str]
    ) -> bool:
        visited.add(node)
        rec_stack.add(node)

        for neighbor in inheritance_graph.get(node, []):
            if neighbor not in visited:
                if has_circular_dependency(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.discard(node)
        return False

    visited = set()
    for protocol in protocols:
        if protocol not in visited:
            if has_circular_dependency(protocol, visited, set()):
                issues["circular_inheritance"].append(protocol)

    # 2. Detect complex multiple inheritance
    for protocol, info in protocols.items():
        if len(info["bases"]) > 2:  # More than 2 base protocols
            issues["complex_multiple_inheritance"].append(
                {
                    "protocol": protocol,
                    "bases": info["bases"],
                    "count": len(info["bases"]),
                }
            )

    # 3. Find protocols missing @runtime_checkable
    for protocol, info in protocols.items():
        if not info["has_runtime_checkable"]:
            issues["missing_runtime_checkable"].append(protocol)

    # 4. Find similar signature groups (potential base protocol opportunities)
    for signature, protocol_list in signature_groups.items():
        if len(protocol_list) > 3:  # 3+ protocols with same signature
            method_sig, prop_sig = signature
            if method_sig or prop_sig:  # Not empty protocols
                issues["similar_signature_groups"].append(
                    {
                        "signature": {"methods": method_sig, "properties": prop_sig},
                        "protocols": protocol_list,
                        "count": len(protocol_list),
                    }
                )

    # 5. Find empty protocols (no methods or properties)
    for protocol, info in protocols.items():
        if not info["methods"] and not info["properties"]:
            issues["empty_protocols"].append(protocol)

    # 6. Find deep inheritance chains
    def get_inheritance_depth(protocol: str, visited: Set[str] = None) -> int:
        if visited is None:
            visited = set()

        if protocol in visited:
            return 0  # Circular reference

        visited.add(protocol)
        bases = inheritance_graph.get(protocol, [])

        if not bases:
            return 1

        max_depth = 0
        for base in bases:
            depth = get_inheritance_depth(base, visited.copy())
            max_depth = max(max_depth, depth)

        return max_depth + 1

    for protocol in protocols:
        depth = get_inheritance_depth(protocol)
        if depth > 4:  # More than 4 levels deep
            issues["inheritance_depth_issues"].append(
                {"protocol": protocol, "depth": depth}
            )

    return issues


def print_inheritance_analysis(analysis_results: Dict, issues: Dict) -> None:
    """Print detailed inheritance analysis results."""

    protocols = analysis_results["protocols"]

    print("\n" + "=" * 80)
    print("🔍 PROTOCOL INHERITANCE ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\n📊 SUMMARY:")
    print(f"   Total protocols analyzed: {len(protocols)}")
    print(f"   Total protocol files: {analysis_results['total_files']}")

    # Runtime checkable status
    runtime_checkable_count = sum(
        1 for p in protocols.values() if p["has_runtime_checkable"]
    )
    print(
        f"   Protocols with @runtime_checkable: {runtime_checkable_count}/{len(protocols)}"
    )

    print(f"\n🚨 INHERITANCE ISSUES FOUND:")

    # Circular inheritance
    if issues["circular_inheritance"]:
        print(
            f"\n   ❌ CIRCULAR INHERITANCE ({len(issues['circular_inheritance'])} protocols):"
        )
        for protocol in issues["circular_inheritance"]:
            print(f"      • {protocol}")

    # Complex multiple inheritance
    if issues["complex_multiple_inheritance"]:
        print(
            f"\n   ⚠️  COMPLEX MULTIPLE INHERITANCE ({len(issues['complex_multiple_inheritance'])} protocols):"
        )
        for item in issues["complex_multiple_inheritance"]:
            print(
                f"      • {item['protocol']} inherits from {item['count']} protocols: {item['bases']}"
            )

    # Missing runtime_checkable
    if issues["missing_runtime_checkable"]:
        print(
            f"\n   📝 MISSING @runtime_checkable ({len(issues['missing_runtime_checkable'])} protocols):"
        )
        for protocol in issues["missing_runtime_checkable"][:10]:  # Show first 10
            print(f"      • {protocol}")
        if len(issues["missing_runtime_checkable"]) > 10:
            print(f"      ... and {len(issues['missing_runtime_checkable']) - 10} more")

    # Similar signature groups
    if issues["similar_signature_groups"]:
        print(
            f"\n   🔄 SIMILAR SIGNATURE GROUPS ({len(issues['similar_signature_groups'])} groups):"
        )
        for group in issues["similar_signature_groups"]:
            print(f"      📋 Group with {group['count']} protocols:")
            print(f"         Methods: {list(group['signature']['methods'])}")
            print(f"         Properties: {list(group['signature']['properties'])}")
            for protocol in group["protocols"][:5]:  # Show first 5
                print(f"         • {protocol}")
            if len(group["protocols"]) > 5:
                print(f"         ... and {len(group['protocols']) - 5} more")
            print()

    # Empty protocols
    if issues["empty_protocols"]:
        print(f"\n   🗂️  EMPTY PROTOCOLS ({len(issues['empty_protocols'])} protocols):")
        for protocol in issues["empty_protocols"][:10]:  # Show first 10
            print(f"      • {protocol}")
        if len(issues["empty_protocols"]) > 10:
            print(f"      ... and {len(issues['empty_protocols']) - 10} more")

    # Deep inheritance
    if issues["inheritance_depth_issues"]:
        print(
            f"\n   📏 DEEP INHERITANCE CHAINS ({len(issues['inheritance_depth_issues'])} protocols):"
        )
        for item in issues["inheritance_depth_issues"]:
            print(f"      • {item['protocol']} (depth: {item['depth']})")

    print(f"\n💡 RECOMMENDATIONS:")

    if issues["circular_inheritance"]:
        print(f"   🔧 Fix circular inheritance by restructuring protocol relationships")

    if issues["complex_multiple_inheritance"]:
        print(
            f"   🔧 Simplify multiple inheritance using composition or mixin patterns"
        )

    if issues["similar_signature_groups"]:
        print(
            f"   🔧 Create base protocols for similar signature groups to reduce duplication"
        )

    if issues["empty_protocols"]:
        print(f"   🔧 Add methods to empty protocols or convert to TypedDict/dataclass")

    if len(issues["missing_runtime_checkable"]) > 0:
        print(
            f"   🔧 Add @runtime_checkable decorator to {len(issues['missing_runtime_checkable'])} protocols"
        )


def main():
    """Main analysis function."""

    if len(sys.argv) > 1:
        src_dir = Path(sys.argv[1])
    else:
        src_dir = Path("src/omnibase_spi/protocols")

    if not src_dir.exists():
        print(f"❌ Directory not found: {src_dir}")
        sys.exit(1)

    print(f"🔍 Analyzing protocol inheritance patterns in: {src_dir}")

    # Analyze inheritance patterns
    analysis_results = analyze_inheritance_patterns(src_dir)

    # Detect issues
    issues = detect_inheritance_issues(analysis_results)

    # Print results
    print_inheritance_analysis(analysis_results, issues)

    # Return exit code based on issues found
    total_issues = sum(
        len(issue_list)
        for issue_list in issues.values()
        if isinstance(issue_list, list)
    )

    if total_issues > 0:
        print(f"\n🚨 ANALYSIS FAILED: {total_issues} issues found")
        sys.exit(1)
    else:
        print(f"\n✅ ANALYSIS PASSED: No critical inheritance issues found")


if __name__ == "__main__":
    main()
