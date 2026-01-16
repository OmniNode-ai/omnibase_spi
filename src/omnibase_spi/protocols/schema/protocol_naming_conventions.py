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
        Convert strings between different naming conventions.

        Args:
            input_state: Contains conversion parameters

        Returns:
            ProtocolOutputState with converted strings
        """
        ...

    async def validate_python_identifier(
        self,
        input_state: ProtocolInputState,
    ) -> ProtocolOutputState:
        """
        Validate and sanitize Python identifiers.

        Args:
            input_state: Contains identifier validation parameters

        Returns:
            ProtocolOutputState with validation results
        """
        ...

    def generate_class_names(
        self, input_state: ProtocolInputState
    ) -> ProtocolOutputState:
        """
        Generate appropriate class names from various inputs.

        Args:
            input_state: Contains class name generation parameters

        Returns:
            ProtocolOutputState with generated class names
        """
        ...

    def generate_file_names(
        self,
        input_state: ProtocolInputState,
    ) -> ProtocolOutputState:
        """
        Generate appropriate file names from class names or other inputs.

        Args:
            input_state: Contains file name generation parameters

        Returns:
            ProtocolOutputState with generated file names
        """
        ...

    def split_into_words(self, input_state: ProtocolInputState) -> ProtocolOutputState:
        """
        Split a string into its constituent words.

        Handles various naming conventions including camelCase, PascalCase,
        snake_case, kebab-case, and mixed formats.

        Args:
            input_state: Contains the string to split and any format hints.

        Returns:
            ProtocolOutputState containing a list of extracted words.
        """
        ...
