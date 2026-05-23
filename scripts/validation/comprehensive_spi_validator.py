#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Comprehensive SPI Protocol Validation Framework - omnibase_spi Architecture Compliance

The definitive SPI compliance checker providing comprehensive architectural validation,
configurable rule engine, detailed reporting, and CI/CD integration capabilities.

Key Features:
1. No __init__ methods in protocol definitions
2. No duplicate protocol definitions with conflict resolution
3. All I/O operations must be async by default
4. Proper typing constraints (ContextValue, Callable patterns)
5. Namespace isolation compliance validation
6. @runtime_checkable decorator enforcement
7. Protocol naming convention validation
8. Type safety and forward reference validation
9. Configurable validation rules engine
10. Comprehensive reporting with fix suggestions
11. Pre-commit hooks and CI/CD integration ready
12. Performance optimization with caching

Usage:
    # Basic validation with comprehensive checks
    python scripts/validation/comprehensive_spi_validator.py src/

    # Validation with configuration file
    python scripts/validation/comprehensive_spi_validator.py src/ --config validation_config.yaml

    # Auto-fix mode for supported violations
    python scripts/validation/comprehensive_spi_validator.py src/ --fix

    # Generate JSON report for CI/CD integration
    python scripts/validation/comprehensive_spi_validator.py src/ --json-report

    # Pre-commit integration mode
    python scripts/validation/comprehensive_spi_validator.py --pre-commit

Author: Claude Code Agent (ONEX Framework)
Version: 2.0.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import timeout_utils
from spi_validator.autofix import AutoFixEngine
from spi_validator.config import ValidationConfig
from spi_validator.duplicate_analyzer import DuplicateProtocolAnalyzer
from spi_validator.engine import (
    ComprehensiveSPIValidationEngine,
    create_sample_config_file,
)
from spi_validator.file_validator import ComprehensiveSPIValidator
from spi_validator.models import ProtocolInfo, ProtocolViolation, ValidationReport

# Re-exported so importlib-based test loaders can access them by attribute name.
__all__ = [
    "AutoFixEngine",
    "ComprehensiveSPIValidationEngine",
    "ComprehensiveSPIValidator",
    "DuplicateProtocolAnalyzer",
    "ProtocolInfo",
    "ProtocolViolation",
    "ValidationConfig",
    "ValidationReport",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comprehensive SPI Protocol Validation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s src/                                    # Basic validation
  %(prog)s src/ --config validation.yaml          # Custom configuration
  %(prog)s src/ --fix                             # Apply auto-fixes
  %(prog)s src/ --json-report                     # Generate JSON report
  %(prog)s --create-config validation.yaml        # Create sample config
  %(prog)s --pre-commit                           # Pre-commit mode
        """,
    )

    parser.add_argument(
        "path", nargs="?", default="src/", help="Path to validate (file or directory)"
    )
    parser.add_argument("--config", "-c", help="Configuration file path (YAML format)")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply automatic fixes for supported violations",
    )
    parser.add_argument(
        "--json-report",
        action="store_true",
        help="Generate JSON report for CI/CD integration",
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML report with interactive features",
    )
    parser.add_argument(
        "--create-config", help="Create sample configuration file at specified path"
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Pre-commit integration mode (faster validation)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed progress",
    )

    args = parser.parse_args()

    try:
        if args.create_config:
            create_sample_config_file(args.create_config)
            return 0

        config = ValidationConfig(args.config)

        if args.pre_commit:
            config.global_settings["timeout_seconds"] = 60
            config.global_settings["max_violations_per_file"] = 20
            for rule in config.rules.values():
                if rule.category in ["documentation", "performance"]:
                    rule.enabled = False

        engine = ComprehensiveSPIValidationEngine(config)

        target_path = Path(args.path)
        if not target_path.exists():
            print(f"❌ Path does not exist: {target_path}")
            return 1

        if args.verbose:
            print("🔍 Starting comprehensive SPI validation")
            print(f"   Target: {target_path}")
            print(f"   Config: {args.config or 'built-in defaults'}")
            print(f"   Auto-fix: {'enabled' if args.fix else 'disabled'}")
            print(f"   Mode: {'pre-commit' if args.pre_commit else 'standard'}")

        if target_path.is_file():
            report = engine.validate_single_file(target_path)
        else:
            report = engine.validate_directory(
                target_path,
                apply_fixes=args.fix,
                generate_json=args.json_report,
                generate_html=args.html_report,
            )

        return 1 if report.error_count > 0 else 0

    except timeout_utils.TimeoutError:
        print("❌ Validation timed out")
        return 1
    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
