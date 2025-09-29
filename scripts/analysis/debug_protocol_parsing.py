#!/usr/bin/env python3
"""
Debug script to understand why protocol parsing isn't working
"""

import ast


def debug_parse_file(file_path: str):
    print(f"🔍 Debugging parsing of: {file_path}")

    with open(file_path, "r") as f:
        content = f.read()

    tree = ast.parse(content)

    print(f"📄 AST nodes found:")

    protocol_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            print(f"   Class: {node.name}")

            # Check if this is a protocol class
            is_protocol = False
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "Protocol":
                    is_protocol = True
                    break

            if is_protocol:
                print(f"   ✅ {node.name} is a Protocol class")

                print(f"      Class body has {len(node.body)} items:")
                for i, item in enumerate(node.body):
                    print(
                        f"         {i+1}. {type(item).__name__}: {getattr(item, 'name', 'N/A')}"
                    )

                    if isinstance(item, ast.FunctionDef):
                        args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                        print(f"            Function: {item.name}({', '.join(args)})")

                    elif isinstance(item, ast.AnnAssign) and isinstance(
                        item.target, ast.Name
                    ):
                        attr_name = item.target.id
                        attr_type = (
                            ast.unparse(item.annotation) if item.annotation else "Any"
                        )
                        print(f"            Attribute: {attr_name}: {attr_type}")

                protocol_classes.append(node.name)
            else:
                print(f"   ❌ {node.name} is not a Protocol class")

    print(f"\n📊 Summary: Found {len(protocol_classes)} protocol classes")
    return protocol_classes


if __name__ == "__main__":
    # Test with the performance metrics file
    debug_parse_file("src/omnibase_spi/protocols/core/protocol_performance_metrics.py")

    print("\n" + "=" * 80)

    # Test with HTTP client file
    debug_parse_file("src/omnibase_spi/protocols/core/protocol_http_client.py")
