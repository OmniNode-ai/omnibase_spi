#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol Duplication Validation for omnibase_spi

Validates that protocol definitions within omnibase_spi are unique:
1. No duplicate protocol definitions with identical signatures
2. No naming conflicts between protocols
3. Consistent protocol patterns across the SPI
4. Proper protocol organization and distribution

Usage:
    python scripts/validation/validate_protocol_duplicates.py src/
    python scripts/validation/validate_protocol_duplicates.py --generate-report src/
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import timeout_utils
from timeout_utils import timeout_context
from validation_constants import KNOWN_ALLOWED_CONFLICTS


class ProtocolClassification(StrEnum):
    """Known structural classifications for discovered SPI protocols."""

    FUNCTIONAL = "functional"
    MARKER = "marker"
    PROPERTY_ONLY = "property_only"
    MIXIN = "mixin"

    @classmethod
    def parse(cls, value: ProtocolClassification | str) -> ProtocolClassification:
        """Return a known protocol classification or fail clearly."""
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as exc:
            valid = ", ".join(item.value for item in cls)
            raise ValueError(
                f"Unknown protocol classification {value!r}; expected one of: {valid}"
            ) from exc


@dataclass
class ProtocolInfo:
    """Information about a discovered protocol."""

    name: str
    file_path: str
    module_path: str
    methods: list[str]
    signature_hash: str
    line_count: int
    imports: list[str]
    line_number: int
    is_runtime_checkable: bool = False
    domain: str = "unknown"
    properties: list[str] = None
    base_protocols: list[str] = None
    protocol_type: ProtocolClassification = ProtocolClassification.FUNCTIONAL
    docstring: str = ""

    def __post_init__(self):
        if self.properties is None:
            self.properties = []
        if self.base_protocols is None:
            self.base_protocols = []
        self.protocol_type = ProtocolClassification.parse(self.protocol_type)


_PATH_DOMAIN_MAP: dict[str, str] = {
    "workflow_orchestration": "workflow",
    "mcp": "mcp",
    "event_bus": "events",
    "container": "container",
    "core": "core",
    "types": "types",
    "file_handling": "file_handling",
    "validation": "validation",
    "memory": "memory",
}

_NAME_DOMAIN_KEYWORDS: list[tuple[str, str]] = [
    ("workflow", "workflow"),
    ("mcp", "mcp"),
    ("event", "events"),
    ("file", "file_handling"),
    ("node", "core"),
    ("memory", "memory"),
]

# Docstring checks omit "node"→"core" (original behavior)
_DOC_DOMAIN_KEYWORDS: list[tuple[str, str]] = [
    ("workflow", "workflow"),
    ("mcp", "mcp"),
    ("event", "events"),
    ("file", "file_handling"),
    ("memory", "memory"),
]


def _domain_from_path(path_parts: tuple[str, ...]) -> str:
    for part, domain in _PATH_DOMAIN_MAP.items():
        if part in path_parts:
            return domain
    return "unknown"


def _domain_from_name(name: str) -> str:
    lower = name.lower()
    for keyword, domain in _NAME_DOMAIN_KEYWORDS:
        if keyword in lower:
            return domain
    return "unknown"


def _domain_from_docstring(docstring: str) -> str:
    if not docstring:
        return "unknown"
    lower = docstring.lower()
    for keyword, domain in _DOC_DOMAIN_KEYWORDS:
        if keyword in lower:
            return domain
    return "unknown"


def _determine_protocol_domain(
    file_path: str, protocol_name: str = "", docstring: str = ""
) -> str:
    domain = _domain_from_path(Path(file_path).parts)
    if domain != "unknown":
        return domain
    if protocol_name:
        domain = _domain_from_name(protocol_name)
        if domain != "unknown":
            return domain
    return _domain_from_docstring(docstring)


def _determine_protocol_type(
    methods: list[str],
    properties: list[str],
    base_protocols: list[str],
) -> ProtocolClassification:
    if not methods and not properties:
        return ProtocolClassification.MARKER
    if not methods and properties:
        return ProtocolClassification.PROPERTY_ONLY
    if methods and not properties and base_protocols:
        return ProtocolClassification.MIXIN
    return ProtocolClassification.FUNCTIONAL


