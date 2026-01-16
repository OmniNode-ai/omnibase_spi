"""
Protocol for naming convention utilities used across ONEX code generation.

This protocol defines the interface for string conversion utilities that ensure
consistent naming across all code generation tools.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolInputState, ProtocolOutputState


@runtime_checkable
class ProtocolNamingConventions(Protocol):
    """
    Protocol for naming convention conversion utilities.

    Provides standardized string conversion methods used across
    code generation tools to ensure consistency.
    """

    def convert_naming_convention(
        self, input_state: ProtocolInputState
    ) -> ProtocolOutputState:
        """
        Convert a string between naming conventions.

        Transforms the input string from its source naming convention to the
        target convention specified in metadata.

        Args:
            input_state: Input state containing:
                - input_string: The string to convert.
                - source_format: Source naming convention (e.g., "snake_case").
                - metadata: Must include "target_format" key specifying the
                  desired output convention (e.g., "camelCase", "PascalCase").

        Returns:
            ProtocolOutputState with:
                - output_string: The converted string in the target format.
                - target_format: The naming convention applied to the output.
                - conversion_success: True if conversion completed successfully.
                - metadata: Conversion details including detected source format.

        Raises:
            ValueError: If input_string is empty or target_format is not a
                recognized naming convention.
            KeyError: If "target_format" key is missing from metadata.
        """
        ...

    async def validate_python_identifier(
        self,
        input_state: ProtocolInputState,
    ) -> ProtocolOutputState:
        """
        Validate and optionally sanitize a Python identifier.

        Checks whether the input string is a valid Python identifier according
        to PEP 3131. When sanitization is enabled, invalid characters are
        replaced and leading digits are prefixed.

        Args:
            input_state: Input state containing:
                - input_string: The identifier to validate.
                - source_format: Expected identifier type (e.g., "variable",
                  "class", "module").
                - metadata: Optional sanitization options (e.g., "sanitize": True).

        Returns:
            ProtocolOutputState with:
                - output_string: The sanitized identifier, or original if valid.
                - target_format: "python_identifier".
                - conversion_success: True if identifier is valid or was
                  sanitized successfully.
                - metadata: Validation details with "is_valid" boolean,
                  "issues" list of detected problems, and "sanitized" flag.

        Raises:
            ValueError: If input_string is empty.
            TypeError: If input_string is not a string type.
        """
        ...

    def generate_class_names(
        self, input_state: ProtocolInputState
    ) -> ProtocolOutputState:
        """
        Generate a PascalCase class name from the input string.

        Converts input strings to valid PascalCase class names following
        Python naming conventions (PEP 8). Handles various input formats
        and applies optional prefix/suffix transformations.

        Args:
            input_state: Input state containing:
                - input_string: The base name to convert to a class name.
                - source_format: Format of the input (e.g., "snake_case",
                  "kebab-case", "natural").
                - metadata: Optional hints including "prefix" and "suffix".

        Returns:
            ProtocolOutputState with:
                - output_string: The generated PascalCase class name.
                - target_format: "PascalCase".
                - conversion_success: True if a valid class name was generated.
                - metadata: Generation details with "original_words" list.

        Raises:
            ValueError: If input_string is empty or contains only invalid
                characters that cannot form a valid class name.
            TypeError: If input_string is not a string type.
        """
        ...

    def generate_file_names(
        self,
        input_state: ProtocolInputState,
    ) -> ProtocolOutputState:
        """
        Generate a snake_case file name from the input string.

        Converts input strings (typically class names) to valid snake_case
        file names following Python module naming conventions. Appends the
        specified file extension.

        Args:
            input_state: Input state containing:
                - input_string: The base name to convert (e.g., class name).
                - source_format: Format of the input (e.g., "PascalCase",
                  "camelCase").
                - metadata: Optional hints including "extension" (default: ".py").

        Returns:
            ProtocolOutputState with:
                - output_string: The generated snake_case file name with extension.
                - target_format: "snake_case".
                - conversion_success: True if a valid file name was generated.
                - metadata: Generation details with "extension" and "base_name".

        Raises:
            ValueError: If input_string is empty or contains only invalid
                characters that cannot form a valid file name.
            TypeError: If input_string is not a string type.
        """
        ...

    def split_into_words(self, input_state: ProtocolInputState) -> ProtocolOutputState:
        """
        Split a string into its constituent words.

        Parses the input string to extract individual words by detecting
        naming convention boundaries. Handles camelCase, PascalCase,
        snake_case, kebab-case, and mixed formats. Word boundaries are
        identified by case transitions, underscores, hyphens, and spaces.

        Args:
            input_state: Input state containing:
                - input_string: The string to split into words.
                - source_format: Optional hint for input format (e.g.,
                  "camelCase", "snake_case"). Auto-detected if not specified.
                - metadata: Optional options including "preserve_case" boolean.

        Returns:
            ProtocolOutputState with:
                - output_string: Space-separated lowercase words.
                - target_format: "word_list".
                - conversion_success: True if at least one word was extracted.
                - metadata: Contains "words" (list of extracted words) and
                  "detected_format" (identified source naming convention).

        Raises:
            ValueError: If input_string is empty.
            TypeError: If input_string is not a string type.
        """
        ...
