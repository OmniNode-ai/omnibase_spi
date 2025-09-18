#!/usr/bin/env python3
"""
SPI Protocol Auditor - Specialized for omnibase_spi validation.

This is a copy of omnibase_core validation logic adapted for SPI use.
Since SPI cannot depend on omnibase_core, this provides standalone validation.
"""

import ast
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypedDict, cast


class DuplicateProtocolInfo(TypedDict):
    """Type definition for duplicate protocol information."""

    signature_hash: str
    protocols: list["ProtocolInfo"]
    recommendation: str


@dataclass
class ProtocolInfo:
    """Information about a discovered protocol."""

    name: str
    file_path: str
    repository: str
    methods: list[str]
    signature_hash: str
    line_count: int
    imports: list[str]


@dataclass
class AuditResult:
    """Result of protocol audit operation."""

    success: bool
    repository: str
    protocols_found: int
    duplicates_found: int
    conflicts_found: int
    violations: list[str]
    recommendations: list[str]
    execution_time_ms: int = 0

    def has_issues(self) -> bool:
        """Check if audit found any issues."""
        return (
            self.duplicates_found > 0
            or self.conflicts_found > 0
            or len(self.violations) > 0
        )


class ProtocolSignatureExtractor(ast.NodeVisitor):
    """Extracts protocol signature for comparison."""

    def __init__(self) -> None:
        self.methods: list[str] = []
        self.imports: list[str] = []
        self.class_name = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract class definition."""
        if node.name.startswith("Protocol"):
            self.class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Extract method signature
                    args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                    returns = ast.unparse(item.returns) if item.returns else "None"
                    signature = f"{item.name}({', '.join(args)}) -> {returns}"
                    self.methods.append(signature)
                elif isinstance(item, ast.Expr) and isinstance(
                    item.value, ast.Constant
                ):
                    # Skip docstrings and ellipsis
                    continue
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Extract imports."""
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Extract from imports."""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")


def extract_protocol_signature(file_path: Path) -> Optional[ProtocolInfo]:
    """Extract protocol signature from Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)

        extractor = ProtocolSignatureExtractor()
        extractor.visit(tree)

        if not extractor.class_name or not extractor.methods:
            return None

        # Create signature hash from methods using SHA256 for better security
        methods_str = "|".join(sorted(extractor.methods))
        signature_hash = hashlib.sha256(methods_str.encode()).hexdigest()[:16]

        return ProtocolInfo(
            name=extractor.class_name,
            file_path=str(file_path),
            repository="omnibase_spi",
            methods=extractor.methods,
            signature_hash=signature_hash,
            line_count=len(content.splitlines()),
            imports=extractor.imports,
        )

    except Exception as e:
        # Silently skip files that can't be parsed
        return None


def is_protocol_file(file_path: Path) -> bool:
    """Check if file likely contains protocols."""
    try:
        # Check filename
        if "protocol" in file_path.name.lower() or file_path.name.startswith(
            "protocol_"
        ):
            return True

        # Check file content (first 1000 chars for performance)
        content_sample = file_path.read_text(encoding="utf-8", errors="ignore")[:1000]
        return "class Protocol" in content_sample

    except Exception:
        return False


def find_protocol_files(directory: Path) -> list[Path]:
    """Find all files that likely contain protocols."""
    protocol_files: list[Path] = []

    if not directory.exists():
        return protocol_files

    for py_file in directory.rglob("*.py"):
        if is_protocol_file(py_file):
            protocol_files.append(py_file)

    return protocol_files


def extract_protocols_from_directory(directory: Path) -> list[ProtocolInfo]:
    """Extract all protocols from a directory."""
    protocols = []

    for protocol_file in find_protocol_files(directory):
        protocol_info = extract_protocol_signature(protocol_file)
        if protocol_info:
            protocols.append(protocol_info)

    return protocols


