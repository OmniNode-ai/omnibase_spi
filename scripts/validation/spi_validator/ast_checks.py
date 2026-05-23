# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Pure helper functions for AST inspection — no state, no side effects."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

_ALLOWED_IMPORT_PREFIXES = [
    "typing",
    "typing_extensions",
    "__future__",
    "collections.abc",
    "collections",
    "abc",
    "datetime",
    "uuid",
    "pathlib",
    "enum",
    "dataclasses",
    "decimal",
    "fractions",
    "functools",
    "itertools",
    "operator",
    "contextlib",
    "asyncio",
    "warnings",
    "logging",
    "copy",
    "weakref",
    "types",
    "json",
    "pickle",
    "re",
    "string",
    "os",
    "sys",
    "io",
    "tempfile",
    "time",
    "calendar",
    "math",
    "random",
    "statistics",
    "threading",
    "multiprocessing",
    "concurrent",
    "queue",
    "inspect",
    "traceback",
    "hashlib",
    "base64",
    "secrets",
    "gzip",
    "zipfile",
    "urllib",
    "http",
    "email",
    "omnibase_spi.protocols",
    "omnibase_spi.contracts",
    "omnibase_spi.exceptions",
    "omnibase_core.models",
    "omnibase_core.contracts",
    "omnibase_core.types",
    "omnibase_core.enums",
]

_FORBIDDEN_IMPORT_PREFIXES = ["omnibase_infra"]

_SYNC_EXCEPTIONS = {
    "get_metadata",
    "get_property",
    "get_attribute",
    "get_config",
    "get_default",
    "get_value",
    "get",
    "get_supported_effects",
    "get_available_capability_ids",
    "get_handler_descriptor",
    "get_policy",
    "list_keys",
    "list_handler_descriptors",
    "is_registered",
    "register",
}

_IO_INDICATORS = [
    "read",
    "write",
    "open",
    "close",
    "connect",
    "disconnect",
    "send",
    "receive",
    "get",
    "post",
    "put",
    "delete",
    "fetch",
    "load",
    "save",
    "store",
    "query",
    "execute",
]

_TYPE_ALIAS_PATTERNS = {
    "Literal",
    "Protocol",
    "Union",
    "Optional",
    "Dict",
    "List",
    "Tuple",
    "Set",
    "Type",
    "Callable",
    "Generic",
    "TypeVar",
    "Final",
    "ClassVar",
    "Any",
    "NoReturn",
    "TypeAlias",
}

_ALLOWED_CALLS = {
    "hasattr",
    "isinstance",
    "getattr",
    "setattr",
    "len",
    "TypeVar",
    "Generic",
    "Union",
    "Optional",
    "Literal",
    "get_args",
    "get_origin",
    "runtime_checkable",
    "Protocol",
    "overload",
    "cast",
    "TYPE_CHECKING",
    "ForwardRef",
    "_GenericAlias",
    "_SpecialForm",
}

_ALLOWED_CALLS_IN_CONTAINS_CHECK = {
    "TypeVar",
    "Generic",
    "Union",
    "Optional",
    "Literal",
    "Final",
    "ClassVar",
    "runtime_checkable",
    "Protocol",
}

_ASYNC_RETURN_HINTS = ["response", "connection", "client", "result", "data"]

_UTILITY_PREFIXES = ("_", "get_", "create_", "build_", "make_")


def is_allowed_import(import_name: str) -> bool:
    if any(import_name.startswith(p) for p in _FORBIDDEN_IMPORT_PREFIXES):
        return False
    return any(import_name.startswith(p) for p in _ALLOWED_IMPORT_PREFIXES)


