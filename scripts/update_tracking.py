#!/usr/bin/env python3
"""
Update remediation tracking metrics from latest validation report.

Usage:
    python scripts/update_tracking.py
    python scripts/update_tracking.py --validation-file comprehensive_spi_validation_20251006_123600.json
"""

import glob
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def find_latest_validation_report(base_dir: Path) -> Path:
    """Find the most recent validation report."""
    pattern = str(base_dir / "comprehensive_spi_validation_*.json")
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(f"No validation reports found matching {pattern}")

    # Sort by timestamp in filename
    latest = sorted(files)[-1]
    return Path(latest)


def extract_metrics(validation_file: Path) -> Dict[str, Any]:
    """Extract key metrics from validation report."""
    with open(validation_file, "r") as f:
        data = json.load(f)

    summary = data.get("summary", {})
    violations = data.get("violations", [])

    # Count violations by rule
    rule_counts = {}
    for violation in violations:
        rule_id = violation.get("rule_id", "unknown")
        rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1

    return {
        "total_violations": len(violations),
        "error_count": summary.get("error_count", 0),
        "warning_count": summary.get("warning_count", 0),
        "quality_score": summary.get("quality_score", 0),
        "spi005_count": rule_counts.get("SPI005", 0),
        "spi011_count": rule_counts.get("SPI011", 0),
        "spi010_count": rule_counts.get("SPI010", 0),
        "spi014_count": rule_counts.get("SPI014", 0),
        "total_protocols": data.get("summary", {}).get("total_protocols", 0),
        "total_files": data.get("summary", {}).get("total_files", 0),
    }


def update_tracking_markdown(tracking_file: Path, metrics: Dict[str, Any]) -> None:
    """Update tracking markdown file with new metrics."""
    with open(tracking_file, "r") as f:
        content = f.read()

    # Update overall progress table
    replacements = {
        r"\| Total Violations \| 380 \| \d+ \|": f'| Total Violations | 380 | {metrics["total_violations"]} |',
        r"\| Error Count \| 34 \| \d+ \|": f'| Error Count | 34 | {metrics["error_count"]} |',
        r"\| Warning Count \| 346 \| \d+ \|": f'| Warning Count | 346 | {metrics["warning_count"]} |',
        r"\| Code Quality Score \| 30\.0% \| [\d.]+% \|": f'| Code Quality Score | 30.0% | {metrics["quality_score"]}% |',
        r"\| SPI005 Errors \| 1 \| \d+ \|": f'| SPI005 Errors | 1 | {metrics["spi005_count"]} |',
        r"\| SPI011 Errors \| 33 \| \d+ \|": f'| SPI011 Errors | 33 | {metrics["spi011_count"]} |',
        r"\| SPI010 Warnings \| 25 \| \d+ \|": f'| SPI010 Warnings | 25 | {metrics["spi010_count"]} |',
        r"\| SPI014 Warnings \| 321 \| \d+ \|": f'| SPI014 Warnings | 321 | {metrics["spi014_count"]} |',
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    # Update status indicators
    # If total violations decreased, update status
    if metrics["total_violations"] < 380:
        content = re.sub(
            r"\| Total Violations \| 380 \| \d+ \| <200 \| 🔴 Not Started \|",
            f'| Total Violations | 380 | {metrics["total_violations"]} | <200 | 🟡 In Progress |',
            content,
        )

    if metrics["error_count"] == 0:
        content = re.sub(
            r"\| Error Count \| 34 \| 0 \| 0 \| 🔴 Not Started \|",
            f"| Error Count | 34 | 0 | 0 | 🟢 Complete |",
            content,
        )

    if metrics["spi005_count"] == 0:
        content = re.sub(
            r"\| SPI005 Errors \| 1 \| 0 \| 0 \| 🔴 Not Started \|",
            f"| SPI005 Errors | 1 | 0 | 0 | 🟢 Complete |",
            content,
        )

    if metrics["spi011_count"] == 0:
        content = re.sub(
            r"\| SPI011 Errors \| 33 \| 0 \| 0 \| 🔴 Not Started \|",
            f"| SPI011 Errors | 33 | 0 | 0 | 🟢 Complete |",
            content,
        )

    if metrics["spi010_count"] == 0:
        content = re.sub(
            r"\| SPI010 Warnings \| 25 \| 0 \| 0 \| 🔴 Not Started \|",
            f"| SPI010 Warnings | 25 | 0 | 0 | 🟢 Complete |",
            content,
        )

    # Update last updated timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = re.sub(
        r"\*\*Last Updated\*\*: .*", f"**Last Updated**: {timestamp}", content
    )

    # Write updated content
    with open(tracking_file, "w") as f:
        f.write(content)


def print_summary(metrics: Dict[str, Any]) -> None:
    """Print summary of current metrics."""
    print("\n" + "=" * 60)
    print("SPI REMEDIATION METRICS SUMMARY")
    print("=" * 60)
    print(f"\nTotal Violations: {metrics['total_violations']}")
    print(f"  Errors:   {metrics['error_count']}")
    print(f"  Warnings: {metrics['warning_count']}")
    print(f"\nCode Quality Score: {metrics['quality_score']}%")
    print(f"\nViolations by Rule:")
    print(f"  SPI005 (Async I/O):        {metrics['spi005_count']}")
    print(f"  SPI011 (Name Conflicts):   {metrics['spi011_count']}")
    print(f"  SPI010 (Duplicates):       {metrics['spi010_count']}")
    print(f"  SPI014 (Documentation):    {metrics['spi014_count']}")
    print(f"\nRepository Stats:")
    print(f"  Total Protocols: {metrics['total_protocols']}")
    print(f"  Total Files:     {metrics['total_files']}")
    print("\n" + "=" * 60)

    # Calculate progress
    errors_resolved = 34 - metrics["error_count"]
    spi011_resolved = 33 - metrics["spi011_count"]
    spi010_resolved = 25 - metrics["spi010_count"]

    print("\nPROGRESS:")
    print(
        f"  Total Errors Resolved:     {errors_resolved}/34 ({errors_resolved/34*100:.1f}%)"
    )
    print(
        f"  SPI011 Conflicts Resolved: {spi011_resolved}/33 ({spi011_resolved/33*100:.1f}%)"
    )
    print(
        f"  SPI010 Duplicates Resolved: {spi010_resolved}/25 ({spi010_resolved/25*100:.1f}%)"
    )
    print("=" * 60 + "\n")


def main():
    """Main execution."""
    base_dir = Path(__file__).parent.parent

    # Find validation file
    if len(sys.argv) > 1 and sys.argv[1] != "--help":
        validation_file = Path(sys.argv[1])
    else:
        validation_file = find_latest_validation_report(base_dir)

    print(f"Using validation report: {validation_file.name}")

    # Extract metrics
    metrics = extract_metrics(validation_file)

    # Print summary
    print_summary(metrics)

    # Update tracking file
    tracking_file = base_dir / "REMEDIATION_TRACKING.md"
    if tracking_file.exists():
        print(f"Updating tracking file: {tracking_file.name}")
        update_tracking_markdown(tracking_file, metrics)
        print("✅ Tracking file updated successfully")
    else:
        print(f"⚠️  Tracking file not found: {tracking_file}")
        print("   Metrics printed above but tracking file not updated.")

    # Return exit code based on errors
    if metrics["error_count"] == 0:
        print("\n✅ All errors resolved!")
        return 0
    else:
        print(f"\n❌ {metrics['error_count']} errors remaining")
        return 1


if __name__ == "__main__":
    sys.exit(main())
