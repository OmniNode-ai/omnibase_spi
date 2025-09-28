#!/usr/bin/env python3
"""
Analyze SPI protocols to identify property-only protocols that may be causing validation confusion.
"""

import argparse
import ast
from pathlib import Path
from typing import Dict, List


class ProtocolAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze protocol definitions."""

    def __init__(self):
        self.protocols: Dict[str, Dict] = {}
        self.current_protocol = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to identify protocols."""
        # Check if class has @runtime_checkable decorator and inherits from Protocol
        is_protocol = False
        has_runtime_checkable = False

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "runtime_checkable":
                has_runtime_checkable = True

        # Check if inherits from Protocol
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                is_protocol = True
            elif isinstance(base, ast.Attribute) and base.attr == "Protocol":
                is_protocol = True

        if is_protocol and has_runtime_checkable:
            self.current_protocol = node.name
            self.protocols[node.name] = {
                "properties": [],
                "methods": [],
                "async_methods": [],
                "special_methods": [],
                "marker_attributes": [],
                "docstring": ast.get_docstring(node),
                "line_number": node.lineno,
                "inherits_from": [
                    self._get_base_name(base)
                    for base in node.bases
                    if self._get_base_name(base) != "Protocol"
                ],
            }

            # Visit all body elements
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    # Type-annotated attribute (property)
                    if isinstance(item.target, ast.Name):
                        attr_name = item.target.id
                        if (
                            attr_name.startswith("__")
                            and attr_name.endswith("__")
                            and "marker" in attr_name
                        ):
                            self.protocols[node.name]["marker_attributes"].append(
                                attr_name
                            )
                        else:
                            self.protocols[node.name]["properties"].append(attr_name)
                elif isinstance(item, ast.FunctionDef):
                    # Method definition
                    if item.name.startswith("__") and item.name.endswith("__"):
                        self.protocols[node.name]["special_methods"].append(item.name)
                    else:
                        self.protocols[node.name]["methods"].append(item.name)
                elif isinstance(item, ast.AsyncFunctionDef):
                    # Async method definition
                    self.protocols[node.name]["async_methods"].append(item.name)

        self.current_protocol = None
        self.generic_visit(node)

    def _get_base_name(self, base):
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        elif isinstance(base, ast.Constant):
            return str(base.value)
        return str(base)


def analyze_protocol_file(file_path: Path) -> Dict[str, Dict]:
    """Analyze a single protocol file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        analyzer = ProtocolAnalyzer()
        analyzer.visit(tree)

        return analyzer.protocols
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {}


def find_protocol_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the protocols directory."""
    protocol_files = []
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    if protocols_dir.exists():
        for py_file in protocols_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                protocol_files.append(py_file)

    return protocol_files


def categorize_protocols(protocols: Dict[str, Dict]) -> Dict[str, List[str]]:
    """Categorize protocols based on their characteristics."""
    categories = {
        "property_only": [],  # Only properties, no methods
        "marker_interfaces": [],  # Have marker attributes
        "complete_protocols": [],  # Have methods
        "data_models": [],  # Property-only but appear to be data structures
        "incomplete_protocols": [],  # Should have methods but don't
        "method_only": [],  # Only methods, no properties
    }

    for name, info in protocols.items():
        has_properties = bool(info["properties"])
        has_methods = bool(info["methods"] + info["async_methods"])
        has_special_methods = bool(info["special_methods"])
        has_marker_attrs = bool(info["marker_attributes"])
        inherits_from_others = bool(
            [b for b in info["inherits_from"] if b not in ["Protocol", "Generic"]]
        )

        if has_marker_attrs:
            categories["marker_interfaces"].append(name)
        elif has_methods and not has_properties and not has_special_methods:
            categories["method_only"].append(name)
        elif has_methods or has_special_methods:
            categories["complete_protocols"].append(name)
        elif has_properties and not has_methods and not has_special_methods:
            # Determine if this is a legitimate data model or incomplete protocol
            docstring = info["docstring"] or ""

            # Heuristics for data models vs incomplete protocols
            if any(
                keyword in name.lower()
                for keyword in [
                    "metadata",
                    "config",
                    "info",
                    "data",
                    "result",
                    "status",
                    "event",
                    "message",
                ]
            ):
                categories["data_models"].append(name)
            elif any(
                keyword in docstring.lower()
                for keyword in [
                    "service",
                    "manager",
                    "handler",
                    "processor",
                    "controller",
                ]
            ):
                categories["incomplete_protocols"].append(name)
            elif inherits_from_others:
                # If it inherits from other protocols, it might be extending them
                categories["data_models"].append(name)
            else:
                categories["property_only"].append(name)
        else:
            # No properties or methods
            categories["incomplete_protocols"].append(name)

    return categories


