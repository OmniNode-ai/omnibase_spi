# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Duplicate protocol detection with conflict resolution strategies."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .config import ValidationConfig
from .models import ProtocolInfo, ProtocolViolation


class DuplicateProtocolAnalyzer:
    def __init__(self, config: ValidationConfig):
        self.config = config

    def analyze_duplicates(
        self, protocols: list[ProtocolInfo]
    ) -> list[ProtocolViolation]:
        by_signature: dict[str, list[ProtocolInfo]] = defaultdict(list)
        by_name: dict[str, list[ProtocolInfo]] = defaultdict(list)
        by_semantic: dict[str, list[ProtocolInfo]] = defaultdict(list)

        for protocol in protocols:
            by_signature[protocol.signature_hash].append(protocol)
            by_name[protocol.name].append(protocol)
            by_semantic[self._get_semantic_key(protocol)].append(protocol)

        violations: list[ProtocolViolation] = []
        violations.extend(self._find_exact_duplicates(by_signature))
        violations.extend(self._find_name_conflicts(by_name))
        violations.extend(self._find_semantic_duplicates(by_semantic))
        return violations

    # -------------------------------------------------------------------------

    def _find_exact_duplicates(
        self, by_signature: dict[str, list[ProtocolInfo]]
    ) -> list[ProtocolViolation]:
        violations = []
        for _, duplicate_protocols in by_signature.items():
            if len(duplicate_protocols) <= 1:
                continue
            for group in self._group_truly_identical_protocols(duplicate_protocols):
                if len(group) <= 1:
                    continue
                primary = group[0]
                for duplicate in group[1:]:
                    if (
                        duplicate.name == primary.name
                        and self._are_protocols_truly_identical(duplicate, primary)
                    ):
                        violations.append(
                            ProtocolViolation(
                                file_path=duplicate.file_path,
                                line_number=duplicate.line_number,
                                column_offset=0,
                                rule_id="SPI010",
                                violation_type="Exact Duplicate Protocol",
                                message=f"Protocol '{duplicate.name}' is identical to '{primary.name}' in {primary.file_path}",
                                severity="error",
                                suggestion=f"Remove duplicate or merge with {primary.file_path}:{primary.line_number}",
                                tags=["duplicate", "exact", "signature"],
                                performance_impact="medium",
                            )
                        )
        return violations

    def _group_truly_identical_protocols(
        self, protocols: list[ProtocolInfo]
    ) -> list[list[ProtocolInfo]]:
        groups: list[list[ProtocolInfo]] = []
        processed: set[int] = set()
        for i, protocol in enumerate(protocols):
            if i in processed:
                continue
            group = [protocol]
            processed.add(i)
            for j, other in enumerate(protocols[i + 1 :], i + 1):
                if j in processed:
                    continue
                if self._are_protocols_truly_identical(protocol, other):
                    group.append(other)
                    processed.add(j)
            if len(group) > 1:
                groups.append(group)
        return groups

    def _are_protocols_truly_identical(
        self, p1: ProtocolInfo, p2: ProtocolInfo
    ) -> bool:
        if p1.name != p2.name:
            return False
        if set(p1.methods) != set(p2.methods):
            return False
        if set(p1.properties) != set(p2.properties):
            return False
        return set(p1.async_methods) == set(p2.async_methods)

    # -------------------------------------------------------------------------

    _MIGRATION_DIRECTORIES = {"nodes", "handlers", "registry", "contracts"}

    def _find_name_conflicts(
        self, by_name: dict[str, list[ProtocolInfo]]
    ) -> list[ProtocolViolation]:
        violations = []
        for name, conflicting in by_name.items():
            if len(conflicting) <= 1:
                continue
            unique_sigs = {p.signature_hash for p in conflicting}
            if len(unique_sigs) <= 1:
                continue
            # Allow intentional migration-path duplicates
            dirs_involved = set()
            for p in conflicting:
                parts = Path(p.file_path).parts
                if "protocols" in parts:
                    idx = parts.index("protocols")
                    if idx + 1 < len(parts):
                        dirs_involved.add(parts[idx + 1])
            if dirs_involved & self._MIGRATION_DIRECTORIES:
                continue
            primary = conflicting[0]
            for conflict in conflicting[1:]:
                violations.append(
                    ProtocolViolation(
                        file_path=conflict.file_path,
                        line_number=conflict.line_number,
                        column_offset=0,
                        rule_id="SPI011",
                        violation_type="Protocol Name Conflict",
                        message=f"Protocol '{conflict.name}' conflicts with different protocol in {primary.file_path}",
                        severity="error",
                        suggestion=f"Rename to 'Protocol{conflict.domain.title()}{name[8:]}' or merge interfaces",
                        tags=["conflict", "naming", "signature"],
                        performance_impact="low",
                    )
                )
        return violations

    # -------------------------------------------------------------------------

    def _find_semantic_duplicates(
        self, by_semantic: dict[str, list[ProtocolInfo]]
    ) -> list[ProtocolViolation]:
        violations = []
        exclusions = self._get_rule_exclusions("SPI010")
        for _, similar in by_semantic.items():
            if len(similar) <= 1:
                continue
            score = self._calculate_similarity_score(similar)
            if score <= 0.8:
                continue
            primary = similar[0]
            for other in similar[1:]:
                if self._matches_exclusion_pattern(
                    primary.name, other.name, exclusions
                ):
                    continue
                violations.append(
                    ProtocolViolation(
                        file_path=other.file_path,
                        line_number=other.line_number,
                        column_offset=0,
                        rule_id="SPI010",
                        violation_type="Semantic Duplicate Protocol",
                        message=f"Protocol '{other.name}' is very similar to '{primary.name}' (similarity: {score:.1%})",
                        severity="warning",
                        suggestion="Consider merging similar protocols or making differences more explicit",
                        tags=["duplicate", "semantic", "similarity"],
                        performance_impact="low",
                    )
                )
        return violations

    def _get_semantic_key(self, protocol: ProtocolInfo) -> str:
        method_patterns = sorted(
            m.split("(")[0].strip().lower() for m in protocol.methods
        )
        return f"{protocol.domain}:{':'.join(method_patterns[:5])}"

    def _calculate_similarity_score(self, protocols: list[ProtocolInfo]) -> float:
        if len(protocols) < 2:
            return 0.0
        similarities = []
        for i in range(len(protocols)):
            for j in range(i + 1, len(protocols)):
                methods_i = set(protocols[i].methods)
                methods_j = set(protocols[j].methods)
                union = len(methods_i | methods_j)
                intersection = len(methods_i & methods_j)
                similarities.append(intersection / union if union > 0 else 0)
        return sum(similarities) / len(similarities) if similarities else 0.0

    def _get_rule_exclusions(self, rule_id: str) -> list[dict[str, Any]]:
        if rule_id not in self.config.rules:
            return []
        rule = self.config.rules[rule_id]
        config_data = rule.configuration if hasattr(rule, "configuration") else {}
        return config_data.get("exclusions", [])

    def _matches_exclusion_pattern(
        self,
        name1: str,
        name2: str,
        exclusions: list[dict[str, Any]],
    ) -> bool:
        for exclusion in exclusions:
            pattern = exclusion.get("pattern", "")
            if not pattern:
                continue
            c1 = f"{name1} vs {name2}"
            c2 = f"{name2} vs {name1}"
            try:
                if re.match(pattern, c1) or re.match(pattern, c2):
                    return True
            except re.error:
                continue
        return False
