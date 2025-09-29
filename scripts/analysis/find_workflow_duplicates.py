#!/usr/bin/env python3
"""
Script to find duplicate protocols specifically in the workflow_orchestration domain.
"""

import ast
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_protocol_signature(node: ast.ClassDef) -> str:
    """Extract a signature string from a protocol class definition."""
    signature_parts = []

    # Add class name
    signature_parts.append(f"class:{node.name}")

    # Extract base classes
    bases = [
        ast.unparse(base) for base in node.bases if ast.unparse(base) != "Protocol"
    ]
    if bases:
        signature_parts.append(f"bases:{','.join(sorted(bases))}")

    # Extract properties and methods
    properties = []
    methods = []
    async_methods = []

    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            # Property annotation
            prop_type = ast.unparse(item.annotation) if item.annotation else "Any"
            properties.append(f"{item.target.id}:{prop_type}")
        elif isinstance(item, ast.FunctionDef):
            # Method definition
            args = []
            for arg in item.args.args[1:]:  # Skip 'self'
                arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
                args.append(f"{arg.arg}:{arg_type}")

            return_type = ast.unparse(item.returns) if item.returns else "Any"
            method_sig = f"{item.name}({','.join(args)})->{return_type}"

            if item.name.startswith("__") and item.name.endswith("__"):
                continue  # Skip special methods for signature comparison

            methods.append(method_sig)
        elif isinstance(item, ast.AsyncFunctionDef):
            # Async method definition
            args = []
            for arg in item.args.args[1:]:  # Skip 'self'
                arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
                args.append(f"{arg.arg}:{arg_type}")

            return_type = ast.unparse(item.returns) if item.returns else "Any"
            method_sig = f"async {item.name}({','.join(args)})->{return_type}"
            async_methods.append(method_sig)

    if properties:
        signature_parts.append(f"props:{','.join(sorted(properties))}")
    if methods:
        signature_parts.append(f"methods:{','.join(sorted(methods))}")
    if async_methods:
        signature_parts.append(f"async_methods:{','.join(sorted(async_methods))}")

    return "|".join(signature_parts)


def analyze_workflow_protocols():
    """Analyze all workflow-related protocol files for duplicates."""

    # Find all workflow-related protocol files
    spi_root = Path("src/omnibase_spi/protocols")
    workflow_files = []

    # Check workflow_orchestration directory
    workflow_dir = spi_root / "workflow_orchestration"
    if workflow_dir.exists():
        workflow_files.extend(list(workflow_dir.glob("protocol_*.py")))

    # Check core directory for workflow-related protocols
    core_dir = spi_root / "core"
    if core_dir.exists():
        for f in core_dir.glob("protocol_*.py"):
            if "workflow" in f.name.lower():
                workflow_files.append(f)

    # Check types directory for workflow types
    types_dir = spi_root / "types"
    if types_dir.exists():
        for f in types_dir.glob("protocol_*.py"):
            if "workflow" in f.name.lower():
                workflow_files.append(f)

    print(f"Found {len(workflow_files)} workflow-related protocol files:")
    for f in workflow_files:
        print(f"  - {f}")
    print()

    # Extract protocols from each file
    all_protocols = {}  # signature_hash -> [(file_path, protocol_name, signature)]
    protocol_details = {}  # (file_path, protocol_name) -> signature

    for file_path in workflow_files:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a protocol class
                    bases = [ast.unparse(base) for base in node.bases]
                    if "Protocol" in bases or any("Protocol" in base for base in bases):
                        signature = extract_protocol_signature(node)
                        signature_hash = hashlib.sha256(signature.encode()).hexdigest()[
                            :16
                        ]

                        if signature_hash not in all_protocols:
                            all_protocols[signature_hash] = []

                        all_protocols[signature_hash].append(
                            (file_path, node.name, signature)
                        )
                        protocol_details[(file_path, node.name)] = signature

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    print(f"Found {len(protocol_details)} protocols total")
    print()

    # Find duplicates
    duplicates = {}
    for signature_hash, protocols in all_protocols.items():
        if len(protocols) > 1:
            duplicates[signature_hash] = protocols

    if not duplicates:
        print("✅ No duplicate protocols found in workflow orchestration domain!")
        return

    print(f"🚨 Found {len(duplicates)} sets of duplicate protocols:")
    print()

    for i, (signature_hash, protocols) in enumerate(duplicates.items(), 1):
        print(f"Duplicate Set #{i} (signature hash: {signature_hash}):")
        print(f"  Protocols with identical signatures:")

        for file_path, protocol_name, signature in protocols:
            rel_path = file_path.relative_to(Path.cwd())
            print(f"    - {protocol_name} in {rel_path}")

        print(f"  Signature: {protocols[0][2]}")
        print()

    # Provide recommendations
    print("🔧 Recommendations:")
    for signature_hash, protocols in duplicates.items():
        print(f"\nDuplicate set with {len(protocols)} protocols:")
        canonical_file, canonical_name = protocols[0][0], protocols[0][1]
        rel_canonical = canonical_file.relative_to(Path.cwd())

        print(f"  Keep: {canonical_name} in {rel_canonical}")
        print(f"  Remove:")
        for file_path, protocol_name, _ in protocols[1:]:
            rel_path = file_path.relative_to(Path.cwd())
            print(f"    - {protocol_name} in {rel_path}")

    return duplicates


if __name__ == "__main__":
    print("🔍 Analyzing workflow orchestration protocols for duplicates...")
    print("=" * 60)

    duplicates = analyze_workflow_protocols()

    if duplicates:
        print(f"\n📊 Summary: {len(duplicates)} duplicate sets found")
        total_duplicates = sum(len(protocols) - 1 for protocols in duplicates.values())
        print(f"📊 Total protocols to remove: {total_duplicates}")
    else:
        print("✅ No duplicates found - workflow orchestration domain is clean!")