def _get_module_path(file_path: str) -> str:
    path = Path(file_path)
    parts = list(path.parts)
    module_parts = parts[parts.index("src") + 1 :] if "src" in parts else parts
    if module_parts and module_parts[-1].endswith(".py"):
        module_parts[-1] = module_parts[-1][:-3]
    return ".".join(module_parts)


def _hash_docstring(docstring: str) -> str:
    if not docstring:
        return "no_docstring"
    normalized = re.sub(r"\s+", " ", docstring.strip().lower())
    normalized = re.sub(r"protocol for\s+", "", normalized)
    normalized = re.sub(r"protocol that\s+", "", normalized)
    return hashlib.md5(normalized.encode()).hexdigest()[:8]


def _build_method_signature(node: ast.FunctionDef) -> str:
    args = [
        f"{arg.arg}: {ast.unparse(arg.annotation) if arg.annotation else 'Any'}"
        for arg in node.args.args
        if arg.arg != "self"
    ]
    returns = ast.unparse(node.returns) if node.returns else "None"
    return f"{node.name}({', '.join(args)}) -> {returns}"


def _build_async_method_signature(node: ast.AsyncFunctionDef) -> str:
    args = [
        f"{arg.arg}: {ast.unparse(arg.annotation) if arg.annotation else 'Any'}"
        for arg in node.args.args
        if arg.arg != "self"
    ]
    returns = ast.unparse(node.returns) if node.returns else "None"
    return f"async {node.name}({', '.join(args)}) -> {returns}"


def _extract_docstring(node: ast.ClassDef) -> str:
    if (
        node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    ):
        return node.body[0].value.value
    return ""


def _extract_base_protocols(node: ast.ClassDef) -> list[str]:
    base_protocols = []
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id != "Protocol":
            base_protocols.append(base.id)
        elif (
            isinstance(base, ast.Attribute) and base.attr != "Protocol"
        ) or isinstance(base, ast.Subscript):
            base_protocols.append(ast.unparse(base))
    return base_protocols


def _extract_body_members(node: ast.ClassDef) -> tuple[list[str], list[str]]:
    methods: list[str] = []
    properties: list[str] = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            methods.append(_build_method_signature(item))
        elif isinstance(item, ast.AsyncFunctionDef):
            methods.append(_build_async_method_signature(item))
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            prop_type = ast.unparse(item.annotation) if item.annotation else "Any"
            properties.append(f"{item.target.id}: {prop_type}")
    return methods, properties


def _build_signature_hash(
    name: str,
    domain: str,
    protocol_type: ProtocolClassification,
    methods: list[str],
    properties: list[str],
    base_protocols: list[str],
    docstring: str,
) -> str:
    components = [f"name:{name}", f"domain:{domain}", f"type:{protocol_type.value}"]
    if methods:
        components.append(f"methods:{':'.join(sorted(methods))}")
    if properties:
        components.append(f"properties:{':'.join(sorted(properties))}")
    if base_protocols:
        components.append(f"bases:{':'.join(sorted(base_protocols))}")
    if docstring:
        components.append(f"doc:{_hash_docstring(docstring)}")
    return hashlib.sha256("|".join(components).encode()).hexdigest()[:16]


