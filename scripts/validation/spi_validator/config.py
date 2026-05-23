# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import ValidationRule


class ValidationConfig:
    def __init__(self, config_file: str | None = None):
        self.rules: dict[str, ValidationRule] = {}
        self.global_settings: dict[str, Any] = {}
        self._load_default_config()

        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)

    def _load_default_config(self) -> None:
        default_rules = [
            ValidationRule(
                rule_id="SPI001",
                name="No Protocol __init__ Methods",
                description="Protocols should not have __init__ methods - use properties or class attributes instead",
                severity="error",
                auto_fixable=False,
                category="protocol_structure",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI002",
                name="Protocol Naming Convention",
                description="Protocol classes should start with 'Protocol' prefix for consistency",
                severity="warning",
                auto_fixable=False,
                category="naming",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI003",
                name="Runtime Checkable Decorator",
                description="All protocols must be @runtime_checkable for isinstance() support",
                severity="error",
                auto_fixable=True,
                category="decorators",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI004",
                name="Protocol Method Bodies",
                description="Protocol methods should have '...' implementation, not concrete code",
                severity="error",
                auto_fixable=True,
                category="protocol_structure",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI005",
                name="Async I/O Operations",
                description="I/O operations should use async def instead of synchronous patterns",
                severity="error",
                auto_fixable=True,
                category="async_patterns",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI006",
                name="Proper Callable Types",
                description="Use 'Callable' types instead of generic 'object' for function parameters",
                severity="error",
                auto_fixable=False,
                category="typing",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI007",
                name="No Concrete Classes in SPI",
                description="SPI should only contain Protocol definitions, not concrete implementations",
                severity="error",
                auto_fixable=False,
                category="spi_purity",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI008",
                name="No Standalone Functions",
                description="SPI should not contain standalone functions - use Protocol methods instead",
                severity="warning",
                auto_fixable=False,
                category="spi_purity",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI009",
                name="ContextValue Usage Patterns",
                description="Consistent ContextValue usage for type-safe context data",
                severity="warning",
                auto_fixable=False,
                category="typing",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI010",
                name="Duplicate Protocol Detection",
                description="No duplicate protocol definitions with identical signatures",
                severity="error",
                auto_fixable=False,
                category="duplicates",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI011",
                name="Protocol Name Conflicts",
                description="No naming conflicts between protocols with different signatures",
                severity="error",
                auto_fixable=False,
                category="duplicates",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI012",
                name="Namespace Isolation",
                description="Maintain strict namespace isolation with omnibase_spi.protocols.* imports only",
                severity="error",
                auto_fixable=False,
                category="namespace",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI013",
                name="Forward Reference Typing",
                description="Use proper forward references with TYPE_CHECKING for model types",
                severity="warning",
                auto_fixable=False,
                category="typing",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI014",
                name="Protocol Documentation",
                description="All protocols should have comprehensive docstrings with examples",
                severity="warning",
                auto_fixable=False,
                category="documentation",
                priority=3,
            ),
            ValidationRule(
                rule_id="SPI015",
                name="Method Type Annotations",
                description="All protocol methods must have complete type annotations",
                severity="error",
                auto_fixable=False,
                category="typing",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI016",
                name="SPI Implementation Purity",
                description="SPI files must not contain implementation logic (if/else, assignments, function calls)",
                severity="error",
                auto_fixable=False,
                category="purity",
                priority=1,
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

        self.global_settings = {
            "max_file_size": 1024 * 1024,
            "timeout_seconds": 300,
            "parallel_processing": True,
            "enable_caching": True,
            "cache_ttl_seconds": 3600,
            "max_violations_per_file": 100,
            "enable_performance_metrics": True,
        }

    def _load_config_file(self, config_file: str) -> None:
        try:
            with open(config_file) as f:
                config_data = yaml.safe_load(f)

            if "global_settings" in config_data:
                self.global_settings.update(config_data["global_settings"])

            if "rules" in config_data:
                for rule_config in config_data["rules"]:
                    rule_id = rule_config.get("rule_id")
                    if rule_id in self.rules:
                        rule = self.rules[rule_id]
                        for key, value in rule_config.items():
                            if hasattr(rule, key):
                                setattr(rule, key, value)

        except Exception as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")

    def get_enabled_rules(self) -> list[ValidationRule]:
        enabled_rules = [rule for rule in self.rules.values() if rule.enabled]
        return sorted(enabled_rules, key=lambda r: (r.priority, r.rule_id))

    def get_rule(self, rule_id: str) -> ValidationRule | None:
        return self.rules.get(rule_id)
