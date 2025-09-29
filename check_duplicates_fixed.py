#!/usr/bin/env python3
"""Check for duplicate protocol definitions - fixed version."""

import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


def get_protocol_signature(node: ast.ClassDef) -> str:
    """Get a normalized signature for a protocol class."""
    methods = []
    properties = []

    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            # Get method signature
            args = []
            for arg in item.args.args[1:]:  # Skip 'self'
                arg_type = ""
                if arg.annotation:
                    arg_type = ast.unparse(arg.annotation)
                args.append(f"{arg.arg}: {arg_type}")

            return_type = ""
            if item.returns:
                return_type = ast.unparse(item.returns)

            sig = f"{item.name}({', '.join(args)}) -> {return_type}"

            # Check if it's a property or async property
            has_property_decorator = False
            is_async = item.is_async

            for decorator in item.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "property":
                    has_property_decorator = True
                    break

            if has_property_decorator:
                properties.append(sig)
            else:
                if is_async:
                    methods.append(f"async {sig}")
                else:
                    methods.append(sig)

        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            # Get property annotation
            prop_type = ""
            if item.annotation:
                prop_type = ast.unparse(item.annotation)
            properties.append(f"{item.target.id}: {prop_type}")

    # Sort for consistent comparison
    methods.sort()
    properties.sort()

    # Create a normalized signature string
    signature = f"properties:{json.dumps(properties)};methods:{json.dumps(methods)}"
    return signature


def find_duplicate_protocols(directory: Path) -> Dict[str, List[Tuple[str, str]]]:
    """Find protocols with identical signatures."""
    protocol_signatures: Dict[str, List[Tuple[str, str]]] = {}
    empty_protocols = []

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a Protocol
                    is_protocol = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Protocol":
                            is_protocol = True
                            break

                    if is_protocol:
                        signature = get_protocol_signature(node)

                        # Check if protocol is empty
                        if signature == 'properties:[];methods:[]':
                            empty_protocols.append((
                                str(py_file.relative_to(directory)),
                                node.name
                            ))
                            continue  # Skip empty protocols for now

                        sig_hash = hashlib.md5(signature.encode()).hexdigest()

                        if sig_hash not in protocol_signatures:
                            protocol_signatures[sig_hash] = []

                        protocol_signatures[sig_hash].append((
                            str(py_file.relative_to(directory)),
                            node.name
                        ))

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    # Filter to only duplicates
    duplicates = {
        sig_hash: protocols
        for sig_hash, protocols in protocol_signatures.items()
        if len(protocols) > 1
    }

    if empty_protocols:
        print(f"\nFound {len(empty_protocols)} empty protocols (skipped from duplicate analysis):")
        for file_path, protocol_name in empty_protocols[:10]:  # Show first 10
            print(f"  - {file_path}: {protocol_name}")
        if len(empty_protocols) > 10:
            print(f"  ... and {len(empty_protocols) - 10} more")

    return duplicates


def main():
    src_dir = Path("src/omnibase_spi/protocols")

    print("Checking for duplicate protocol definitions...")
    duplicates = find_duplicate_protocols(src_dir)

    if duplicates:
        print(f"\nFound {len(duplicates)} groups of duplicate protocols:")
        print("=" * 60)

        for i, (sig_hash, protocols) in enumerate(duplicates.items(), 1):
            print(f"\nGroup {i} ({len(protocols)} duplicates):")
            for file_path, protocol_name in protocols[:10]:  # Show first 10
                print(f"  - {file_path}: {protocol_name}")
            if len(protocols) > 10:
                print(f"  ... and {len(protocols) - 10} more")
    else:
        print("\nNo duplicate protocols found!")

    print(f"\nTotal duplicate protocol groups: {len(duplicates)}")
    total_duplicates = sum(len(p) - 1 for p in duplicates.values())  # -1 to count extras only
    print(f"Total duplicate protocols that could be removed: {total_duplicates}")


if __name__ == "__main__":
    main()