def is_protocol_class(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "Protocol":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "Protocol":
            return True
    return False


def has_ellipsis_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    if not node.body:
        return False
    if (
        len(node.body) == 1
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and node.body[0].value.value is ...
    ):
        return True
    if len(node.body) == 2:
        first_is_docstring = (
            isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )
        second_is_ellipsis = (
            isinstance(node.body[1], ast.Expr)
            and isinstance(node.body[1].value, ast.Constant)
            and node.body[1].value.value is ...
        )
        return first_is_docstring and second_is_ellipsis
    return False


def has_complete_type_annotations(node: ast.FunctionDef) -> bool:
    if not node.returns:
        return False
    return all(arg.annotation for arg in node.args.args[1:])


def class_declares_synchronous_execution(node: ast.ClassDef) -> bool:
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            if item.target.id == "synchronous_execution":
                return True
        elif isinstance(item, ast.Assign):
            for target in item.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "synchronous_execution"
                ):
                    return True
    return False


def should_be_async_method(node: ast.FunctionDef, class_synchronous: bool) -> bool:
    for decorator in node.decorator_list:
        name = ""
        if isinstance(decorator, ast.Name):
            name = decorator.id
        elif isinstance(decorator, ast.Attribute):
            name = decorator.attr
        if name == "property":
            return False

    if class_synchronous:
        return False

    method_name = node.name.lower()
    if method_name in _SYNC_EXCEPTIONS:
        return False

    if any(indicator in method_name for indicator in _IO_INDICATORS):
        return True

    if node.returns:
        return_type = ast.unparse(node.returns)
        if any(hint in return_type.lower() for hint in _ASYNC_RETURN_HINTS):
            return True

    return False


def uses_object_instead_of_callable(node: ast.FunctionDef) -> bool:
    if node.returns:
        return_type = ast.unparse(node.returns)
        if "object" in return_type and any(
            word in node.name.lower()
            for word in ["callback", "handler", "func", "callable"]
        ):
            return True
    for arg in node.args.args:
        if arg.annotation:
            arg_type = ast.unparse(arg.annotation)
            if "object" in arg_type and any(
                word in arg.arg for word in ["callback", "handler", "func"]
            ):
                return True
    return False


def is_type_alias_class(node: ast.ClassDef) -> bool:
    return (
        len(node.bases) == 0
        and len(node.body) <= 2
        and any(isinstance(item, ast.Assign) for item in node.body)
    )


def is_literal_class(node: ast.ClassDef) -> bool:
    return len(node.bases) == 0 and all(
        isinstance(item, ast.Assign | ast.AnnAssign | ast.Expr) for item in node.body
    )


def is_utility_function(node: ast.FunctionDef) -> bool:
    return any(node.name.startswith(p) for p in _UTILITY_PREFIXES)


def get_call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return "unknown_call"


def is_implementation_function_call(node: ast.Call) -> bool:
    call_name = get_call_name(node)
    if call_name in ["...", "Ellipsis", "TYPE_CHECKING"]:
        return False
    return call_name not in _ALLOWED_CALLS


