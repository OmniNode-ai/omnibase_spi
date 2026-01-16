"""
Protocol for AST Builder functionality.

Defines the interface for building Python Abstract Syntax Tree (AST)
nodes for code generation.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolSchemaDefinition,
    )


@runtime_checkable
class ProtocolASTBuilder(Protocol):
    """
    Protocol for Python Abstract Syntax Tree (AST) construction and code generation.

    Defines the contract for building Python AST nodes from schema definitions,
    enabling programmatic code generation for Pydantic models, enums, validators,
    and complete modules. Provides the foundation for contract-driven code generation
    workflows in the ONEX ecosystem.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolASTBuilder
        from omnibase_spi.protocols.types import ProtocolSchemaDefinition
        import ast

        async def generate_model_code(
            builder: ProtocolASTBuilder,
            schema: ProtocolSchemaDefinition
        ) -> str:
            # Generate Pydantic model class AST
            model_ast = builder.generate_model_class(
                class_name="UserProfile",
                schema=schema,
                base_class="BaseModel"
            )

            # Generate complete module with imports
            imports = [
                builder.generate_import_statement(
                    module="pydantic",
                    names=["BaseModel", "Field"]
                )
            ]
            module_ast = builder.generate_module(
                imports=imports,
                classes=[model_ast],
                module_docstring="Auto-generated user profile model"
            )

            # Convert AST to Python code
            code = ast.unparse(module_ast)
            return code
        ```

    Key Features:
        - Pydantic model class generation from schemas
        - Enum class generation with proper member handling
        - Type annotation generation from string specifications
        - Validator and field default value generation
        - Complete module assembly with imports and docstrings
        - AST node creation for all Python constructs

    See Also:
        - ProtocolContractAnalyzer: Contract analysis for code generation
        - ProtocolEnumGenerator: Specialized enum discovery and generation
        - ProtocolOutputFormatter: Code formatting and output handling
    """

    def generate_model_class(
        self,
        class_name: str,
        schema: "ProtocolSchemaDefinition",
        base_class: str | None = None,
    ) -> object:
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
    ) -> object:
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
    ) -> object:
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
    ) -> object:
        """Generate an import statement.

        Args:
            module: Module to import from
            names: Names to import
            alias: Optional alias for import

        Returns:
            AST ImportFrom node
        """
        ...

    def generate_docstring(self, text: str) -> object:
        """Generate an AST expression node for a docstring.

        Creates an AST Expr node containing a Constant string node,
        suitable for use as a docstring in classes, functions, or modules.

        Args:
            text: The docstring text content.

        Returns:
            AST Expr node containing the docstring constant.

        Raises:
            ValueError: If text is empty or contains only whitespace.
        """
        ...

    def generate_field_default(self, default_value: object) -> object:
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
    ) -> object:
        """Generate a Pydantic validator method.

        Args:
            field_name: Field to validate
            validator_type: Type of validator

        Returns:
            AST FunctionDef for validator
        """
        ...

    def generate_type_annotation(
        self,
        type_string: str,
    ) -> object:
        """Generate type annotation from string.

        Args:
            type_string: Type as string

        Returns:
            AST expression for the type annotation
        """
        ...

    def generate_module(
        self,
        imports: list[object],
        classes: list[object],
        module_docstring: str | None = None,
    ) -> object:
        """Generate complete module AST.

        Args:
            imports: Import statements (AST nodes)
            classes: Class definitions (AST nodes)
            module_docstring: Optional module docstring

        Returns:
            Complete AST Module node
        """
        ...