class SPIProtocolAuditor:
    """
    SPI-specific protocol auditor.

    Validates protocols within omnibase_spi for:
    - Internal consistency
    - Duplicate detection
    - Naming convention compliance
    - SPI-specific quality checks
    """

    def __init__(self, spi_path: str = "."):
        self.spi_path = Path(spi_path).resolve()

    def audit_spi_protocols(self) -> AuditResult:
        """
        Audit all protocols in omnibase_spi.

        Checks for:
        - Duplicate protocols within SPI
        - Naming convention violations
        - SPI-specific quality issues
        - Category organization consistency
        """
        protocols_path = self.spi_path / "src" / "omnibase_spi" / "protocols"
        violations = []
        recommendations = []

        if not protocols_path.exists():
            return AuditResult(
                success=False,
                repository="omnibase_spi",
                protocols_found=0,
                duplicates_found=0,
                conflicts_found=0,
                violations=["No protocols directory found in SPI"],
                recommendations=[
                    "Create src/omnibase_spi/protocols/ directory structure"
                ],
            )

        # Extract all SPI protocols
        protocols = extract_protocols_from_directory(protocols_path)

        # Check for internal duplicates
        local_duplicates = self._find_local_duplicates(protocols)

        # Check SPI-specific naming conventions
        naming_violations = self._check_spi_naming_conventions(protocols)

        # Check category organization
        category_issues = self._check_category_organization(protocols)

        # Check SPI-specific quality
        quality_issues = self._check_spi_quality(protocols)

        violations.extend(naming_violations)
        violations.extend(category_issues)
        violations.extend(quality_issues)

        if local_duplicates:
            violations.extend(
                [
                    f"Internal SPI duplicate: {dup['protocols'][0].name}"
                    for dup in local_duplicates
                ]
            )

        # Generate SPI-specific recommendations
        if protocols:
            recommendations.append(
                f"SPI contains {len(protocols)} protocols across categories"
            )

        if not violations:
            recommendations.append("SPI protocol organization is clean and consistent")

        return AuditResult(
            success=len(violations) == 0,
            repository="omnibase_spi",
            protocols_found=len(protocols),
            duplicates_found=len(local_duplicates),
            conflicts_found=0,
            violations=violations,
            recommendations=recommendations,
        )

    def _find_local_duplicates(
        self, protocols: list[ProtocolInfo]
    ) -> list[DuplicateProtocolInfo]:
        """Find duplicate protocols within SPI."""
        duplicates: list[DuplicateProtocolInfo] = []
        by_signature = defaultdict(list)

        for protocol in protocols:
            by_signature[protocol.signature_hash].append(protocol)

        for signature_hash, protocol_group in by_signature.items():
            if len(protocol_group) > 1:
                duplicate_info = cast(
                    DuplicateProtocolInfo,
                    {
                        "signature_hash": signature_hash,
                        "protocols": protocol_group,
                        "recommendation": f"Merge duplicate {protocol_group[0].name} protocols",
                    },
                )
                duplicates.append(duplicate_info)

        return duplicates

    def _check_spi_naming_conventions(self, protocols: list[ProtocolInfo]) -> list[str]:
        """Check SPI-specific naming conventions."""
        violations = []

        for protocol in protocols:
            # Check protocol name starts with Protocol
            if not protocol.name.startswith("Protocol"):
                violations.append(
                    f"SPI protocol {protocol.name} should start with 'Protocol'"
                )

            # Check file name follows protocol_*.py pattern
            file_path = Path(protocol.file_path)
            if not file_path.name.startswith("protocol_"):
                violations.append(
                    f"SPI file {file_path.name} should follow protocol_*.py naming"
                )

            # Check protocol is in appropriate category directory
            expected_categories = [
                "core",
                "agent",
                "workflow",
                "file_handling",
                "event_bus",
                "monitoring",
                "integration",
                "testing",
                "data",
                "memory",
            ]

            protocol_dir = file_path.parent.name
            if protocol_dir not in expected_categories:
                violations.append(
                    f"Protocol {protocol.name} in unexpected category: {protocol_dir}"
                )

        return violations

    def _check_category_organization(self, protocols: list[ProtocolInfo]) -> list[str]:
        """Check if protocols are organized in appropriate categories."""
        issues = []

        # Group protocols by category
        by_category = defaultdict(list)
        for protocol in protocols:
            category = Path(protocol.file_path).parent.name
            by_category[category].append(protocol)

        # Check for empty categories
        protocols_path = self.spi_path / "src" / "omnibase_spi" / "protocols"
        for category_dir in protocols_path.iterdir():
            if category_dir.is_dir() and category_dir.name not in by_category:
                issues.append(f"Empty protocol category: {category_dir.name}")

        # Check for overpopulated categories
        for category, category_protocols in by_category.items():
            if len(category_protocols) > 10:
                issues.append(
                    f"Category {category} has {len(category_protocols)} protocols - consider splitting"
                )

        return issues

    def _check_spi_quality(self, protocols: list[ProtocolInfo]) -> list[str]:
        """Check SPI-specific quality issues."""
        issues = []

        for protocol in protocols:
            # Check for empty protocols
            if not protocol.methods:
                issues.append(f"SPI protocol {protocol.name} has no methods")

            # Check for overly complex protocols
            if len(protocol.methods) > 15:
                issues.append(
                    f"SPI protocol {protocol.name} has {len(protocol.methods)} methods - consider splitting"
                )

            # Check for SPI import issues
            if any(
                "omniagent" in imp or "omnibase_core" in imp for imp in protocol.imports
            ):
                issues.append(
                    f"SPI protocol {protocol.name} imports non-SPI modules - should be self-contained"
                )

        return issues

    def print_audit_summary(self, result: AuditResult) -> None:
        """Print human-readable SPI audit summary."""
        print(f"\n{'='*60}")
        print(f"🔍 SPI PROTOCOL AUDIT SUMMARY")
        print(f"{'='*60}")

        print(f"\n📊 SPI INVENTORY:")
        print(f"   Protocols found: {result.protocols_found}")
        print(f"   Internal duplicates: {result.duplicates_found}")

        if result.violations:
            print(f"\n🚨 SPI VIOLATIONS FOUND ({len(result.violations)}):")
            for violation in result.violations:
                print(f"   • {violation}")

        if result.recommendations:
            print(f"\n💡 SPI RECOMMENDATIONS ({len(result.recommendations)}):")
            for recommendation in result.recommendations:
                print(f"   • {recommendation}")

        status = "✅ SPI CLEAN" if result.success else "❌ SPI ISSUES FOUND"
        print(f"\n{status}")


def main() -> None:
    """Main SPI audit function."""
    import argparse

    parser = argparse.ArgumentParser(description="Audit omnibase_spi protocols")
    parser.add_argument(
        "--spi-path", default=".", help="Path to omnibase_spi repository"
    )

    args = parser.parse_args()

    auditor = SPIProtocolAuditor(args.spi_path)
    result = auditor.audit_spi_protocols()
    auditor.print_audit_summary(result)

    # Exit with appropriate code for CI
    exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
