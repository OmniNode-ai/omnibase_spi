"""
Protocol for AST Builder functionality.

Defines the interface for building Python Abstract Syntax Tree (AST)
nodes for code generation.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolSchemaDefinition,
    )


@runtime_checkable
class ProtocolASTBuilder(Protocol):
    """Protocol for AST building functionality.

    This protocol defines the interface for generating Python AST
    nodes from schema definitions, used in code generation tools.
    """

    def generate_model_class(
        self,
        class_name: str,
        schema: "ProtocolSchemaDefinition",
        base_class: str | None = None,
    ) -> "Any":
        """Generate a Pydantic model class from a schema definition.

        Args:
            class_name: Name for the generated class
            schema: Schema definition to convert
            base_class: Base class to inherit from

        Returns:
            AST ClassDef node for the model
        """
        ...

    def generate_model_field(
        self,
        field_name: str,
        field_schema: "ProtocolSchemaDefinition",
        required: bool | None = None,
    ) -> "Any":
        """Generate a model field annotation.

        Args:
            field_name: Name of the field
            field_schema: Schema for the field
            required: Whether field is required

        Returns:
            AST annotation assignment for the field
        """
        ...

    def generate_enum_class(
        self,
        class_name: str,
        enum_values: list[str],
    ) -> "Any":
        """Generate an enum class from values.

        Args:
            class_name: Name for the enum class
            enum_values: List of enum values

        Returns:
            AST ClassDef node for the enum
        """
        ...

    def generate_import_statement(
        self,
        module: str,
        names: list[str],
        alias: str | None = None,
    ) -> "Any":
        """Generate an import statement.

        Args:
            module: Module to import from
            names: Names to import
            alias: Optional alias for import

        Returns:
            AST ImportFrom node
        """
        ...

    def generate_docstring(self, text: str) -> "Any": ...
    def generate_field_default(self, default_value: Any) -> "Any":
        """Generate default value expression for a field.

        Args:
            default_value: Default value (any Python value)

        Returns:
            AST expression for the default
        """
        ...

    def generate_validator_method(
        self,
        field_name: str,
        validator_type: str | None = None,
    ) -> "Any":
        """Generate a Pydantic validator method.

        Args:
            field_name: Field to validate
            validator_type: Type of validator
                ...
        Returns:
            AST FunctionDef for validator
        """
        ...

    def generate_type_annotation(
        self,
        type_string: str,
    ) -> "Any":
        """Generate type annotation from string.

        Args:
            type_string: Type as string

        Returns:
            ...
        """
        ...

    def generate_module(
        self,
        imports: list["Any"],
        classes: list["Any"],
        module_docstring: str | None = None,
    ) -> "Any":
        """Generate complete module AST.

        Args:
            imports: Import statements
                ...
            classes: Class definitions
            module_docstring: Optional module docstring

        Returns:
            Complete AST Module node
        """
        ...
