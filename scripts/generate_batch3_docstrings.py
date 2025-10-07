#!/usr/bin/env python3
"""
Script to generate comprehensive docstrings for batch 3 protocols.

Batch 3 includes:
- LLM protocols (3 files) ✅ Already completed manually
- MCP protocols (14 files)
- Memory protocols (11 files)
- Validation protocols (10 files)
- Workflow Orchestration protocols (12 files)
- Type files (3 files)
"""

import ast
import sys
from pathlib import Path
from typing import Any


def enhance_method_docstring(
    method_name: str, node: ast.FunctionDef, domain: str
) -> str:
    """Generate enhanced docstring for a protocol method."""
    # Get existing docstring
    existing = ast.get_docstring(node) or f"{method_name} method."

    # Extract return type and parameters
    returns = ""
    if node.returns:
        returns = ast.unparse(node.returns)

    params = []
    for arg in node.args.args:
        if arg.arg != "self":
            param_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            params.append((arg.arg, param_type))

    # Build enhanced docstring
    lines = [f"{existing.strip()}", ""]

    # Add Args section if there are parameters
    if params:
        lines.append("Args:")
        for param_name, param_type in params:
            lines.append(f"    {param_name}: {param_name} parameter")
        lines.append("")

    # Add Returns section
    if returns:
        lines.append("Returns:")
        lines.append(f"    {returns}")
        lines.append("")

    # Add domain-specific example
    if domain == "workflow_orchestration":
        lines.extend(
            [
                "Example:",
                "    ```python",
                f"    # Workflow orchestration example for {method_name}",
                f"    result = await protocol.{method_name}(...)",
                "    # Process result with event sourcing patterns",
                "    ```",
                "",
            ]
        )
    elif domain == "mcp":
        lines.extend(
            [
                "Example:",
                "    ```python",
                f"    # MCP tool coordination example for {method_name}",
                f"    result = await registry.{method_name}(...)",
                "    # Handle multi-subsystem coordination",
                "    ```",
                "",
            ]
        )

    return "\n        ".join(lines)


def enhance_protocol_file(file_path: Path, domain: str) -> tuple[bool, str]:
    """Enhance a protocol file with comprehensive docstrings."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        # Count protocols that need enhancement
        protocols_found = 0
        methods_found = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Protocol class
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Protocol":
                        protocols_found += 1
                        # Count methods in this protocol
                        for item in node.body:
                            if (
                                isinstance(item, ast.FunctionDef)
                                and item.name != "__init__"
                            ):
                                methods_found += 1

        return True, f"Found {protocols_found} protocols with {methods_found} methods"

    except Exception as e:
        return False, f"Error processing {file_path}: {e}"


def main():
    """Main script execution."""
    base_path = Path("src/omnibase_spi/protocols")

    # Define batch 3 domains
    domains = {
        "mcp": list((base_path / "mcp").glob("protocol_*.py")),
        "memory": list((base_path / "memory").glob("protocol_*.py")),
        "validation": list((base_path / "validation").glob("protocol_*.py")),
        "workflow_orchestration": list(
            (base_path / "workflow_orchestration").glob("protocol_*.py")
        ),
    }

    print("Batch 3 Protocol Documentation Enhancement")
    print("=" * 60)

    total_files = 0
    total_protocols = 0
    total_methods = 0

    for domain, files in domains.items():
        print(f"\n{domain.upper()} Domain:")
        print(f"  Files to process: {len(files)}")

        for file_path in sorted(files):
            success, message = enhance_protocol_file(file_path, domain)
            if success:
                print(f"    ✅ {file_path.name}: {message}")
                total_files += 1
            else:
                print(f"    ❌ {file_path.name}: {message}")

    print(f"\n{'='*60}")
    print(f"Total files analyzed: {total_files}")
    print("\nNote: This analysis identifies protocols needing enhancement.")
    print("Actual docstring generation requires AST manipulation and careful editing.")


if __name__ == "__main__":
    main()
