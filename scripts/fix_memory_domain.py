#!/usr/bin/env python3
"""
Script to remediate Memory domain SPI purity violations.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


def fix_memory_domain_file(file_path: Path) -> Dict[str, int]:
    """Fix SPI purity violations in a Memory domain file."""
    violations_fixed = {
        "namespace": 0,
        "concrete_classes": 0,
        "abstract_methods": 0,
        "runtime_checkable": 0,
    }

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix namespace violations - remove omnibase_core imports
    namespace_pattern = r"from omnibase_core\.models?\.[^\n]+\n"
    content = re.sub(namespace_pattern, "", content)
    violations_fixed["namespace"] = len(re.findall(namespace_pattern, original_content))

    # Add forward reference section if it doesn't exist
    if "if TYPE_CHECKING:" not in content:
        # Find the imports section and add forward references after it
        lines = content.split("\n")
        import_end = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                import_end = i + 1
            elif line.strip() == "" and import_end > 0:
                break

        # Insert forward reference section
        forward_ref_section = '''if TYPE_CHECKING:
    # Forward references for agent configuration and model types
    class ModelAgentConfig:
        """Protocol for agent configuration."""
        agent_id: str
        agent_type: str
        configuration: dict[str, Any]
        security_context: dict[str, Any]

    class ModelAgentInstance:
        """Protocol for agent instance."""
        instance_id: str
        agent_id: str
        status: str
        health_status: str
        configuration: "ModelAgentConfig"

    class ModelAgentHealthStatus:
        """Protocol for agent health status."""
        status: str
        last_check: str
        metrics: dict[str, Any]

    class ModelAgentStatus:
        """Protocol for agent status."""
        state: str
        error_message: str | None
        last_activity: str

    class ModelValidationResult:
        """Protocol for validation results."""
        is_valid: bool
        errors: list[str]
        warnings: list[str]

    class ModelMemoryOperation:
        """Protocol for memory operations."""
        operation_type: str
        data: dict[str, Any]
        timestamp: str

    class ModelMemoryResponse:
        """Protocol for memory responses."""
        success: bool
        data: Any
        error_message: str | None

    class ModelMemoryMetadata:
        """Protocol for memory metadata."""
        size: int
        created_at: str
        modified_at: str
        access_count: int

    class ModelMemoryError:
        """Protocol for memory errors."""
        error_type: str
        message: str
        details: dict[str, Any]

    class ModelMemoryRequest:
        """Protocol for memory requests."""
        operation: str
        key: str
        data: Any
        options: dict[str, Any]

    class ModelMemoryResponse:
        """Protocol for memory responses."""
        success: bool
        data: Any
        error: str | None

    class ModelMemorySecurityContext:
        """Protocol for memory security context."""
        user_id: str
        permissions: list[str]
        session_id: str

    class ModelMemoryStreamingResponse:
        """Protocol for streaming memory responses."""
        chunk_id: str
        data: Any
        is_last: bool

    class ModelMemoryStreamingRequest:
        """Protocol for streaming memory requests."""
        stream_id: str
        operation: str
        parameters: dict[str, Any]

    class ModelMemorySecurityPolicy:
        """Protocol for memory security policies."""
        policy_id: str
        rules: list[dict[str, Any]]
        default_action: str

    class ModelMemoryComposable:
        """Protocol for composable memory operations."""
        components: list[str]
        operations: list[str]
        metadata: dict[str, Any]

    class ModelMemoryErrorHandling:
        """Protocol for memory error handling."""
        error_type: str
        severity: str
        recovery_strategy: str
        context: dict[str, Any]


'''
        lines.insert(import_end, forward_ref_section)
        content = "\n".join(lines)

    # Fix concrete classes - convert ABC/abstractmethod to Protocol
    content = content.replace("from abc import ABC, abstractmethod", "")
    content = content.replace("from abc import ABC", "")
    content = content.replace(
        "class ProtocolAgentConfiguration(ABC):",
        "@runtime_checkable\nclass ProtocolAgentConfiguration(Protocol):",
    )
    content = content.replace(
        "class ProtocolAgentManager(ABC):",
        "@runtime_checkable\nclass ProtocolAgentManager(Protocol):",
    )
    content = content.replace(
        "class ProtocolAgentPool(ABC):",
        "@runtime_checkable\nclass ProtocolAgentPool(Protocol):",
    )
    content = content.replace(
        "class ProtocolDistributedAgentOrchestrator(ABC):",
        "@runtime_checkable\nclass ProtocolDistributedAgentOrchestrator(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryBase(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryBase(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryComposable(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryComposable(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryOperations(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryOperations(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryRequests(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryRequests(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryResponses(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryResponses(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemorySecurity(ABC):",
        "@runtime_checkable\nclass ProtocolMemorySecurity(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryStreaming(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryStreaming(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryErrorHandling(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryErrorHandling(Protocol):",
    )
    content = content.replace(
        "class ProtocolMemoryErrors(ABC):",
        "@runtime_checkable\nclass ProtocolMemoryErrors(Protocol):",
    )

    # Count concrete class fixes
    if "class ProtocolAgentConfiguration(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolAgentManager(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolAgentPool(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolDistributedAgentOrchestrator(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryBase(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryComposable(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryOperations(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryRequests(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryResponses(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemorySecurity(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryStreaming(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryErrorHandling(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1
    if "class ProtocolMemoryErrors(ABC):" in original_content:
        violations_fixed["concrete_classes"] += 1

    # Remove @abstractmethod decorators
    content = content.replace("    @abstractmethod\n", "")
    violations_fixed["abstract_methods"] = original_content.count(
        "    @abstractmethod\n"
    )

    # Add @runtime_checkable decorator if missing
    if "@runtime_checkable" not in content:
        # Find the first class definition
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("class Protocol") and "(Protocol):" in line:
                if i > 0 and not lines[i - 1].strip().startswith("@runtime_checkable"):
                    lines.insert(i, "@runtime_checkable")
                    violations_fixed["runtime_checkable"] += 1
                break
        content = "\n".join(lines)

    # Update imports to include Protocol, runtime_checkable, TYPE_CHECKING
    if "from typing import" in content:
        imports_line = re.search(r"from typing import (.+)", content)
        if imports_line:
            current_imports = imports_line.group(1)
            required_imports = set(["Protocol", "runtime_checkable", "TYPE_CHECKING"])
            current_imports_set = set(imp.strip() for imp in current_imports.split(","))

            # Add required imports
            missing_imports = required_imports - current_imports_set
            if missing_imports:
                new_imports = current_imports
                for imp in sorted(missing_imports):
                    new_imports += f", {imp}"
                content = content.replace(
                    imports_line.group(0), f"from typing import {new_imports}"
                )

    # Add Any import if not present and needed
    if (
        "Any" in content
        and "Any" not in content.split("from typing import")[1].split("\n")[0]
    ):
        if "from typing import" in content:
            imports_line = re.search(r"from typing import (.+)", content)
            if imports_line and "Any" not in imports_line.group(1):
                content = content.replace(
                    imports_line.group(0),
                    imports_line.group(0).replace(
                        "typing import", "typing import Any,"
                    ),
                )

    # Write back the fixed content
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {file_path.name}: {sum(violations_fixed.values())} violations")
    else:
        print(f"No fixes needed for {file_path.name}")

    return violations_fixed


def main():
    """Process all Memory domain files."""
    memory_dir = Path(
        "/Volumes/PRO-G40/Code/omnibase_spi/src/omnibase_spi/protocols/memory"
    )

    total_fixes = {
        "namespace": 0,
        "concrete_classes": 0,
        "abstract_methods": 0,
        "runtime_checkable": 0,
    }

    print("Processing Memory domain files...")

    for file_path in memory_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            fixes = fix_memory_domain_file(file_path)
            for key, value in fixes.items():
                total_fixes[key] += value

    print(f"\nTotal fixes applied:")
    print(f"  Namespace violations: {total_fixes['namespace']}")
    print(f"  Concrete classes: {total_fixes['concrete_classes']}")
    print(f"  Abstract methods: {total_fixes['abstract_methods']}")
    print(f"  Runtime checkable: {total_fixes['runtime_checkable']}")
    print(f"  Total: {sum(total_fixes.values())}")


if __name__ == "__main__":
    main()
