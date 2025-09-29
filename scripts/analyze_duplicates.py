#!/usr/bin/env python3
"""
Analyze protocol duplicates in the omnibase_spi codebase.
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List


class ProtocolAnalyzer:
    def __init__(self, src_dir: str):
        self.src_dir = Path(src_dir)
        self.protocols: Dict[str, List[Dict[str, Any]]] = {}  # name -> [file_info, ...]
        self.empty_protocols: List[Dict[str, Any]] = []
        self.protocol_signatures: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(
            list
        )  # signature -> [protocol_info, ...]

    def analyze(self) -> None:
        """Analyze all Python files in the source directory."""
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name.startswith("."):
                continue
            self.analyze_file(py_file)

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for protocol definitions."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self.is_protocol_class(node):
                        protocol_info = self.extract_protocol_info(node, file_path)
                        self.protocols.setdefault(protocol_info["name"], []).append(
                            protocol_info
                        )

                        # Generate signature for duplicate detection
                        signature = self.generate_signature(protocol_info)
                        self.protocol_signatures[signature].append(protocol_info)

                        if protocol_info["is_empty"]:
                            self.empty_protocols.append(protocol_info)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a Protocol class."""
        # Check if it inherits from Protocol
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            elif isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def extract_protocol_info(
        self, node: ast.ClassDef, file_path: Path
    ) -> Dict[str, Any]:
        """Extract information about a protocol class."""
        # Count methods and properties
        methods = []
        properties = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith("__") and item.name.endswith("__"):
                    continue  # Skip magic methods for signature
                methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                properties.append(item.target.id)

        # Check if has @runtime_checkable decorator
        has_runtime_checkable = any(
            isinstance(d, ast.Name) and d.id == "runtime_checkable"
            for d in node.decorator_list
        )

        # Get docstring
        docstring = ""
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value

        is_empty = len(methods) == 0 and len(properties) == 0

        return {
            "name": node.name,
            "file_path": str(file_path),
            "methods": methods,
            "properties": properties,
            "has_runtime_checkable": has_runtime_checkable,
            "docstring": docstring.strip(),
            "is_empty": is_empty,
            "line_number": node.lineno,
            "method_count": len(methods),
            "property_count": len(properties),
        }

    def generate_signature(self, protocol_info: Dict[str, Any]) -> str:
        """Generate a signature for duplicate detection."""
        # Simple signature based on sorted method and property names
        methods = sorted(protocol_info["methods"])
        properties = sorted(protocol_info["properties"])
        return f"methods:{','.join(methods)}|properties:{','.join(properties)}"

    def find_exact_duplicates(self) -> List[List[Dict[str, Any]]]:
        """Find protocols with identical signatures."""
        duplicates = []
        for signature, protocols in self.protocol_signatures.items():
            if len(protocols) > 1:
                duplicates.append(protocols)
        return duplicates

    def find_name_conflicts(self) -> List[List[Dict[str, Any]]]:
        """Find protocols with same name but different signatures."""
        conflicts = []
        for name, protocols in self.protocols.items():
            if len(protocols) > 1:
                # Check if they have different signatures
                signatures = set(self.generate_signature(p) for p in protocols)
                if len(signatures) > 1:
                    conflicts.append(protocols)
        return conflicts

    def print_analysis(self) -> None:
        """Print analysis results."""
        print("=== PROTOCOL ANALYSIS RESULTS ===")
        print(f"Total protocols found: {sum(len(p) for p in self.protocols.values())}")
        print(f"Unique protocol names: {len(self.protocols)}")
        print(f"Empty protocols (no methods/properties): {len(self.empty_protocols)}")

        # Find exact duplicates
        exact_duplicates = self.find_exact_duplicates()
        print(f"\n=== EXACT DUPLICATES ({len(exact_duplicates)} groups) ===")
        for i, group in enumerate(exact_duplicates):
            print(f"\nGroup {i+1}: {len(group)} protocols with identical signatures")
            for protocol in group:
                print(
                    f"  - {protocol['name']} in {protocol['file_path']}:{protocol['line_number']}"
                )
                print(f"    Methods: {protocol['methods']}")
                print(f"    Properties: {protocol['properties']}")
                print(f"    Empty: {protocol['is_empty']}")

        # Find name conflicts
        name_conflicts = self.find_name_conflicts()
        print(f"\n=== NAME CONFLICTS ({len(name_conflicts)} groups) ===")
        for i, group in enumerate(name_conflicts):
            print(
                f"\nGroup {i+1}: {group[0]['name']} - {len(group)} different definitions"
            )
            for protocol in group:
                print(f"  - {protocol['file_path']}:{protocol['line_number']}")
                print(f"    Methods: {protocol['methods']}")
                print(f"    Properties: {protocol['properties']}")

        # Empty protocols analysis
        print("\n=== EMPTY PROTOCOLS ===")
        empty_by_file = defaultdict(list)
        for protocol in self.empty_protocols:
            empty_by_file[protocol["file_path"]].append(protocol["name"])

        for file_path, protocol_names in empty_by_file.items():
            print(f"{file_path}: {len(protocol_names)} empty protocols")
            for name in protocol_names[:5]:  # Show first 5
                print(f"  - {name}")
            if len(protocol_names) > 5:
                print(f"  ... and {len(protocol_names) - 5} more")


def main() -> None:
    analyzer = ProtocolAnalyzer("src")
    analyzer.analyze()
    analyzer.print_analysis()


if __name__ == "__main__":
    main()
