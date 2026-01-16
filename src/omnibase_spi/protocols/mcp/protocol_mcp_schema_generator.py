"""
MCP Schema Generator Protocol - ONEX SPI Interface.

Protocol definition for generating JSON schemas for MCP tools.
Provides schema generation capabilities for input/output models and parameter definitions.

Domain: MCP schema generation and tool definition support
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolMCPSchemaGenerator(Protocol):
    """
    Protocol for generating JSON schemas for MCP tool definitions.

    Provides comprehensive schema generation capabilities for creating
    well-formed JSON schemas that describe MCP tool inputs, outputs,
    and parameters. Generated schemas follow JSON Schema draft specifications
    and are compatible with MCP tool registration requirements.

    Key Features:
        - **Input Schema Generation**: Create schemas for tool input models
        - **Output Schema Generation**: Create schemas for tool output models
        - **Parameter Schema Generation**: Batch generation for multiple parameters
        - **Schema Validation**: Validate generated schemas for correctness
        - **Field Mapping Support**: Map model fields to schema properties with custom mappings

    Usage:
        Implementations of this protocol are used during MCP tool registration
        to generate the JSON schemas that describe tool interfaces.

    Example:
        ```python
        generator: ProtocolMCPSchemaGenerator = get_schema_generator()

        # Generate input schema for a tool
        input_schema = await generator.generate_input_schema(
            input_model="ProcessDataInput",
            mappings=["input_file:required", "options:optional"]
        )

        # Generate output schema
        output_schema = await generator.generate_output_schema(
            output_model="ProcessDataOutput"
        )

        # Validate the generated schema
        if await generator.validate_schema(input_schema):
            # Schema is valid, proceed with registration
            register_tool(input_schema, output_schema)

        # Generate schemas for multiple parameters at once
        param_schemas = await generator.generate_parameter_schemas(
            parameters=[
                {"name": "query", "type": "string", "required": True},
                {"name": "limit", "type": "integer", "required": False},
            ]
        )
        ```

    Schema Format:
        Generated schemas follow JSON Schema format with properties like:
        - type: The JSON type (string, integer, object, array, etc.)
        - properties: For object types, the nested property definitions
        - required: List of required property names
        - description: Human-readable property descriptions

    See Also:
        - ProtocolMCPToolValidator: For validating tool definitions including schemas
        - ProtocolMCPRegistry: For registering tools with generated schemas
    """

    async def generate_input_schema(
        self, input_model: str, mappings: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Generate a JSON schema for an MCP tool input model.

        Creates a well-formed JSON schema that describes the expected input
        structure for an MCP tool. The schema can be used for validation,
        documentation, and client code generation.

        Args:
            input_model: The name or identifier of the input model to generate
                a schema for. This typically corresponds to a Pydantic model
                class name or a registered model identifier.
            mappings: Optional list of field mapping specifications. Each mapping
                is a string in the format "field_name:constraint" where constraint
                can be "required", "optional", or a type hint. If None, default
                mappings are inferred from the model definition.

        Returns:
            A dictionary representing the JSON schema for the input model.
            The schema includes standard JSON Schema properties like "type",
            "properties", "required", and "description". Values are standard
            JSON-compatible types (str, int, bool, list, dict, None).

        Raises:
            ValueError: If the input_model identifier is invalid or not found.
            SchemaGenerationError: If schema generation fails due to model
                introspection errors or invalid field configurations.

        Example:
            ```python
            # Generate schema with default mappings
            schema = await generator.generate_input_schema("UserInput")

            # Generate schema with explicit field mappings
            schema = await generator.generate_input_schema(
                input_model="SearchQuery",
                mappings=[
                    "query:required",
                    "filters:optional",
                    "page_size:integer",
                ]
            )
            ```
        """
        ...

    async def generate_output_schema(self, output_model: str) -> dict[str, Any]:
        """
        Generate a JSON schema for an MCP tool output model.

        Creates a well-formed JSON schema that describes the expected output
        structure from an MCP tool execution. The schema enables clients to
        understand and validate tool responses.

        Args:
            output_model: The name or identifier of the output model to generate
                a schema for. This typically corresponds to a Pydantic model
                class name or a registered model identifier.

        Returns:
            A dictionary representing the JSON schema for the output model.
            The schema includes standard JSON Schema properties like "type",
            "properties", and "description". Values are standard
            JSON-compatible types (str, int, bool, list, dict, None).

        Raises:
            ValueError: If the output_model identifier is invalid or not found.
            SchemaGenerationError: If schema generation fails due to model
                introspection errors.

        Example:
            ```python
            # Generate output schema
            schema = await generator.generate_output_schema("SearchResult")

            # Use schema for response validation
            validate_response(response_data, schema)
            ```
        """
        ...

    async def validate_schema(self, schema: dict[str, Any]) -> bool:
        """
        Validate a generated JSON schema for correctness.

        Performs comprehensive validation of a JSON schema to ensure it
        conforms to the JSON Schema specification and meets MCP tool
        registration requirements.

        Args:
            schema: The JSON schema dictionary to validate. Should be a
                schema previously generated by this generator or one
                that follows the same format conventions.

        Returns:
            True if the schema is valid and conforms to all requirements,
            False otherwise.

        Raises:
            TypeError: If the schema argument is not a dictionary.

        Example:
            ```python
            schema = await generator.generate_input_schema("MyInput")

            if await generator.validate_schema(schema):
                print("Schema is valid")
            else:
                print("Schema validation failed")
            ```

        Validation Checks:
            - Required "type" property is present
            - Property types are valid JSON Schema types
            - Required array contains only defined properties
            - Nested object schemas are recursively valid
            - No circular references exist
        """
        ...

    async def generate_parameter_schemas(
        self, parameters: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Generate JSON schemas for multiple parameters in batch.

        Efficiently generates schemas for a list of parameter definitions,
        useful when registering tools with multiple parameters or when
        generating documentation for tool interfaces.

        Args:
            parameters: A list of parameter definition dictionaries. Each
                dictionary should contain at minimum:
                - "name": The parameter name (str)
                - "type": The parameter type (str, e.g., "string", "integer")

                Optional keys include:
                - "required": Whether the parameter is required (bool)
                - "description": Human-readable description (str)
                - "default": Default value if not provided
                - "enum": List of allowed values for enum types
                - "items": Item schema for array types

        Returns:
            A list of JSON schema dictionaries, one for each input parameter.
            Each schema is a complete JSON Schema object that can be used
            independently for validation or documentation.

        Raises:
            ValueError: If any parameter definition is missing required keys
                or contains invalid type specifications.
            SchemaGenerationError: If batch schema generation fails.

        Example:
            ```python
            parameters = [
                {
                    "name": "query",
                    "type": "string",
                    "required": True,
                    "description": "Search query string"
                },
                {
                    "name": "limit",
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "description": "Maximum results to return"
                },
                {
                    "name": "filters",
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter criteria"
                }
            ]

            schemas = await generator.generate_parameter_schemas(parameters)
            for schema in schemas:
                print(f"Generated schema: {schema}")
            ```
        """
        ...
