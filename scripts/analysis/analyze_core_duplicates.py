#!/usr/bin/env python3
"""
Core Domain Duplicate Protocol Analysis Script
Agent 3 - Focus on core domain duplicates only
"""

import ast
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class CoreDuplicateAnalyzer:
    def __init__(self):
        self.core_protocols: Dict[str, Dict] = {}
        self.protocol_signatures: Dict[str, str] = {}
        self.duplicates: Dict[str, List[str]] = defaultdict(list)

    def extract_protocol_signature(self, file_path: str) -> List[Dict]:
        """Extract protocol signatures from a Python file"""
        protocols = []
        try:
            with open(file_path, "r") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this is a protocol class
                    is_protocol = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Protocol":
                            is_protocol = True
                            break

                    if is_protocol:
                        # Extract method signatures, properties, and class-level attributes
                        methods = []
                        properties = []
                        attributes = []

                        for item in node.body:
                            if isinstance(
                                item, (ast.FunctionDef, ast.AsyncFunctionDef)
                            ):
                                # Get method signature with parameters and return type
                                args = []
                                for arg in item.args.args:
                                    if arg.arg != "self":
                                        arg_str = arg.arg
                                        if arg.annotation:
                                            arg_str += (
                                                f": {ast.unparse(arg.annotation)}"
                                            )
                                        args.append(arg_str)

                                # Add return type if present
                                return_type = ""
                                if item.returns:
                                    return_type = f" -> {ast.unparse(item.returns)}"

                                # Mark async methods
                                async_prefix = (
                                    "async "
                                    if isinstance(item, ast.AsyncFunctionDef)
                                    else ""
                                )
                                method_sig = f"{async_prefix}{item.name}({', '.join(args)}){return_type}"

                                if any(
                                    isinstance(decorator, ast.Name)
                                    and decorator.id == "property"
                                    for decorator in item.decorator_list
                                ):
                                    properties.append(method_sig)
                                else:
                                    methods.append(method_sig)

                            elif isinstance(item, ast.AnnAssign) and isinstance(
                                item.target, ast.Name
                            ):
                                # Class-level attribute annotations (e.g., status_code: int)
                                attr_name = item.target.id
                                attr_type = (
                                    ast.unparse(item.annotation)
                                    if item.annotation
                                    else "Any"
                                )
                                attributes.append(f"{attr_name}: {attr_type}")

                        # Create a comprehensive signature hash
                        combined_sig = f"methods:{sorted(methods)},properties:{sorted(properties)},attributes:{sorted(attributes)}"
                        sig_hash = hashlib.md5(combined_sig.encode()).hexdigest()

                        protocols.append(
                            {
                                "name": node.name,
                                "methods": sorted(methods),
                                "properties": sorted(properties),
                                "attributes": sorted(attributes),
                                "signature_hash": sig_hash,
                                "file_path": file_path,
                                "combined_signature": combined_sig,
                            }
                        )

        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")

        return protocols

    def analyze_core_domain(self):
        """Analyze all protocols in the core domain"""
        core_path = Path("src/omnibase_spi/protocols/core")

        print("🔍 Analyzing core domain protocols...")

        for py_file in core_path.glob("protocol_*.py"):
            protocols = self.extract_protocol_signature(str(py_file))

            for protocol in protocols:
                protocol_name = protocol["name"]
                signature_hash = protocol["signature_hash"]

                # Store protocol info
                self.core_protocols[protocol_name] = protocol

                # Track signatures for duplicate detection
                if signature_hash in self.protocol_signatures:
                    # Found a duplicate signature
                    existing_protocol = self.protocol_signatures[signature_hash]
                    self.duplicates[signature_hash].append(protocol_name)
                    if existing_protocol not in self.duplicates[signature_hash]:
                        self.duplicates[signature_hash].append(existing_protocol)
                else:
                    self.protocol_signatures[signature_hash] = protocol_name

    def report_duplicates(self):
        """Generate a detailed duplicate report for core domain"""
        print("\n" + "=" * 80)
        print("🎯 CORE DOMAIN DUPLICATE PROTOCOL ANALYSIS")
        print("=" * 80)

        if not self.duplicates:
            print("✅ No duplicate protocols found in core domain!")
            return

        print(
            f"❌ Found {len(self.duplicates)} groups of duplicate protocol signatures"
        )
        print(
            f"📊 Total duplicate protocols: {sum(len(group) for group in self.duplicates.values())}"
        )

        for idx, (sig_hash, duplicate_group) in enumerate(self.duplicates.items(), 1):
            print(f"\n📁 Duplicate Group #{idx} (signature hash: {sig_hash[:8]}...)")
            print(f"   Protocols with identical signatures: {len(duplicate_group)}")

            # Show details for each protocol in this duplicate group
            for protocol_name in duplicate_group:
                if protocol_name in self.core_protocols:
                    protocol_info = self.core_protocols[protocol_name]
                    print(f"   • {protocol_name}")
                    print(f"     File: {protocol_info['file_path']}")
                    print(
                        f"     Methods ({len(protocol_info['methods'])}): {protocol_info['methods'][:3]}{'...' if len(protocol_info['methods']) > 3 else ''}"
                    )
                    print(
                        f"     Properties ({len(protocol_info['properties'])}): {protocol_info['properties']}"
                    )
                    print(
                        f"     Attributes ({len(protocol_info['attributes'])}): {protocol_info['attributes']}"
                    )

            # Recommend which to keep
            if len(duplicate_group) > 1:
                # Keep the one with the most comprehensive definition (most methods + properties + attributes)
                recommended = max(
                    duplicate_group,
                    key=lambda name: (
                        len(self.core_protocols.get(name, {}).get("methods", []))
                        + len(self.core_protocols.get(name, {}).get("properties", []))
                        + len(self.core_protocols.get(name, {}).get("attributes", [])),
                        len(name),  # Longer names often more descriptive
                    ),
                )
                print(f"   💡 RECOMMENDATION: Keep '{recommended}', remove others")

        print("\n" + "=" * 80)

        return self.duplicates

    def generate_fix_plan(self):
        """Generate specific fix plan for core domain duplicates"""
        if not self.duplicates:
            print("✅ No fixes needed - no duplicates found!")
            return

        print("\n🛠️ CORE DOMAIN DUPLICATE FIX PLAN")
        print("=" * 50)

        for idx, (sig_hash, duplicate_group) in enumerate(self.duplicates.items(), 1):
            print(f"\nGroup #{idx}: {len(duplicate_group)} duplicates")

            # Determine which protocol to keep (most comprehensive definition)
            recommended_keep = max(
                duplicate_group,
                key=lambda name: (
                    len(self.core_protocols.get(name, {}).get("methods", []))
                    + len(self.core_protocols.get(name, {}).get("properties", []))
                    + len(self.core_protocols.get(name, {}).get("attributes", [])),
                    len(name),
                ),
            )

            to_remove = [p for p in duplicate_group if p != recommended_keep]

            print(f"   ✅ KEEP: {recommended_keep}")
            print(f"   ❌ REMOVE: {to_remove}")

            # Show files that need to be removed
            for protocol_name in to_remove:
                if protocol_name in self.core_protocols:
                    file_path = self.core_protocols[protocol_name]["file_path"]
                    print(f"      📁 Delete from: {file_path}")

        return self.duplicates


if __name__ == "__main__":
    analyzer = CoreDuplicateAnalyzer()
    analyzer.analyze_core_domain()
    duplicates = analyzer.report_duplicates()
    analyzer.generate_fix_plan()

    # Summary
    if duplicates:
        total_duplicates = sum(len(group) for group in duplicates.values())
        total_groups = len(duplicates)
        print(f"\n📊 SUMMARY:")
        print(f"   Duplicate groups: {total_groups}")
        print(f"   Total duplicate protocols: {total_duplicates}")
        print(f"   Files to be modified: {total_duplicates - total_groups}")
    else:
        print(f"\n✅ CORE DOMAIN CLEAN: No duplicates found!")
