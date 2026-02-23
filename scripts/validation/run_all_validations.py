#!/usr/bin/env python3
"""
Unified Validation Runner for omnibase_spi.

Runs all SPI validation scripts in sequence and provides a summary report.
This is a STANDALONE script using only Python stdlib (no omnibase_core imports).

Validators Executed:
    1. Architecture Validation - Domain cohesion rule (max protocols per file)
    2. Naming Pattern Validation - Protocol/Error naming and @runtime_checkable
    3. Namespace Isolation Validation - No Infra imports, no Pydantic models

Usage:
    python scripts/validation/run_all_validations.py
    python scripts/validation/run_all_validations.py --strict
    python scripts/validation/run_all_validations.py --verbose
    python scripts/validation/run_all_validations.py --strict --verbose

Options:
    --strict    Fail on any violation (exit code 1)
    --verbose   Show detailed output from each validator
    --json      Output results as JSON (includes all validator results)

Exit Codes:
    0 - All validators passed (or --strict not set)
    1 - One or more validators failed (with --strict)
    2 - Script error (e.g., validator script not found)

Author: OmniNode Team
Version: 1.0.0 (Temporary - standalone until Core removes SPI dependency)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class ValidatorResult:
    """Result from running a single validator."""

    name: str
    description: str
    exit_code: int
    duration_seconds: float
    stdout: str = ""
    stderr: str = ""
    error: str | None = None

    @property
    def passed(self) -> bool:
        """Check if validator passed (exit code 0)."""
        return self.exit_code == 0 and self.error is None

    @property
    def status(self) -> str:
        """Human-readable status."""
        if self.error:
            return "ERROR"
        return "PASS" if self.passed else "FAIL"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "passed": self.passed,
            "error": self.error,
        }


@dataclass
class ValidationSummary:
    """Summary of all validation results."""

    results: list[ValidatorResult] = field(default_factory=list)
    total_duration_seconds: float = 0.0

    @property
    def all_passed(self) -> bool:
        """Check if all validators passed."""
        return all(r.passed for r in self.results)

    @property
    def passed_count(self) -> int:
        """Count of passed validators."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        """Count of failed validators."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def error_count(self) -> int:
        """Count of validators with errors."""
        return sum(1 for r in self.results if r.error is not None)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "all_passed": self.all_passed,
            "total_validators": len(self.results),
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "error_count": self.error_count,
            "total_duration_seconds": round(self.total_duration_seconds, 3),
            "validators": [r.to_dict() for r in self.results],
        }


# ============================================================================
# Validator Configuration
# ============================================================================


@dataclass
class ValidatorConfig:
    """Configuration for a validator script."""

    name: str
    script_name: str
    description: str
    extra_args: list[str] = field(default_factory=list)


# Define all validators to run
VALIDATORS: list[ValidatorConfig] = [
    ValidatorConfig(
        name="architecture",
        script_name="validate_architecture.py",
        description="Domain cohesion rule (max 15 protocols per file)",
        extra_args=["--strict"],
    ),
    ValidatorConfig(
        name="naming_patterns",
        script_name="validate_naming_patterns.py",
        description="Naming conventions and @runtime_checkable decorator",
        extra_args=[],  # Uses default path (src/)
    ),
    ValidatorConfig(
        name="namespace_isolation",
        script_name="validate_namespace_isolation.py",
        description="No Infra imports, no Pydantic models",
        extra_args=[],  # Uses default path (src/omnibase_spi)
    ),
]


# ============================================================================
# Validator Runner
# ============================================================================


