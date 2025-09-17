#!/bin/bash

# Validate Forbidden Patterns - Check for patterns that violate SPI standards
# Uses AST-based Python validation to check only real code, not comments/docstrings
# Exit codes: 0 = success, 1 = forbidden patterns found

set -euo pipefail

echo "🔍 Validating forbidden patterns in SPI codebase (AST-based)..."

# Check if Python validator exists
VALIDATOR_SCRIPT="scripts/validate_forbidden_patterns.py"

if [ ! -f "$VALIDATOR_SCRIPT" ]; then
    echo "❌ AST validator script not found: $VALIDATOR_SCRIPT"
    exit 1
fi

# Make validator executable
chmod +x "$VALIDATOR_SCRIPT"

# Run the AST-based validator
python3 "$VALIDATOR_SCRIPT"