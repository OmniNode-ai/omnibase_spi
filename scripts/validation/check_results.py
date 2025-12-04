#!/usr/bin/env python3
"""
Check validation results from the unified validation suite.

This script analyzes the JSON output from run_all_validations.py and determines
whether the validation passed based on configured strictness levels:

- Critical validators (naming_patterns, namespace_isolation): Must pass
- Non-critical validators (architecture): Informational only (technical debt)

Usage:
    python scripts/validation/check_results.py [options]
    python scripts/validation/check_results.py validation_results.json
    python scripts/validation/check_results.py --strict

Exit codes:
    0 - Success (all critical validators passed)
    1 - Failure (critical validators failed or file error)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Default results file name
DEFAULT_RESULTS_FILE = "validation_results.json"

# Validators that must pass for the build to succeed
CRITICAL_VALIDATORS: frozenset[str] = frozenset({
    "naming_patterns",
    "namespace_isolation",
})

# Validators that are informational only (known technical debt)
INFORMATIONAL_VALIDATORS: frozenset[str] = frozenset({
    "architecture",
})


def load_results(file_path: Path) -> dict[str, Any]:
    """
    Load validation results from JSON file.

    Args:
        file_path: Path to the validation results JSON file.

    Returns:
        Parsed JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the results file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Results file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_validators(
    data: dict[str, Any],
    strict: bool = False,
    verbose: bool = False,
) -> tuple[bool, list[str], list[str]]:
    """
    Check validation results against configured strictness levels.

    Args:
        data: Parsed validation results JSON.
        strict: If True, treat all validators as critical.
        verbose: If True, print detailed status for each validator.

    Returns:
        Tuple of (passed, failures, warnings) where:
        - passed: True if all critical validators passed
        - failures: List of critical validator failure messages
        - warnings: List of informational/warning messages
    """
    failures: list[str] = []
    warnings: list[str] = []

    validators = data.get("validators", [])

    if not validators:
        failures.append("No validators found in results file")
        return False, failures, warnings

    for validator in validators:
        name = validator.get("name", "<unknown>")
        passed = validator.get("passed", False)
        error = validator.get("error", "validation failed")

        if verbose:
            status = "PASSED" if passed else "FAILED"
            print(f"  [{status}] {name}")

        if not passed:
            if name in CRITICAL_VALIDATORS or (strict and name not in INFORMATIONAL_VALIDATORS):
                failures.append(f"{name}: {error}")
            elif name in INFORMATIONAL_VALIDATORS:
                warnings.append(f"{name}: has existing violations (technical debt)")
            else:
                # Unknown validator - treat as warning in non-strict mode
                if strict:
                    failures.append(f"{name}: {error}")
                else:
                    warnings.append(f"{name}: {error}")

    return len(failures) == 0, failures, warnings


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Check validation results from the unified validation suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python check_results.py
    python check_results.py validation_results.json
    python check_results.py --strict --verbose

Critical validators (must pass):
    - naming_patterns: Protocol and exception naming conventions
    - namespace_isolation: No forbidden imports (Infra, Pydantic)

Informational validators (known technical debt):
    - architecture: One-protocol-per-file rule (92 existing violations)
        """,
    )
    parser.add_argument(
        "results_file",
        nargs="?",
        default=DEFAULT_RESULTS_FILE,
        help=f"Path to validation results JSON file (default: {DEFAULT_RESULTS_FILE})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat all validators as critical (fail on any validation failure)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed status for each validator",
    )

    args = parser.parse_args()

    results_path = Path(args.results_file)

    # Load results
    try:
        data = load_results(results_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Make sure run_all_validations.py was executed with --json flag first.")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in results file: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to load results: {e}")
        return 1

    # Check validators
    if args.verbose:
        print(f"Checking validation results from: {results_path}")
        print()

    passed, failures, warnings = check_validators(
        data,
        strict=args.strict,
        verbose=args.verbose,
    )

    # Print failures
    if failures:
        print()
        for failure in failures:
            print(f"FAIL: {failure}")

    # Print warnings (informational)
    if warnings:
        print()
        for warning in warnings:
            print(f"INFO: {warning}")

    # Final result
    print()
    if passed:
        print("All critical validators passed!")
        return 0
    else:
        print(f"Validation failed: {len(failures)} critical validator(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
