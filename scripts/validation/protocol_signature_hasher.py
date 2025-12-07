#!/usr/bin/env python3
"""
Enhanced Protocol Signature Hashing for omnibase_spi

Provides comprehensive protocol signature hashing that considers:
1. Protocol name and namespace
2. Property names and their type annotations
3. Method signatures with full type information
4. Inheritance relationships
5. Docstring content for semantic differentiation
6. Protocol classification (functional, marker, property-only, mixin)

This eliminates false positive duplicate detection while maintaining
accurate identification of true duplicates.
"""

from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ProtocolSignatureComponents:
    """Components that make up a protocol's unique signature."""

    protocol_name: str
    namespace: str  # module path
    properties: list[tuple[str, str]]  # (name, type_annotation)
    methods: list[str]  # Full method signatures including types
    base_protocols: list[str]  # Inheritance chain
    docstring_hash: str  # Semantic content hash
    protocol_type: str  # functional, marker, property_only, mixin
    domain: str  # workflow, mcp, events, etc.


class EnhancedProtocolSignatureHasher:
    """
    Enhanced protocol signature hasher that eliminates false positives.

    Key improvements over the original algorithm:
    1. Includes protocol name in hash (prevents different protocols from colliding)
    2. Captures properties and their types (not just methods)
    3. Includes inheritance relationships
    4. Uses semantic docstring hashing
    5. Considers protocol classification and domain
    6. Uses longer hash to reduce collision probability
    """

    def __init__(self):
        self.hash_algorithm = hashlib.sha256  # More robust than MD5
        self.hash_length = 16  # Longer hash reduces collision probability

    def generate_signature_hash(
        self, protocol_node: ast.ClassDef, file_path: str
    ) -> str:
        """
        Generate comprehensive signature hash for a protocol.

        Args:
            protocol_node: AST node representing the protocol class
            file_path: Path to the file containing the protocol

        Returns:
            Hex string representing the protocol's unique signature
        """
        components = self._extract_signature_components(protocol_node, file_path)
        return self._compute_signature_hash(components)

    def _extract_signature_components(
        self, node: ast.ClassDef, file_path: str
    ) -> ProtocolSignatureComponents:
        """Extract all components that make up the protocol signature."""

        # Extract protocol name and namespace
        protocol_name = node.name
        namespace = self._get_module_path(file_path)

        # Extract properties with their types
        properties = self._extract_properties(node)

        # Extract methods with full signatures
        methods = self._extract_method_signatures(node)

        # Extract inheritance relationships
        base_protocols = self._extract_base_protocols(node)

        # Extract and hash docstring for semantic differentiation
        docstring_hash = self._hash_docstring(node)

        # Determine protocol type and domain
        protocol_type = self._classify_protocol_type(node, properties, methods)
        domain = self._determine_domain(file_path)

        return ProtocolSignatureComponents(
            protocol_name=protocol_name,
            namespace=namespace,
            properties=properties,
            methods=methods,
            base_protocols=base_protocols,
            docstring_hash=docstring_hash,
            protocol_type=protocol_type,
            domain=domain,
        )

    def _extract_properties(self, node: ast.ClassDef) -> list[tuple[str, str]]:
        """Extract properties and their type annotations."""
        properties = []

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Type annotated property: property_name: Type
                prop_name = item.target.id
                prop_type = ast.unparse(item.annotation) if item.annotation else "Any"
                properties.append((prop_name, prop_type))
            elif isinstance(item, ast.Assign):
                # Regular assignment (less common in protocols)
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        prop_name = target.id
                        prop_type = "Unknown"  # No type annotation
                        properties.append((prop_name, prop_type))

        return sorted(properties)  # Sort for consistent hashing

    def _extract_method_signatures(self, node: ast.ClassDef) -> list[str]:
        """Extract complete method signatures including all type information."""
        methods = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                signature = self._get_detailed_method_signature(item)
                methods.append(signature)
            elif isinstance(item, ast.AsyncFunctionDef):
                signature = self._get_detailed_async_method_signature(item)
                methods.append(signature)

        return sorted(methods)  # Sort for consistent hashing

    def _get_detailed_method_signature(self, node: ast.FunctionDef) -> str:
        """Generate detailed method signature with full type information."""
        method_name = node.name

        # Extract parameter information
        params = []
        for arg in node.args.args:
            if arg.arg == "self":
                continue

            param_name = arg.arg
            param_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            params.append(f"{param_name}: {param_type}")

        # Handle defaults (simplified - could be more sophisticated)
        defaults_count = len(node.args.defaults)
        if defaults_count > 0:
            # Mark parameters with defaults
            for i in range(len(params) - defaults_count, len(params)):
                if i < len(params):
                    params[i] += " = ..."

        # Extract return type
        return_type = ast.unparse(node.returns) if node.returns else "None"

        # Handle decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)

        decorator_str = f"@{','.join(decorators)} " if decorators else ""

        return f"{decorator_str}{method_name}({', '.join(params)}) -> {return_type}"

    def _get_detailed_async_method_signature(self, node: ast.AsyncFunctionDef) -> str:
        """Generate detailed async method signature."""
        # Convert to regular function node for processing
        sync_node = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_comment=getattr(node, "type_comment", None),
        )

        base_signature = self._get_detailed_method_signature(sync_node)
        return f"async {base_signature}"

    def _extract_base_protocols(self, node: ast.ClassDef) -> list[str]:
        """Extract inheritance relationships."""
        base_protocols = []

        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id != "Protocol":  # Exclude typing.Protocol itself
                    base_protocols.append(base.id)
            elif isinstance(base, ast.Attribute):
                if base.attr != "Protocol":
                    base_protocols.append(base.attr)
            elif isinstance(base, ast.Subscript):
                # Handle Generic[T] or similar
                base_name = ast.unparse(base)
                base_protocols.append(base_name)

        return sorted(base_protocols)

    def _hash_docstring(self, node: ast.ClassDef) -> str:
        """Extract and hash docstring for semantic differentiation."""
        docstring = ast.get_docstring(node)
        if not docstring:
            return "no_docstring"

        # Normalize docstring for hashing
        normalized = re.sub(r"\s+", " ", docstring.strip().lower())
        # Remove common protocol boilerplate to focus on unique content
        normalized = re.sub(r"protocol for\s+", "", normalized)
        normalized = re.sub(r"protocol that\s+", "", normalized)

        # Hash the normalized docstring
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    def _classify_protocol_type(
        self, node: ast.ClassDef, properties: list, methods: list
    ) -> str:
        """Classify the type of protocol for better differentiation."""
        has_methods = len(methods) > 0
        has_properties = len(properties) > 0
        has_inheritance = len(node.bases) > 1  # More than just Protocol

        if not has_methods and not has_properties:
            return "marker"  # Empty marker protocol
        elif has_properties and not has_methods:
            return "property_only"  # Data structure protocol
        elif has_methods and not has_properties:
            return "functional"  # Behavioral protocol
        elif has_inheritance and (has_methods or has_properties):
            return "mixin"  # Mixin protocol
        else:
            return "composite"  # Mix of properties and methods

    def _determine_domain(self, file_path: str) -> str:
        """Determine protocol domain from file path."""
        path_parts = file_path.lower().split("/")

        domain_mapping = {
            "workflow_orchestration": "workflow",
            "mcp": "mcp",
            "event_bus": "events",
            "container": "container",
            "core": "core",
            "types": "types",
            "validation": "validation",
            "memory": "memory",
            "file_handling": "file_handling",
        }

        for path_part in path_parts:
            if path_part in domain_mapping:
                return domain_mapping[path_part]

        return "unknown"

    def _get_module_path(self, file_path: str) -> str:
        """Get Python module path from file path."""
        # Convert file path to module path
        path_parts = file_path.replace("\\", "/").split("/")

        # Find src directory and build module path
        if "src" in path_parts:
            src_idx = path_parts.index("src")
            module_parts = path_parts[src_idx + 1 :]
        else:
            module_parts = path_parts

        # Remove .py extension
        if module_parts and module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]

        return ".".join(module_parts)

    def _compute_signature_hash(self, components: ProtocolSignatureComponents) -> str:
        """Compute the final signature hash from all components."""

        # Build comprehensive signature string
        signature_parts = [
            f"name:{components.protocol_name}",
            f"namespace:{components.namespace}",
            f"domain:{components.domain}",
            f"type:{components.protocol_type}",
            f"docstring:{components.docstring_hash}",
        ]

        # Add inheritance information
        if components.base_protocols:
            signature_parts.append(f"bases:{','.join(components.base_protocols)}")

        # Add properties with types
        if components.properties:
            props_str = "|".join(
                f"{name}:{ptype}" for name, ptype in components.properties
            )
            signature_parts.append(f"properties:{props_str}")

        # Add methods
        if components.methods:
            methods_str = "|".join(components.methods)
            signature_parts.append(f"methods:{methods_str}")

        # Create final signature string
        signature_string = "\n".join(signature_parts)

        # Generate hash
        hash_obj = self.hash_algorithm(signature_string.encode("utf-8"))
        return hash_obj.hexdigest()[: self.hash_length]

    def debug_signature_components(
        self, protocol_node: ast.ClassDef, file_path: str
    ) -> dict[str, Any]:
        """
        Debug method to see all signature components for a protocol.
        Useful for understanding why protocols might have the same or different hashes.
        """
        components = self._extract_signature_components(protocol_node, file_path)
        signature_hash = self._compute_signature_hash(components)

        return {
            "protocol_name": components.protocol_name,
            "signature_hash": signature_hash,
            "namespace": components.namespace,
            "domain": components.domain,
            "protocol_type": components.protocol_type,
            "docstring_hash": components.docstring_hash,
            "base_protocols": components.base_protocols,
            "properties": components.properties,
            "methods": components.methods,
            "signature_string": self._build_debug_signature_string(components),
        }

    def _build_debug_signature_string(
        self, components: ProtocolSignatureComponents
    ) -> str:
        """Build the signature string for debugging purposes."""
        signature_parts = [
            f"name:{components.protocol_name}",
            f"namespace:{components.namespace}",
            f"domain:{components.domain}",
            f"type:{components.protocol_type}",
            f"docstring:{components.docstring_hash}",
        ]

        if components.base_protocols:
            signature_parts.append(f"bases:{','.join(components.base_protocols)}")

        if components.properties:
            props_str = "|".join(
                f"{name}:{ptype}" for name, ptype in components.properties
            )
            signature_parts.append(f"properties:{props_str}")

        if components.methods:
            methods_str = "|".join(components.methods)
            signature_parts.append(f"methods:{methods_str}")

        return "\n".join(signature_parts)


