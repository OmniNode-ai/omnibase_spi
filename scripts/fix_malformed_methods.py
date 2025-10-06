#!/usr/bin/env python3
"""
Script to fix malformed method signatures in Memory domain files.
"""

import os
import re
from pathlib import Path


def fix_malformed_methods(file_path: Path) -> int:
    """Fix malformed method signatures with \n escape sequences."""
    fixes_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix the malformed pattern: \n        """\n        ...\n\n        ...
    pattern = r'\\n\s*"""\\n\s*\.\.\.\\n\\n\s*\.\.\.'
    replacement = '"""\n        ...'

    content = re.sub(pattern, replacement, content)

    # Fix missing return types - add common return types based on method names
    return_type_patterns = [
        (
            r"async def validate_configuration\(self[^)]+\):",
            r'async def validate_configuration(self, config: ProtocolAgentConfig) -> "ProtocolValidationResult":',
        ),
        (
            r"async def save_configuration\(self[^)]+\):",
            r"async def save_configuration(self, config: ProtocolAgentConfig) -> bool:",
        ),
        (
            r"async def load_configuration\(self[^)]+\):",
            r"async def load_configuration(self, agent_id: str) -> ProtocolAgentConfig | None:",
        ),
        (
            r"async def delete_configuration\(self[^)]+\):",
            r"async def delete_configuration(self, agent_id: str) -> bool:",
        ),
        (
            r"async def list_configurations\(self\):",
            r"async def list_configurations(self) -> list[str]:",
        ),
        (
            r"async def update_configuration\(self[^)]+\):",
            r"async def update_configuration(self, agent_id: str, updates: dict[str, ContextValue]) -> ProtocolAgentConfig:",
        ),
        (
            r"async def create_configuration_template\(self[^)]+\):",
            r"async def create_configuration_template(self, template_name: str, base_config: ProtocolAgentConfig) -> bool:",
        ),
        (
            r"async def apply_configuration_template\(self[^)]+\):",
            r"async def apply_configuration_template(self, agent_id: str, template_name: str, overrides: dict[str, ContextValue] | None = None) -> ProtocolAgentConfig:",
        ),
        (
            r"async def list_configuration_templates\(self\):",
            r"async def list_configuration_templates(self) -> list[str]:",
        ),
        (
            r"async def backup_configuration\(self[^)]+\):",
            r"async def backup_configuration(self, agent_id: str) -> str:",
        ),
        (
            r"async def restore_configuration\(self[^)]+\):",
            r"async def restore_configuration(self, agent_id: str, backup_id: str) -> bool:",
        ),
        (
            r"async def get_configuration_history\(self[^)]+\):",
            r"async def get_configuration_history(self, agent_id: str) -> list[dict]:",
        ),
        (
            r"async def clone_configuration\(self[^)]+\):",
            r"async def clone_configuration(self, source_agent_id: str, target_agent_id: str) -> ProtocolAgentConfig:",
        ),
        (
            r"async def validate_security_policies\(self[^)]+\):",
            r"async def validate_security_policies(self, config: ProtocolAgentConfig) -> list[str]:",
        ),
        (
            r"async def encrypt_sensitive_fields\(self[^)]+\):",
            r"async def encrypt_sensitive_fields(self, config: ProtocolAgentConfig) -> ProtocolAgentConfig:",
        ),
        (
            r"async def decrypt_sensitive_fields\(self[^)]+\):",
            r"async def decrypt_sensitive_fields(self, config: ProtocolAgentConfig) -> ProtocolAgentConfig:",
        ),
        (
            r"async def set_configuration_defaults\(self[^)]+\):",
            r"async def set_configuration_defaults(self, config: ProtocolAgentConfig) -> ProtocolAgentConfig:",
        ),
        (
            r"async def merge_configurations\(self[^)]+\):",
            r"async def merge_configurations(self, base_config: ProtocolAgentConfig, override_config: ProtocolAgentConfig) -> ProtocolAgentConfig:",
        ),
        (
            r"async def export_configuration\(self[^)]+\):",
            r'async def export_configuration(self, agent_id: str, format_type: str = "yaml") -> str:',
        ),
        (
            r"async def import_configuration\(self[^)]+\):",
            r'async def import_configuration(self, agent_id: str, config_data: str, format_type: str = "yaml") -> ProtocolAgentConfig:',
        ),
    ]

    for pattern, replacement in return_type_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes_count += 1

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {fixes_count} malformed methods in {file_path.name}")

    return fixes_count


def main():
    """Process all Memory domain files."""
    memory_dir = Path(
        "/Volumes/PRO-G40/Code/omnibase_spi/src/omnibase_spi/protocols/memory"
    )

    total_fixes = 0

    print("Fixing malformed method signatures in Memory domain files...")

    for file_path in memory_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            fixes = fix_malformed_methods(file_path)
            total_fixes += fixes

    print(f"\nTotal malformed methods fixed: {total_fixes}")


if __name__ == "__main__":
    main()