def find_repo_root() -> Path:
    """Find the repository root by looking for pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    # Fallback: assume we're in scripts/validation/
    return Path(__file__).resolve().parent.parent.parent


def run_validator(
    config: ValidatorConfig,
    repo_root: Path,
    verbose: bool = False,
) -> ValidatorResult:
    """
    Run a single validator script.

    Args:
        config: Validator configuration
        repo_root: Path to repository root
        verbose: Whether to show verbose output

    Returns:
        ValidatorResult with execution details
    """
    script_path = repo_root / "scripts" / "validation" / config.script_name

    # Check script exists
    if not script_path.exists():
        return ValidatorResult(
            name=config.name,
            description=config.description,
            exit_code=2,
            duration_seconds=0.0,
            error=f"Script not found: {script_path}",
        )

    # Build command
    cmd = [sys.executable, str(script_path)] + config.extra_args

    # Add verbose flag if verbose mode is on (all validators support --verbose)
    if verbose:
        cmd.append("--verbose")

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=300,  # 5 minute timeout
        )
        duration = time.time() - start_time

        return ValidatorResult(
            name=config.name,
            description=config.description,
            exit_code=result.returncode,
            duration_seconds=duration,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return ValidatorResult(
            name=config.name,
            description=config.description,
            exit_code=2,
            duration_seconds=duration,
            error="Validator timed out after 5 minutes",
        )

    except Exception as e:
        duration = time.time() - start_time
        return ValidatorResult(
            name=config.name,
            description=config.description,
            exit_code=2,
            duration_seconds=duration,
            error=str(e),
        )


def run_all_validators(
    verbose: bool = False,
) -> ValidationSummary:
    """
    Run all validators and collect results.

    Args:
        verbose: Whether to show verbose output

    Returns:
        ValidationSummary with all results
    """
    repo_root = find_repo_root()
    summary = ValidationSummary()

    total_start = time.time()

    for config in VALIDATORS:
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Running: {config.name}")
            print(f"Description: {config.description}")
            print("=" * 60)

        result = run_validator(config, repo_root, verbose)
        summary.results.append(result)

        if verbose and result.stdout:
            print(result.stdout)
        if verbose and result.stderr:
            print(result.stderr, file=sys.stderr)

    summary.total_duration_seconds = time.time() - total_start

    return summary


# ============================================================================
# Output Formatting
# ============================================================================


def print_summary(summary: ValidationSummary, verbose: bool = False) -> None:
    """Print validation summary."""
    print()
    print("=" * 70)
    print("UNIFIED SPI VALIDATION SUMMARY")
    print("=" * 70)

    # Print each validator result
    print()
    print("VALIDATOR RESULTS:")
    print("-" * 70)

    for result in summary.results:
        status_icon = "[PASS]" if result.passed else "[FAIL]"
        if result.error:
            status_icon = "[ERR!]"

        duration_str = f"{result.duration_seconds:.2f}s"
        print(
            f"  {status_icon} {result.name:<25} {duration_str:>8}  {result.description}"
        )

        if result.error:
            print(f"         ERROR: {result.error}")

    # Print summary stats
    print()
    print("-" * 70)
    print("STATISTICS:")
    print(f"  Total validators:    {len(summary.results)}")
    print(f"  Passed:              {summary.passed_count}")
    print(f"  Failed:              {summary.failed_count}")
    if summary.error_count > 0:
        print(f"  Errors:              {summary.error_count}")
    print(f"  Total duration:      {summary.total_duration_seconds:.2f}s")

    # Print overall result
    print()
    print("=" * 70)
    if summary.all_passed:
        print("RESULT: ALL VALIDATIONS PASSED")
    else:
        print("RESULT: VALIDATION FAILURES DETECTED")
        if not verbose:
            print()
            print("Run with --verbose to see detailed output from failed validators.")
    print("=" * 70)


def print_json_output(summary: ValidationSummary) -> None:
    """Print validation summary as JSON."""
    print(json.dumps(summary.to_dict(), indent=2))


# ============================================================================
# CLI Entry Point
# ============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run all SPI validation scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Validators:
  1. architecture         Domain cohesion rule (max 15 protocols per file)
  2. naming_patterns      Naming conventions and @runtime_checkable
  3. namespace_isolation  No Infra imports, no Pydantic models

Examples:
  %(prog)s                     Run all validators
  %(prog)s --strict            Exit 1 on any failure
  %(prog)s --verbose           Show detailed output
  %(prog)s --json              Output as JSON

Note: These are TEMPORARY standalone validators. They will be replaced
by omnibase_core.validation when Core removes its SPI dependency.
""",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any violation (exit code 1)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output from each validator",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Print header unless JSON output
    if not args.json:
        print("Running SPI Validation Suite...")
        print(f"Validators to run: {len(VALIDATORS)}")

    # Run all validators
    summary = run_all_validators(verbose=args.verbose)

    # Output results
    if args.json:
        print_json_output(summary)
    else:
        print_summary(summary, verbose=args.verbose)

    # Determine exit code
    if args.strict and not summary.all_passed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