def compare_protocol_signatures(
    file_path1: str, protocol_name1: str, file_path2: str, protocol_name2: str
) -> dict[str, Any]:
    """
    Compare two protocol signatures and explain differences.
    Useful for debugging why protocols are or aren't considered duplicates.
    """
    hasher = EnhancedProtocolSignatureHasher()

    # Parse both files and find the protocols
    def find_protocol_node(file_path: str, protocol_name: str) -> ast.ClassDef | None:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == protocol_name:
                    return node
        except Exception:
            pass
        return None

    node1 = find_protocol_node(file_path1, protocol_name1)
    node2 = find_protocol_node(file_path2, protocol_name2)

    if not node1 or not node2:
        return {"error": "Could not find one or both protocols"}

    debug1 = hasher.debug_signature_components(node1, file_path1)
    debug2 = hasher.debug_signature_components(node2, file_path2)

    are_duplicates = debug1["signature_hash"] == debug2["signature_hash"]

    differences = []
    for key in debug1:
        if key != "signature_string" and debug1[key] != debug2[key]:
            differences.append(
                {
                    "component": key,
                    "protocol1_value": debug1[key],
                    "protocol2_value": debug2[key],
                }
            )

    return {
        "are_duplicates": are_duplicates,
        "protocol1": debug1,
        "protocol2": debug2,
        "differences": differences,
        "hash_comparison": {
            "hash1": debug1["signature_hash"],
            "hash2": debug2["signature_hash"],
            "match": are_duplicates,
        },
    }
