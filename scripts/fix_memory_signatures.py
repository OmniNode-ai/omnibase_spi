#!/usr/bin/env python3
"""
Script to fix method signatures and forward references in Memory domain.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


def fix_method_signatures(file_path: Path) -> Dict[str, int]:
    """Fix method signatures to use forward references."""
    fixes_applied = {"signatures": 0, "method_bodies": 0, "forward_refs": 0}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Replace ModelAgentConfig with "ModelAgentConfig" in return types and parameters
    content = re.sub(r"-> ModelAgentConfig\b", '-> "ModelAgentConfig"', content)
    content = re.sub(r"\bModelAgentConfig([^:])", '"ModelAgentConfig"\\1', content)

    # Replace ModelAgentInstance with "ModelAgentInstance" in return types and parameters
    content = re.sub(r"-> ModelAgentInstance\b", '-> "ModelAgentInstance"', content)
    content = re.sub(r"\bModelAgentInstance([^:])", '"ModelAgentInstance"\\1', content)

    # Replace ModelAgentHealthStatus with "ModelAgentHealthStatus" in return types and parameters
    content = re.sub(
        r"-> ModelAgentHealthStatus\b", '-> "ModelAgentHealthStatus"', content
    )
    content = re.sub(
        r"\bModelAgentHealthStatus([^:])", '"ModelAgentHealthStatus"\\1', content
    )

    # Replace ModelAgentStatus with "ModelAgentStatus" in return types and parameters
    content = re.sub(r"-> ModelAgentStatus\b", '-> "ModelAgentStatus"', content)
    content = re.sub(r"\bModelAgentStatus([^:])", '"ModelAgentStatus"\\1', content)

    # Replace ModelValidationResult with "ModelValidationResult" in return types and parameters
    content = re.sub(
        r"-> ModelValidationResult\b", '-> "ModelValidationResult"', content
    )
    content = re.sub(
        r"\bModelValidationResult([^:])", '"ModelValidationResult"\\1', content
    )

    # Replace ModelMemoryOperation with "ModelMemoryOperation" in return types and parameters
    content = re.sub(r"-> ModelMemoryOperation\b", '-> "ModelMemoryOperation"', content)
    content = re.sub(
        r"\bModelMemoryOperation([^:])", '"ModelMemoryOperation"\\1', content
    )

    # Replace ModelMemoryResponse with "ModelMemoryResponse" in return types and parameters
    content = re.sub(r"-> ModelMemoryResponse\b", '-> "ModelMemoryResponse"', content)
    content = re.sub(
        r"\bModelMemoryResponse([^:])", '"ModelMemoryResponse"\\1', content
    )

    # Replace ModelMemoryMetadata with "ModelMemoryMetadata" in return types and parameters
    content = re.sub(r"-> ModelMemoryMetadata\b", '-> "ModelMemoryMetadata"', content)
    content = re.sub(
        r"\bModelMemoryMetadata([^:])", '"ModelMemoryMetadata"\\1', content
    )

    # Replace ModelMemoryError with "ModelMemoryError" in return types and parameters
    content = re.sub(r"-> ModelMemoryError\b", '-> "ModelMemoryError"', content)
    content = re.sub(r"\bModelMemoryError([^:])", '"ModelMemoryError"\\1', content)

    # Replace ModelMemoryRequest with "ModelMemoryRequest" in return types and parameters
    content = re.sub(r"-> ModelMemoryRequest\b", '-> "ModelMemoryRequest"', content)
    content = re.sub(r"\bModelMemoryRequest([^:])", '"ModelMemoryRequest"\\1', content)

    # Replace ModelMemorySecurityContext with "ModelMemorySecurityContext" in return types and parameters
    content = re.sub(
        r"-> ModelMemorySecurityContext\b", '-> "ModelMemorySecurityContext"', content
    )
    content = re.sub(
        r"\bModelMemorySecurityContext([^:])",
        '"ModelMemorySecurityContext"\\1',
        content,
    )

    # Replace ModelMemoryStreamingResponse with "ModelMemoryStreamingResponse" in return types and parameters
    content = re.sub(
        r"-> ModelMemoryStreamingResponse\b",
        '-> "ModelMemoryStreamingResponse"',
        content,
    )
    content = re.sub(
        r"\bModelMemoryStreamingResponse([^:])",
        '"ModelMemoryStreamingResponse"\\1',
        content,
    )

    # Replace ModelMemoryStreamingRequest with "ModelMemoryStreamingRequest" in return types and parameters
    content = re.sub(
        r"-> ModelMemoryStreamingRequest\b", '-> "ModelMemoryStreamingRequest"', content
    )
    content = re.sub(
        r"\bModelMemoryStreamingRequest([^:])",
        '"ModelMemoryStreamingRequest"\\1',
        content,
    )

    # Replace ModelMemorySecurityPolicy with "ModelMemorySecurityPolicy" in return types and parameters
    content = re.sub(
        r"-> ModelMemorySecurityPolicy\b", '-> "ModelMemorySecurityPolicy"', content
    )
    content = re.sub(
        r"\bModelMemorySecurityPolicy([^:])", '"ModelMemorySecurityPolicy"\\1', content
    )

    # Replace ModelMemoryComposable with "ModelMemoryComposable" in return types and parameters
    content = re.sub(
        r"-> ModelMemoryComposable\b", '-> "ModelMemoryComposable"', content
    )
    content = re.sub(
        r"\bModelMemoryComposable([^:])", '"ModelMemoryComposable"\\1', content
    )

    # Replace ModelMemoryErrorHandling with "ModelMemoryErrorHandling" in return types and parameters
    content = re.sub(
        r"-> ModelMemoryErrorHandling\b", '-> "ModelMemoryErrorHandling"', content
    )
    content = re.sub(
        r"\bModelMemoryErrorHandling([^:])", '"ModelMemoryErrorHandling"\\1', content
    )

    # Count signature fixes
    signature_fixes = len(re.findall(r'-> "Model[A-Z][a-zA-Z]*"', content))
    fixes_applied["signatures"] = signature_fixes

    # Replace method bodies (remove empty lines after method definitions)
    content = re.sub(
        r'def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)(?: -> [^:]+)?:\s*\n\s*"""([^"]*+)"""\s*\n',
        lambda m: f'def {m.group(0).split("def ")[1].split("(")[0]}({m.group(0).split("(")[1].split(")")[0]}):\\n        """{m.group(1)}"""\\n        ...\\n\\n',
        content,
    )

    # Add ellipsis (...) to methods that don't have it
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith('"""') and i > 0:
            # Check if previous line is a method definition
            prev_line = lines[i - 1].strip()
            if prev_line.endswith(":") and not prev_line.startswith("class"):
                # Look for next non-empty line
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j >= len(lines) or not lines[j].strip().startswith("..."):
                    # Insert ellipsis
                    lines.insert(j, "        ...")
                    fixes_applied["method_bodies"] += 1

    content = "\n".join(lines)

    # Write back the fixed content
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed signatures in {file_path.name}")
    else:
        print(f"No signature fixes needed for {file_path.name}")

    return fixes_applied


def main():
    """Process all Memory domain files."""
    memory_dir = Path(
        "/Volumes/PRO-G40/Code/omnibase_spi/src/omnibase_spi/protocols/memory"
    )

    total_fixes = {"signatures": 0, "method_bodies": 0, "forward_refs": 0}

    print("Processing Memory domain files for signature fixes...")

    for file_path in memory_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            fixes = fix_method_signatures(file_path)
            for key, value in fixes.items():
                total_fixes[key] += value

    print(f"\nTotal signature fixes applied:")
    print(f"  Method signatures: {total_fixes['signatures']}")
    print(f"  Method bodies: {total_fixes['method_bodies']}")
    print(f"  Forward references: {total_fixes['forward_refs']}")
    print(f"  Total: {sum(total_fixes.values())}")


if __name__ == "__main__":
    main()
