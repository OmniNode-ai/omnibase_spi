"""
Protocol for Type Mapper functionality.

Defines the interface for mapping JSON Schema types to Python type strings.
Used for contract generation and model creation.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolModelSchema(Protocol):
    """
    Protocol for schema models used in JSON Schema to Python type mapping.

    Represents a JSON Schema definition with introspection capabilities
    for determining the schema type, extracting properties, and generating
    corresponding Python type representations.

    Attributes:
        type: JSON Schema type (string, number, object, array, etc.)
        properties: Dictionary of property definitions for object types
        required: List of required property names
        items: Schema definition for array item types
        enum: List of allowed values for enum types

    Example:
        ```python
        mapper: ProtocolTypeMapper = get_type_mapper()

        # Given a schema from contract
        if schema.is_array_type():
            type_str = await mapper.get_array_type_string(schema)
        elif schema.is_object_type():
            type_str = await mapper.get_object_type_string(schema)
        elif schema.is_enum_type():
            enum_name = mapper.generate_enum_name_from_values(schema.enum)
        else:
            type_str = await schema.get_python_type()
        ```

    See Also:
        - ProtocolTypeMapper: Type mapping interface
        - ProtocolContractModelSchema: Contract schema structure
    """

    type: str
    properties: dict[str, object]
    required: list[str]
    items: object | None  # For array types
    enum: list[str] | None  # For enum types

    async def get_python_type(self) -> str: ...

    def is_array_type(self) -> bool: ...

    def is_object_type(self) -> bool: ...

    def is_enum_type(self) -> bool: ...


@runtime_checkable
class ProtocolTypeMapper(Protocol):
    """
    Protocol for JSON Schema to Python type mapping functionality.

    Provides the interface for converting JSON Schema definitions to
    Python type strings for code generation, including complex types,
    arrays, enums, and import statement generation.

    Example:
        ```python
        mapper: ProtocolTypeMapper = get_type_mapper()

        # Map a simple schema
        type_str = await mapper.get_type_string_from_schema(schema)
        print(f"Python type: {type_str}")

        # Check if import needed
        import_stmt = await mapper.get_import_for_type(type_str)
        if import_stmt:
            print(f"Required import: {import_stmt}")

        # Check if this is a model type
        if mapper.is_model_type(type_str):
            print(f"Model type detected: {type_str}")

        # Generate enum name from values
        enum_name = mapper.generate_enum_name_from_values(["ACTIVE", "INACTIVE"])
        print(f"Enum name: {enum_name}")  # e.g., "EnumStatus"
        ```

    See Also:
        - ProtocolModelSchema: Schema input for mapping
        - ProtocolContractAnalyzer: Contract analysis with type mapping
    """

    async def get_type_string_from_schema(self, schema: ProtocolModelSchema) -> str:
        """Get type string representation from schema.

        Args:
            schema: ProtocolModelSchema object to convert

        Returns:
            Python type string (e.g., "str", "List[str]", "ModelFoo")
        """
        ...

    async def get_array_type_string(self, schema: ProtocolModelSchema) -> str:
        """Get array type string from schema.

        Args:
            schema: Array schema with items definition

        Returns:
            Array type string (e.g., "List[str]", "List[ModelItem]")
        """
        ...

    async def get_object_type_string(self, schema: ProtocolModelSchema) -> str:
        """Get object type string from schema.

        Args:
            schema: Object schema to analyze

        Returns:
            Object type string (e.g., "ModelObjectData", "ModelCustom")
        """
        ...

    def generate_enum_name_from_values(self, enum_values: list[str]) -> str:
        """Generate enum class name from enum values.

        Args:
            enum_values: List of enum values

        Returns:
            Generated enum class name (e.g., "EnumStatus")
        """
        ...

    async def get_import_for_type(self, type_string: str) -> str | None:
        """Get the import statement needed for a type string.

        Args:
            type_string: Python type string to analyze

        Returns:
            Import statement if needed, None otherwise
        """
        ...

    def is_model_type(self, type_string: str) -> bool:
        """Check if a type string represents a model type.

        Args:
            type_string: Type string to check

        Returns:
            True if this is a model type (starts with Model)
        """
        ...