def contains_function_calls(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            call_name = get_call_name(child)
            if call_name not in _ALLOWED_CALLS_IN_CONTAINS_CHECK:
                return True
    return False


def is_complex_implementation_expression(node: ast.AST) -> bool:
    if isinstance(node, ast.BinOp | ast.BoolOp | ast.Compare | ast.IfExp):
        return True
    return bool(
        isinstance(node, ast.ListComp | ast.DictComp | ast.SetComp | ast.GeneratorExp)
    )


def is_type_alias_assignment(var_name: str, value_node: ast.AST) -> bool:
    if var_name.startswith(("Literal", "Protocol", "Type")):
        return True
    if var_name.endswith(
        ("Type", "Types", "Value", "Values", "State", "States", "Status")
    ):
        return True
    if var_name[0].isupper() and any(c.isupper() for c in var_name[1:]):
        return True
    if isinstance(value_node, ast.Subscript):
        if isinstance(value_node.value, ast.Name):
            return value_node.value.id in _TYPE_ALIAS_PATTERNS
        if isinstance(value_node.value, ast.Attribute):
            return value_node.value.attr in _TYPE_ALIAS_PATTERNS
    if isinstance(value_node, ast.Name):
        return value_node.id in _TYPE_ALIAS_PATTERNS or value_node.id[0].isupper()
    if isinstance(value_node, ast.Attribute):
        return value_node.attr in _TYPE_ALIAS_PATTERNS or value_node.attr[0].isupper()
    return False


_ALLOWED_MODULE_ASSIGNMENTS = {
    "version",
    "VERSION",
    "__version__",
    "SCHEMA_VERSION",
    "API_VERSION",
    "__all__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
    "_T",
    "_P",
    "_V",
    "_K",
    "_Return",
    "_Args",
    "_Self",
}

_ALLOWED_MODULE_PREFIXES = {"DEFAULT_", "MAX_", "MIN_", "TIMEOUT_", "CONFIG_"}


def is_allowed_module_assignment(var_name: str, value_node: ast.AST) -> bool:
    if var_name in _ALLOWED_MODULE_ASSIGNMENTS:
        return True
    if any(var_name.startswith(p) for p in _ALLOWED_MODULE_PREFIXES):
        return True
    if isinstance(value_node, ast.Constant):
        if isinstance(value_node.value, str | int | float | bool):
            return True
    return bool(isinstance(value_node, ast.Constant) and value_node.value is None)


def is_spi_implementation_violation(node: ast.Assign, in_protocol_class: bool) -> bool:
    for target in node.targets:
        if isinstance(target, ast.Name):
            if target.id.startswith("__") and target.id.endswith("__"):
                return False
            if target.id.isupper():
                return False
            if is_type_alias_assignment(target.id, node.value):
                return False
            if is_allowed_module_assignment(target.id, node.value):
                return False
    return _is_implementation_logic(node, in_protocol_class)


def _is_implementation_logic(node: ast.Assign, in_protocol_class: bool) -> bool:
    for target in node.targets:
        if isinstance(target, ast.Attribute):
            if (
                isinstance(target.value, ast.Name)
                and target.value.id == "self"
                and in_protocol_class
            ):
                return True
        elif isinstance(target, ast.Subscript):
            return True
    if contains_function_calls(node.value):
        return True
    return bool(is_complex_implementation_expression(node.value))


def get_method_signature(node: ast.FunctionDef) -> str:
    args = []
    for arg in node.args.args:
        if arg.arg != "self":
            arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            args.append(f"{arg.arg}: {arg_type}")
    returns = ast.unparse(node.returns) if node.returns else "None"
    return f"{node.name}({', '.join(args)}) -> {returns}"


def get_async_method_signature(node: ast.AsyncFunctionDef) -> str:
    args = []
    for arg in node.args.args:
        if arg.arg != "self":
            arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
            args.append(f"{arg.arg}: {arg_type}")
    returns = ast.unparse(node.returns) if node.returns else "None"
    return f"async {node.name}({', '.join(args)}) -> {returns}"


def get_module_path(file_path: str) -> str:
    path = Path(file_path)
    parts = list(path.parts)
    if "src" in parts:
        src_idx = parts.index("src")
        module_parts = parts[src_idx + 1 :]
    else:
        module_parts = parts
    if module_parts and module_parts[-1].endswith(".py"):
        module_parts[-1] = module_parts[-1][:-3]
    return ".".join(module_parts)


def determine_domain(file_path: str) -> str:
    path_parts = Path(file_path).parts
    domain_mapping = {
        "workflow_orchestration": "workflow",
        "mcp": "mcp",
        "event_bus": "events",
        "container": "container",
        "core": "core",
        "types": "types",
        "file_handling": "files",
        "discovery": "discovery",
    }
    for part in path_parts:
        if part in domain_mapping:
            return domain_mapping[part]
    return "unknown"


def count_generic_complexity(annotation: ast.AST) -> int:
    return sum(1 for node in ast.walk(annotation) if isinstance(node, ast.Subscript))


def generate_signature_hash(
    protocol_name: str,
    module_path: str,
    file_path: str,
    methods: list[str],
    properties: list[str],
) -> str:
    methods_str = "|".join(sorted(methods))
    props_str = "|".join(sorted(properties))
    combined = f"name:{protocol_name}|module:{module_path}|methods:{methods_str}|props:{props_str}|file:{Path(file_path).name}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]
