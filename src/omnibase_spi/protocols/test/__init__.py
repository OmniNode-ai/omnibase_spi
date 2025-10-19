"""Testing domain protocols for ONEX.

This domain contains protocols for testing frameworks,
testable components, and test coordination.
"""

from .protocol_testable import ProtocolTestable
from .protocol_testable_cli import ProtocolTestableCLI

__all__ = ["ProtocolTestable", "ProtocolTestableCLI"]