class ProtocolExtractor(ast.NodeVisitor):
    """Extracts protocol information from AST."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.protocols: list[ProtocolInfo] = []
        self.imports: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Extract imports."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Extract from imports."""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract protocol class definitions."""
        is_protocol = self._is_protocol_class(node)
        if is_protocol and node.name.startswith("Protocol"):
            protocol_info = self._extract_protocol_info(node)
            if protocol_info:
                self.protocols.append(protocol_info)
        self.generic_visit(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a Protocol class."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def _extract_protocol_info(self, node: ast.ClassDef) -> ProtocolInfo | None:
        """Extract enhanced protocol information with properties, inheritance, and better hashing."""
        try:
            docstring = _extract_docstring(node)
            base_protocols = _extract_base_protocols(node)
            methods, properties = _extract_body_members(node)

            protocol_type = _determine_protocol_type(
                methods, properties, base_protocols
            )
            domain = _determine_protocol_domain(self.file_path, node.name, docstring)
            signature_hash = _build_signature_hash(
                node.name,
                domain,
                protocol_type,
                methods,
                properties,
                base_protocols,
                docstring,
            )

            is_runtime_checkable = any(
                (isinstance(d, ast.Name) and d.id == "runtime_checkable")
                or (isinstance(d, ast.Attribute) and d.attr == "runtime_checkable")
                for d in node.decorator_list
            )

            return ProtocolInfo(
                name=node.name,
                file_path=self.file_path,
                module_path=_get_module_path(self.file_path),
                methods=methods,
                signature_hash=signature_hash,
                line_count=len(methods) + len(properties),
                imports=self.imports.copy(),
                line_number=node.lineno,
                is_runtime_checkable=is_runtime_checkable,
                domain=domain,
                properties=properties,
                base_protocols=base_protocols,
                protocol_type=protocol_type,
                docstring=docstring,
            )

        except Exception as e:
            print(f"⚠️  Error extracting protocol info from {self.file_path}: {e}")
            return None

    def _get_method_signature(self, node: ast.FunctionDef) -> str:
        """Get method signature string for comparison."""
        return _build_method_signature(node)

    def _get_async_method_signature(self, node: ast.AsyncFunctionDef) -> str:
        """Get async method signature string for comparison."""
        return _build_async_method_signature(node)


def find_all_protocols(base_path: Path) -> list[ProtocolInfo]:
    """Find all protocols in the specified directory."""
    protocols = []

    try:
        with timeout_context("protocol_discovery"):
            for py_file in base_path.rglob("*.py"):
                # Skip test files, __init__.py, and __pycache__
                if (
                    py_file.name.startswith("test_")
                    or py_file.name == "__init__.py"
                    or "__pycache__" in str(py_file)
                    or py_file.name.startswith("_")
                ):
                    continue

                # Only check files that are likely to contain protocols
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Quick check if file contains Protocol definitions
                    if "Protocol" in content and "class " in content:
                        tree = ast.parse(content)
                        extractor = ProtocolExtractor(str(py_file))
                        extractor.visit(tree)
                        protocols.extend(extractor.protocols)

                except Exception as e:
                    print(f"⚠️  Error processing {py_file}: {e}")
                    continue

    except timeout_utils.TimeoutError:
        print("❌ Protocol discovery timeout")
        raise
    except Exception as e:
        print(f"❌ Error during protocol discovery: {e}")
        raise

    return protocols


def _group_protocols(
    protocols: list[ProtocolInfo],
) -> tuple[
    dict[str, list[ProtocolInfo]],
    dict[str, list[ProtocolInfo]],
    dict[str, list[ProtocolInfo]],
    dict[str, list[ProtocolInfo]],
]:
    """Group protocols by signature, name, domain, and type."""
    by_signature: dict[str, list[ProtocolInfo]] = defaultdict(list)
    by_name: dict[str, list[ProtocolInfo]] = defaultdict(list)
    by_domain: dict[str, list[ProtocolInfo]] = defaultdict(list)
    by_type: dict[str, list[ProtocolInfo]] = defaultdict(list)
    for protocol in protocols:
        by_signature[protocol.signature_hash].append(protocol)
        by_name[protocol.name].append(protocol)
        by_domain[protocol.domain].append(protocol)
        by_type[protocol.protocol_type.value].append(protocol)
    return by_signature, by_name, by_domain, by_type


def _find_actual_duplicates(
    by_signature: dict[str, list[ProtocolInfo]],
) -> dict[str, list[ProtocolInfo]]:
    actual: dict[str, list[ProtocolInfo]] = {}
    for sig_hash, group in by_signature.items():
        if len(group) > 1:
            real = _filter_real_duplicates(group)
            if len(real) > 1:
                actual[sig_hash] = real
    return actual


def _find_actual_conflicts(
    by_name: dict[str, list[ProtocolInfo]],
) -> dict[str, list[ProtocolInfo]]:
    actual: dict[str, list[ProtocolInfo]] = {}
    for name, group in by_name.items():
        if len(group) <= 1:
            continue
        if len({p.signature_hash for p in group}) <= 1:
            continue
        real = _filter_real_conflicts(group)
        if len(real) > 1:
            actual[name] = real
    return actual


def _build_domain_distribution(
    by_domain: dict[str, list[ProtocolInfo]],
) -> dict[str, Any]:
    distribution: dict[str, Any] = {}
    for domain, domain_protocols in by_domain.items():
        type_dist: dict[str, int] = defaultdict(int)
        for p in domain_protocols:
            type_dist[p.protocol_type.value] += 1
        n = len(domain_protocols)
        distribution[domain] = {
            "count": n,
            "protocols": [p.name for p in domain_protocols],
            "runtime_checkable_ratio": sum(
                1 for p in domain_protocols if p.is_runtime_checkable
            )
            / n
            if n
            else 0,
            "type_distribution": dict(type_dist),
            "avg_properties": sum(len(p.properties) for p in domain_protocols) / n
            if n
            else 0,
            "avg_methods": sum(len(p.methods) for p in domain_protocols) / n
            if n
            else 0,
        }
    return distribution


def analyze_duplicates(protocols: list[ProtocolInfo]) -> dict[str, Any]:
    """Analyze protocols for duplicates and conflicts with enhanced detection."""
    by_signature, by_name, by_domain, by_type = _group_protocols(protocols)
    return {
        "exact_duplicates": _find_actual_duplicates(by_signature),
        "name_conflicts": _find_actual_conflicts(by_name),
        "distribution_analysis": _build_domain_distribution(by_domain),
        "total_protocols": len(protocols),
        "protocols_by_domain": by_domain,
        "protocols_by_type": by_type,
        "quality_metrics": _analyze_quality_metrics(protocols),
    }


def _are_semantically_different(p1: ProtocolInfo, p2: ProtocolInfo) -> bool:
    """Check if two protocols with similar names are semantically different.

    Args:
        p1: First protocol to compare
        p2: Second protocol to compare

    Returns:
        True if protocols are semantically different, False if they're likely duplicates
    """
    # Check 1: Different method names indicate different purposes
    p1_methods = {m.split("(")[0] for m in p1.methods}
    p2_methods = {m.split("(")[0] for m in p2.methods}

    if p1_methods != p2_methods:
        return True  # Different operations = different protocols

    # Check 2: Check for "Batch" vs singular patterns
    if "Batch" in p1.name and "Batch" not in p2.name:
        return True  # Batch operations are semantically different from singular
    if "Batch" in p2.name and "Batch" not in p1.name:
        return True

    # Check 3: Different property sets indicate different data models
    p1_props = set(p1.properties)
    p2_props = set(p2.properties)

    if p1_props != p2_props:
        # Check if it's a meaningful difference (not just additions)
        if len(p1_props.symmetric_difference(p2_props)) >= 2:
            return True  # Significantly different data models

    # Check 4: Different architectural layers (e.g., "Workflow" vs "Onex")
    layer_keywords = [
        "Workflow",
        "Onex",
        "Node",
        "Agent",
        "Service",
        "Memory",
        "Event",
        "MCP",
    ]
    p1_layers = [kw for kw in layer_keywords if kw in p1.name]
    p2_layers = [kw for kw in layer_keywords if kw in p2.name]

    if p1_layers != p2_layers:
        return True  # Different architectural layers

    # Check 5: Different domains indicate different contexts
    if p1.domain != p2.domain and p1.domain != "unknown" and p2.domain != "unknown":
        return True  # Different domains usually mean different purposes

    # Check 6: Different protocol types indicate different usage patterns
    if p1.protocol_type != p2.protocol_type:
        return True  # Different structural patterns

    return False  # Likely true duplicates


def _filter_real_duplicates(protocols: list[ProtocolInfo]) -> list[ProtocolInfo]:
    """Filter out false positive duplicates based on enhanced protocol analysis."""
    if not protocols or len(protocols) < 2:
        return protocols

    # First check for semantic differences - if any pair is semantically different, no duplicates
    for i, p1 in enumerate(protocols):
        for p2 in protocols[i + 1 :]:
            if _are_semantically_different(p1, p2):
                # Found semantic differences, these are not duplicates
                return []

    # If we get here, no semantic differences were found, proceed with existing logic
    # Group by domain and type - protocols in same domain with same structure are more likely real duplicates
    by_domain_type = defaultdict(list)
    for protocol in protocols:
        key = (protocol.domain, protocol.protocol_type)
        by_domain_type[key].append(protocol)

    real_duplicates = []
    for (_domain, protocol_type), domain_protocols in by_domain_type.items():
        if len(domain_protocols) > 1:
            # For property-only protocols, check if they have truly identical properties
            if protocol_type is ProtocolClassification.PROPERTY_ONLY:
                property_groups = defaultdict(list)
                for protocol in domain_protocols:
                    prop_key = "|".join(sorted(protocol.properties))
                    property_groups[prop_key].append(protocol)

                for prop_protocols in property_groups.values():
                    if len(prop_protocols) > 1:
                        real_duplicates.extend(prop_protocols)
            else:
                # For other types, same domain + type + signature = likely duplicate
                real_duplicates.extend(domain_protocols)

    return real_duplicates if real_duplicates else protocols


def _filter_real_conflicts(protocols: list[ProtocolInfo]) -> list[ProtocolInfo]:
    """Filter out legitimate protocol variations from real naming conflicts."""
    if not protocols or len(protocols) < 2:
        return protocols

    # Skip known allowed conflicts that are documented and intentional
    protocol_name = protocols[0].name if protocols else ""
    if protocol_name in KNOWN_ALLOWED_CONFLICTS:
        return []  # Skip - this is a known, documented conflict

    # If protocols are in different domains with different purposes, they might be legitimate
    domains = {p.domain for p in protocols}
    protocol_types = {p.protocol_type for p in protocols}

    # If all protocols are in different domains, this is likely acceptable variation
    if len(domains) == len(protocols):
        return []  # No conflicts - they're domain-specific variations

    # If protocols have different types and related inheritance, might be acceptable
    if len(protocol_types) > 1:
        # Check if they're related through inheritance
        for p1 in protocols:
            for p2 in protocols:
                if p1 != p2 and (
                    p1.name in p2.base_protocols
                    or p2.name in p1.base_protocols
                    or any(base in p2.base_protocols for base in p1.base_protocols)
                ):
                    return []  # Related protocols, not conflicts

    # Otherwise, these are likely real conflicts
    return protocols


def _analyze_quality_metrics(protocols: list[ProtocolInfo]) -> dict[str, Any]:
    """Analyze overall quality metrics of the protocol collection."""
    if not protocols:
        return {}

    empty_protocols = [p for p in protocols if not p.methods and not p.properties]
    property_only = [p for p in protocols if not p.methods and p.properties]
    functional_protocols = [p for p in protocols if p.methods]
    missing_docstrings = [p for p in protocols if not p.docstring]

    return {
        "empty_protocols": len(empty_protocols),
        "property_only_protocols": len(property_only),
        "functional_protocols": len(functional_protocols),
        "missing_docstrings": len(missing_docstrings),
        "docstring_coverage": (len(protocols) - len(missing_docstrings))
        / len(protocols),
        "avg_properties_per_protocol": sum(len(p.properties) for p in protocols)
        / len(protocols),
        "avg_methods_per_protocol": sum(len(p.methods) for p in protocols)
        / len(protocols),
    }


def _print_domain_distribution(distribution: dict[str, Any]) -> None:
    print("\n📁 PROTOCOL DISTRIBUTION BY DOMAIN:")
    for domain, info in distribution.items():
        checkable_percent = info["runtime_checkable_ratio"] * 100
        print(
            f"   {domain}: {info['count']} protocols ({checkable_percent:.0f}% @runtime_checkable)"
        )
        if info["count"] <= 5:
            print(f"      Protocols: {', '.join(info['protocols'])}")


def _print_exact_duplicates(exact_duplicates: dict[str, list[ProtocolInfo]]) -> None:
    if not exact_duplicates:
        return
    print(f"\n🚨 EXACT DUPLICATES FOUND: {len(exact_duplicates)} groups")
    print("   These protocols have identical signatures and should be merged:")
    for signature_hash, duplicate_protocols in exact_duplicates.items():
        print(f"\n   📋 Signature Hash: {signature_hash}")
        for protocol in duplicate_protocols:
            print(f"      • {protocol.name}")
            print(f"        File: {protocol.file_path}")
            print(f"        Module: {protocol.module_path}")
            print(f"        Domain: {protocol.domain}")
            print(f"        Methods: {len(protocol.methods)}")
            print(
                f"        @runtime_checkable: {'Yes' if protocol.is_runtime_checkable else 'No'}"
            )
        print("      💡 RECOMMENDATION: Keep one version, remove others")
        print("      💡 Consider: Which domain/location is most appropriate?")


def _print_name_conflicts(name_conflicts: dict[str, list[ProtocolInfo]]) -> None:
    if not name_conflicts:
        return
    print(f"\n⚠️  NAME CONFLICTS FOUND: {len(name_conflicts)} conflicts")
    print("   These protocols share names but have different signatures:")
    for name, conflicting_protocols in name_conflicts.items():
        print(f"\n   📋 Protocol Name: {name}")
        for protocol in conflicting_protocols:
            print(f"      • {protocol.file_path}")
            print(f"        Signature: {protocol.signature_hash}")
            print(f"        Domain: {protocol.domain}")
            print(f"        Methods: {len(protocol.methods)}")
        print("      💡 RECOMMENDATION: Rename protocols to be more specific")
        print(
            f"      💡 Consider: Add domain prefix (e.g., WorkflowProtocol{name[8:]})"
        )


def _print_quality_issues(
    protocols: list[ProtocolInfo],
) -> tuple[list[ProtocolInfo], list[ProtocolInfo]]:
    non_checkable = [p for p in protocols if not p.is_runtime_checkable]
    empty_protocols = [p for p in protocols if not p.methods]
    quality_issues = []
    if non_checkable:
        quality_issues.append(
            f"{len(non_checkable)} protocols missing @runtime_checkable"
        )
    if empty_protocols:
        quality_issues.append(f"{len(empty_protocols)} protocols with no methods")
    if quality_issues:
        print("\n📋 QUALITY ISSUES:")
        for issue in quality_issues:
            print(f"   ⚠️  {issue}")
    return non_checkable, empty_protocols


def _print_recommendations(
    exact_duplicates: dict[str, Any],
    name_conflicts: dict[str, Any],
    non_checkable: list[ProtocolInfo],
    empty_protocols: list[ProtocolInfo],
    distribution: dict[str, Any],
) -> None:
    print("\n💡 RECOMMENDATIONS:")
    if not exact_duplicates and not name_conflicts:
        print("   ✅ No duplicates found - excellent protocol organization!")
    else:
        if exact_duplicates:
            print(
                f"   🔧 Resolve {len(exact_duplicates)} exact duplicates by merging or removing"
            )
        if name_conflicts:
            print(
                f"   🏷️  Resolve {len(name_conflicts)} name conflicts with more specific naming"
            )
    if non_checkable:
        print(
            f"   🏃 Add @runtime_checkable to {len(non_checkable)} protocols for isinstance() support"
        )
    if empty_protocols:
        print(f"   📝 Add method signatures to {len(empty_protocols)} empty protocols")
    largest_domain = max(distribution.keys(), key=lambda d: distribution[d]["count"])
    if distribution[largest_domain]["count"] > 10:
        print(
            f"   📁 Consider splitting {largest_domain} domain ({distribution[largest_domain]['count']} protocols)"
        )


def print_duplication_report(
    analysis: dict[str, Any], protocols: list[ProtocolInfo]
) -> None:
    """Print comprehensive duplication analysis report."""
    print("\n" + "=" * 80)
    print("🔍 SPI PROTOCOL DUPLICATION ANALYSIS")
    print("=" * 80)

    exact_duplicates = analysis["exact_duplicates"]
    name_conflicts = analysis["name_conflicts"]
    distribution = analysis["distribution_analysis"]

    print("\n📊 PROTOCOL INVENTORY:")
    print(f"   Total protocols: {analysis['total_protocols']}")

    _print_domain_distribution(distribution)
    _print_exact_duplicates(exact_duplicates)
    _print_name_conflicts(name_conflicts)
    non_checkable, empty_protocols = _print_quality_issues(protocols)
    _print_recommendations(
        exact_duplicates, name_conflicts, non_checkable, empty_protocols, distribution
    )


def generate_migration_plan(analysis: dict[str, Any]) -> dict[str, Any]:
    """Generate actionable migration plan for resolving duplicates."""
    plan = {"exact_duplicates": [], "name_conflicts": [], "quality_improvements": []}

    # Handle exact duplicates
    for _signature_hash, duplicate_protocols in analysis["exact_duplicates"].items():
        primary = duplicate_protocols[0]  # Keep first as primary
        plan["exact_duplicates"].append(
            {
                "action": "remove_duplicates",
                "keep": {
                    "protocol": primary.name,
                    "file": primary.file_path,
                    "reason": "Primary protocol definition",
                },
                "remove": [
                    {
                        "protocol": p.name,
                        "file": p.file_path,
                        "reason": f"Duplicate of {primary.name}",
                    }
                    for p in duplicate_protocols[1:]
                ],
            }
        )

    # Handle name conflicts
    for name, conflicting_protocols in analysis["name_conflicts"].items():
        plan["name_conflicts"].append(
            {
                "action": "resolve_naming",
                "conflicts": [
                    {
                        "protocol": p.name,
                        "file": p.file_path,
                        "suggested_name": f"Protocol{p.domain.title()}{name[8:]}",
                        "domain": p.domain,
                    }
                    for p in conflicting_protocols
                ],
            }
        )

    return plan


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate SPI protocol duplicates")
    parser.add_argument("path", nargs="?", default="src/", help="Path to validate")
    parser.add_argument(
        "--generate-report", action="store_true", help="Generate detailed JSON report"
    )
    parser.add_argument(
        "--generate-plan", action="store_true", help="Generate migration plan"
    )

    args = parser.parse_args()

    try:
        base_path = Path(args.path)

        if not base_path.exists():
            print(f"❌ Path does not exist: {base_path}")
            return 1

        print(f"🔍 Analyzing protocol duplicates in: {base_path}")

        # Find all protocols
        protocols = find_all_protocols(base_path)

        if not protocols:
            print("✅ No protocols found to validate")
            return 0

        print(f"📁 Found {len(protocols)} protocols to analyze")

        # Analyze for duplicates
        analysis = analyze_duplicates(protocols)

        # Print report
        print_duplication_report(analysis, protocols)

        # Generate detailed report if requested
        if args.generate_report:
            report_data = {
                "analysis": analysis,
                "protocols": [
                    {
                        "name": p.name,
                        "file_path": p.file_path,
                        "module_path": p.module_path,
                        "signature_hash": p.signature_hash,
                        "domain": p.domain,
                        "method_count": len(p.methods),
                        "is_runtime_checkable": p.is_runtime_checkable,
                    }
                    for p in protocols
                ],
            }

            with open("spi_protocol_analysis.json", "w") as f:
                json.dump(report_data, f, indent=2, default=str)
            print("\n💾 Detailed analysis saved to: spi_protocol_analysis.json")

        # Generate migration plan if requested
        if args.generate_plan:
            plan = generate_migration_plan(analysis)
            with open("spi_protocol_migration_plan.json", "w") as f:
                json.dump(plan, f, indent=2, default=str)
            print("💾 Migration plan saved to: spi_protocol_migration_plan.json")

        # Exit codes for CI
        exact_dupes = len(analysis["exact_duplicates"])
        name_conflicts = len(analysis["name_conflicts"])

        if exact_dupes > 0 or name_conflicts > 0:
            print(
                f"\n🚨 VALIDATION FAILED: {exact_dupes} duplicates, {name_conflicts} conflicts"
            )
            return 1
        print("\n✅ VALIDATION PASSED: No duplicates detected")
        return 0

    except timeout_utils.TimeoutError:
        print("❌ Validation timeout")
        return 1
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
