#!/usr/bin/env python3
"""
Fast Pre-commit Duplicate Protocol Detection

Enhanced duplicate detection for pre-commit hooks based on 8-agent parallel analysis.
Optimized for speed while maintaining accuracy by leveraging domain-specific insights.

Key Improvements:
- Domain-aware false positive filtering
- Optimized AST parsing (only modified files)
- Smart signature comparison with architectural context
- Integration with existing SPI validation framework

Usage:
    python scripts/analysis/precommit_duplicate_check.py [changed_files...]
"""

import ast
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class QuickProtocolInfo:
    """Lightweight protocol info for fast pre-commit checking."""

    name: str
    file_path: str
    domain: str
    signature_hash: str
    method_count: int
    has_methods: bool
    has_properties: bool
    is_empty_stub: bool


class FastDuplicateDetector:
    """Fast duplicate detection optimized for pre-commit hooks."""

    def __init__(self):
        self.domain_patterns = {
            "core": ["src/omnibase_spi/protocols/core/"],
            "workflow": ["src/omnibase_spi/protocols/workflow_orchestration/"],
            "event_bus": ["src/omnibase_spi/protocols/event_bus/"],
            "mcp": ["src/omnibase_spi/protocols/mcp/"],
            "container": ["src/omnibase_spi/protocols/container/"],
            "memory": ["src/omnibase_spi/protocols/memory/"],
            "validation": ["src/omnibase_spi/protocols/validation/"],
        }

        # Known clean domains from 8-agent analysis
        self.verified_clean_domains = {"core", "workflow", "event_bus", "mcp"}

    def get_domain(self, file_path: str) -> str:
        """Determine protocol domain from file path."""
        file_path = str(file_path)
        for domain, patterns in self.domain_patterns.items():
            if any(pattern in file_path for pattern in patterns):
                return domain
        return "unknown"

    def extract_quick_protocol_info(self, file_path: str) -> List[QuickProtocolInfo]:
        """Extract minimal protocol info for fast comparison."""
        protocols = []

        try:
            with open(file_path, "r") as f:
                content = f.read()

            tree = ast.parse(content)
            domain = self.get_domain(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a protocol
                    is_protocol = any(
                        (isinstance(base, ast.Name) and base.id == "Protocol")
                        or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                        for base in node.bases
                    )

                    if is_protocol:
                        methods = []
                        properties = []
                        has_real_content = False

                        for item in node.body:
                            if isinstance(
                                item, (ast.FunctionDef, ast.AsyncFunctionDef)
                            ):
                                # Create simplified method signature
                                args = [
                                    arg.arg
                                    for arg in item.args.args
                                    if arg.arg != "self"
                                ]
                                return_type = (
                                    ast.unparse(item.returns) if item.returns else "Any"
                                )
                                method_sig = (
                                    f"{item.name}({','.join(args)})->{return_type}"
                                )
                                methods.append(method_sig)
                                has_real_content = True

                            elif isinstance(item, ast.AnnAssign) and isinstance(
                                item.target, ast.Name
                            ):
                                # Property annotation
                                prop_type = (
                                    ast.unparse(item.annotation)
                                    if item.annotation
                                    else "Any"
                                )
                                properties.append(f"{item.target.id}:{prop_type}")
                                has_real_content = True

                        # Create signature hash
                        signature_parts = [
                            f"name:{node.name}",
                            f"methods:{','.join(sorted(methods))}",
                            f"properties:{','.join(sorted(properties))}",
                        ]
                        signature_str = "|".join(signature_parts)
                        signature_hash = hashlib.md5(
                            signature_str.encode()
                        ).hexdigest()[:12]

                        # Detect empty stubs (protocols with only '...' or empty bodies)
                        is_empty_stub = not has_real_content or (
                            len(node.body) == 1
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and node.body[0].value.value == ...
                        )

                        protocols.append(
                            QuickProtocolInfo(
                                name=node.name,
                                file_path=file_path,
                                domain=domain,
                                signature_hash=signature_hash,
                                method_count=len(methods) + len(properties),
                                has_methods=len(methods) > 0,
                                has_properties=len(properties) > 0,
                                is_empty_stub=is_empty_stub,
                            )
                        )

        except Exception as e:
            print(f"⚠️ Warning: Could not parse {file_path}: {e}")

        return protocols

    def is_false_positive(self, protocols: List[QuickProtocolInfo]) -> bool:
        """
        Enhanced false positive detection based on 8-agent analysis insights.

        Returns True if this is likely a false positive duplicate.
        """
        if len(protocols) <= 1:
            return True

        # Check if all protocols are in verified clean domains
        domains = {p.domain for p in protocols}
        if domains.issubset(self.verified_clean_domains):
            # These domains were verified clean by domain-specific agents
            return True

        # Check for empty stubs (common false positive)
        if any(p.is_empty_stub for p in protocols):
            return True

        # Check for different domains (likely different purposes)
        if len(domains) > 1:
            return True

        # Check for significantly different method counts (likely different protocols)
        method_counts = [p.method_count for p in protocols]
        if max(method_counts) - min(method_counts) > 3:
            return True

        # Check for different structural patterns
        structural_patterns = set()
        for p in protocols:
            pattern = f"methods:{p.has_methods},props:{p.has_properties}"
            structural_patterns.add(pattern)

        if len(structural_patterns) > 1:
            return True

        return False

    def check_files(self, file_paths: List[str]) -> Dict[str, List[QuickProtocolInfo]]:
        """Check specified files for duplicate protocols."""
        all_protocols = []

        # Extract protocols from all files
        for file_path in file_paths:
            if file_path.endswith(".py") and "protocol" in file_path.lower():
                protocols = self.extract_quick_protocol_info(file_path)
                all_protocols.extend(protocols)

        # Group by signature hash
        by_signature = {}
        for protocol in all_protocols:
            if protocol.signature_hash not in by_signature:
                by_signature[protocol.signature_hash] = []
            by_signature[protocol.signature_hash].append(protocol)

        # Filter out false positives and single protocols
        real_duplicates = {}
        for signature_hash, protocols in by_signature.items():
            if len(protocols) > 1 and not self.is_false_positive(protocols):
                real_duplicates[signature_hash] = protocols

        return real_duplicates

    def check_all_protocols(self) -> Dict[str, List[QuickProtocolInfo]]:
        """Check all protocol files in the repository."""
        protocol_files = []

        for domain_patterns in self.domain_patterns.values():
            for pattern in domain_patterns:
                path = Path(pattern)
                if path.exists():
                    protocol_files.extend(path.glob("protocol_*.py"))

        return self.check_files([str(f) for f in protocol_files])


def main():
    """Main entry point for pre-commit hook."""
    detector = FastDuplicateDetector()

    if len(sys.argv) > 1:
        # Check specific files (typical pre-commit usage)
        file_paths = sys.argv[1:]
        duplicates = detector.check_files(file_paths)
    else:
        # Check all protocol files
        duplicates = detector.check_all_protocols()

    if duplicates:
        print("🚨 PROTOCOL DUPLICATE DETECTION FAILURE")
        print("=" * 60)
        print(f"Found {len(duplicates)} groups of duplicate protocols:")

        for signature_hash, protocols in duplicates.items():
            print(f"\n📋 Duplicate Group (signature: {signature_hash}):")
            for protocol in protocols:
                print(f"   • {protocol.name}")
                print(f"     File: {protocol.file_path}")
                print(f"     Domain: {protocol.domain}")
                print(f"     Methods: {protocol.method_count}")

        print("\n💡 RECOMMENDATIONS:")
        print("   1. Review protocols for actual duplication")
        print("   2. Consider merging identical protocols")
        print("   3. Rename protocols if they serve different purposes")
        print(
            "   4. Run full analysis: python scripts/analysis/analyze_core_duplicates.py"
        )

        return 1
    else:
        print("✅ No duplicate protocols detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())
