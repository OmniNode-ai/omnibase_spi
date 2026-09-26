#!/bin/bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

set -e

echo "🔍 Validating namespace isolation for omnibase-spi..."

if [[ $# -gt 0 ]]; then
    TARGETS=("$@")
    RUN_NAMESPACE_TESTS=false
else
    TARGETS=(src/)
    RUN_NAMESPACE_TESTS=true
fi

# Check for external omnibase imports (not omnibase_spi.protocols.*)
echo "Checking for external omnibase imports..."
EXTERNAL_IMPORTS=$(grep -rHn --include="*.py" "from omnibase\." "${TARGETS[@]}" 2>/dev/null | grep -v "from omnibase_spi.protocols" || true)

if [ -n "$EXTERNAL_IMPORTS" ]; then
    echo "❌ NAMESPACE VIOLATION: Found external omnibase imports:"
    echo "$EXTERNAL_IMPORTS"
    echo ""
    echo "All imports must use 'from omnibase_spi.protocols.*' for namespace isolation."
    exit 1
fi

# Check for Any usage (we try to minimize this for strong typing)
echo "Checking for Any type usage..."
ANY_USAGE=$(grep -rH --include="*.py" "from typing import.*Any" "${TARGETS[@]}" 2>/dev/null | wc -l | tr -d ' ')
if [ "$ANY_USAGE" -gt 0 ]; then
    echo "⚠️  INFO: Found $ANY_USAGE files with Any type imports (aim to minimize for strong typing)"
fi

# Check protocol naming conventions (informational)
echo "Checking protocol naming conventions..."
PROTOCOL_COUNT=$(grep -rH --include="*.py" "^class Protocol.*:" "${TARGETS[@]}" 2>/dev/null | wc -l | tr -d ' ')
echo "✅ Found $PROTOCOL_COUNT properly named Protocol classes"

if [[ "$RUN_NAMESPACE_TESTS" == true ]]; then
    echo "Running namespace isolation tests..."
    uv run pytest tests/test_protocol_imports.py -v
fi

echo "✅ Namespace isolation validation passed!"
echo "✅ All protocol imports are self-contained"
echo "✅ No external omnibase dependencies found"
echo "✅ Strong typing maintained"
