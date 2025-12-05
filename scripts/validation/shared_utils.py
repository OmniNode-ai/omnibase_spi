#!/usr/bin/env python3
"""
Shared Utilities for Security Validation Scripts.

This module provides common functionality used across multiple security
validation scripts, including bypass comment detection and shared constants.

Usage:
    from shared_utils import BypassChecker

    # Check for file-level bypass
    if BypassChecker.check_file_bypass_from_lines(content_lines, BYPASS_PATTERNS):
        return True  # Skip file

    # Check for line-level bypass
    if BypassChecker.check_line_bypass(line, BYPASS_PATTERNS):
        continue  # Skip this line

Note:
    This module uses only Python stdlib and has no external dependencies.
    This is required for pre-commit hook execution without virtualenv activation.
"""

from __future__ import annotations


class BypassChecker:
    """Unified bypass comment detection for security validators.

    Provides consistent bypass checking across all security validation tools.
    Supports both file-level bypasses (at file header or anywhere in file) and
    line-level bypasses (inline with specific violations).

    File-level bypasses can be detected in two modes:
    1. Header-only: Check first N lines (default 10) for bypass comments
    2. Anywhere: Check entire file content for bypass patterns

    Line-level bypasses are checked inline with the violation.

    Attributes:
        DEFAULT_HEADER_LINES: Default number of lines to check for header bypasses.

    Example:
        >>> from shared_utils import BypassChecker
        >>> bypass_patterns = ["secret-ok:", "nosec"]
        >>> line = 'api_key = "test"  # secret-ok: test fixture'
        >>> BypassChecker.check_line_bypass(line, bypass_patterns)
        True
        >>> content_lines = ["# secret-ok: entire file", "code here"]
        >>> BypassChecker.check_file_bypass_from_lines(content_lines, bypass_patterns)
        True
    """

    DEFAULT_HEADER_LINES: int = 10

    @staticmethod
    def check_line_bypass(line: str, bypass_patterns: list[str]) -> bool:
        """Check if a specific line has an inline bypass comment.

        Searches for any of the bypass patterns within the given line.
        This is typically used for inline bypass comments like:
            api_key = "test"  # secret-ok: test fixture

        Args:
            line: The source code line to check for bypass patterns.
            bypass_patterns: List of bypass pattern strings to search for.
                Common patterns include "secret-ok:", "nosec", "noqa: secrets".

        Returns:
            True if any bypass pattern is found in the line, False otherwise.

        Example:
            >>> line = 'password = "test"  # nosec'
            >>> BypassChecker.check_line_bypass(line, ["nosec", "secret-ok:"])
            True
        """
        return any(pattern in line for pattern in bypass_patterns)

    @staticmethod
    def check_file_bypass_from_lines(
        content_lines: list[str],
        bypass_patterns: list[str],
        max_lines: int | None = None,
    ) -> bool:
        """Check if file has a bypass comment in the header section.

        Scans the first N lines (default: DEFAULT_HEADER_LINES) of a file
        for bypass comments. Only considers lines that start with '#' after
        stripping whitespace, to ensure we're checking actual comments.

        This method is preferred when you already have the file content as
        a list of lines, as it avoids re-reading the file.

        Args:
            content_lines: List of lines from the file (including newlines).
            bypass_patterns: List of bypass pattern strings to search for.
            max_lines: Maximum number of lines to check from the start.
                If None, uses DEFAULT_HEADER_LINES (10).

        Returns:
            True if any bypass pattern is found in a comment within
            the header section, False otherwise.

        Example:
            >>> lines = ["#!/usr/bin/env python3", "# secret-ok: test file", "code"]
            >>> BypassChecker.check_file_bypass_from_lines(lines, ["secret-ok:"])
            True
        """
        if max_lines is None:
            max_lines = BypassChecker.DEFAULT_HEADER_LINES

        for line in content_lines[:max_lines]:
            stripped = line.strip()
            if stripped.startswith("#"):
                if any(pattern in line for pattern in bypass_patterns):
                    return True
        return False

    @staticmethod
    def check_file_bypass_from_content(
        content: str, bypass_patterns: list[str]
    ) -> bool:
        """Check if file has a bypass comment anywhere in content.

        Performs a simple string search for bypass patterns anywhere
        in the file content. This is a more permissive check than
        check_file_bypass_from_lines, as it doesn't require the bypass
        to be in a comment or in the header.

        Use this method when you want to allow bypass comments anywhere
        in the file, not just in the header section.

        Args:
            content: The entire file content as a string.
            bypass_patterns: List of bypass pattern strings to search for.

        Returns:
            True if any bypass pattern is found anywhere in the content,
            False otherwise.

        Example:
            >>> content = "code\\n# env-var-ok: configuration file\\nmore code"
            >>> BypassChecker.check_file_bypass_from_content(content, ["env-var-ok:"])
            True
        """
        return any(pattern in content for pattern in bypass_patterns)

    @staticmethod
    def extract_bypass_reason(line: str) -> str:
        """Extract the reason/justification from a bypass comment.

        When a bypass comment is found, this method extracts the full
        comment text including the bypass marker and any justification.
        This is useful for logging or auditing bypass usage.

        Args:
            line: The source code line containing a bypass comment.

        Returns:
            The comment portion of the line (from '#' to end), stripped
            of leading/trailing whitespace. Returns empty string if no
            '#' is found in the line.

        Example:
            >>> line = 'api_key = "test"  # secret-ok: required for tests'
            >>> BypassChecker.extract_bypass_reason(line)
            '# secret-ok: required for tests'
        """
        if "#" not in line:
            return ""
        comment_start = line.index("#")
        return line[comment_start:].strip()