def main():
    """Main analysis function."""
    parser = argparse.ArgumentParser(
        description="Analyze SPI protocols to identify property-only protocols"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory of the omnibase-spi project (defaults to current directory)",
    )

    args = parser.parse_args()
    root_dir = Path(args.root_dir).resolve()

    if not root_dir.exists():
        print(f"Error: Directory {root_dir} does not exist")
        return 1

    protocol_files = find_protocol_files(root_dir)

    if not protocol_files:
        protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"
        print(f"Error: No protocol files found in {protocols_dir}")
        print("Make sure you're running from the correct directory")
        return 1

    print(f"Found {len(protocol_files)} protocol files")
    print("=" * 80)

    all_protocols = {}
    file_protocol_counts = {}

    for file_path in protocol_files:
        protocols = analyze_protocol_file(file_path)
        if protocols:
            rel_path = file_path.relative_to(root_dir)
            file_protocol_counts[str(rel_path)] = len(protocols)
            all_protocols.update(protocols)
            print(f"{rel_path}: {len(protocols)} protocols")

    print(f"\nTotal protocols found: {len(all_protocols)}")
    print("=" * 80)

    # Categorize protocols
    categories = categorize_protocols(all_protocols)

    print("\nPROTOCOL CATEGORIZATION:")
    print("=" * 80)

    for category, protocol_list in categories.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(protocol_list)}):")
        for protocol in sorted(protocol_list):
            info = all_protocols[protocol]
            props = len(info["properties"])
            methods = len(info["methods"] + info["async_methods"])
            special = len(info["special_methods"])
            markers = len(info["marker_attributes"])
            inherits = (
                ", ".join(info["inherits_from"]) if info["inherits_from"] else "None"
            )

            print(f"  {protocol}")
            print(
                f"    Properties: {props}, Methods: {methods}, Special: {special}, Markers: {markers}"
            )
            print(f"    Inherits: {inherits}")
            if info["docstring"]:
                doc_summary = info["docstring"].split(".")[0][:100]
                print(f"    Doc: {doc_summary}...")

    # Focus on problematic protocols
    problematic = categories["property_only"] + categories["incomplete_protocols"]
    print(f"\nPROBLEMATIC PROTOCOLS REQUIRING ATTENTION ({len(problematic)}):")
    print("=" * 80)

    for protocol in sorted(problematic):
        info = all_protocols[protocol]
        print(f"\n{protocol}:")
        print(f"  File line: {info['line_number']}")
        print(f"  Properties: {info['properties']}")
        print(f"  Inherits from: {info['inherits_from']}")
        if info["docstring"]:
            print(f"  Purpose: {info['docstring'].split('.')[0]}")

    # Summary statistics
    print("\nSUMMARY STATISTICS:")
    print("=" * 80)
    print(f"Total protocols: {len(all_protocols)}")
    print(f"Complete protocols (have methods): {len(categories['complete_protocols'])}")
    print(
        f"Data model protocols (properties only, legitimate): {len(categories['data_models'])}"
    )
    print(f"Marker interfaces: {len(categories['marker_interfaces'])}")
    print(
        f"Property-only protocols (may need methods): {len(categories['property_only'])}"
    )
    print(
        f"Incomplete protocols (definitely need methods): {len(categories['incomplete_protocols'])}"
    )
    print(f"Method-only protocols: {len(categories['method_only'])}")

    # The 177 protocols mentioned in the issue
    property_only_count = (
        len(categories["property_only"])
        + len(categories["data_models"])
        + len(categories["incomplete_protocols"])
    )
    print(f"\nTotal protocols with no methods: {property_only_count}")

    if property_only_count >= 177:
        print("✓ Found the source of the validation confusion!")
    else:
        print(f"? Expected ~177 protocols with no methods, found {property_only_count}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
