#!/usr/bin/env python3
"""Debug protocol signature detection."""

import ast
from pathlib import Path


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

            if item.decorator_list and any(
                isinstance(d, ast.Name) and d.id == "property"
                for d in item.decorator_list
            ):
                properties.append(sig)
            else:
                methods.append(sig)

        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            # Get property annotation
            prop_type = ""
            if item.annotation:
                prop_type = ast.unparse(item.annotation)
            properties.append(f"{item.target.id}: {prop_type}")

    return f"Properties: {properties}\nMethods: {methods}"


def check_sample_protocols():
    """Check signature for specific protocols."""
    test_files = [
        "src/omnibase_spi/protocols/container/protocol_container_service.py",
        "src/omnibase_spi/protocols/container/protocol_service_registry.py",
    ]

    for file_path in test_files:
        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(path))

        print(f"\n{file_path}:")
        print("=" * 60)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Protocol
                is_protocol = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Protocol":
                        is_protocol = True
                        break

                if is_protocol:
                    sig = get_protocol_signature(node)
                    print(f"\n{node.name}:")
                    print(sig)


if __name__ == "__main__":
    check_sample_protocols()