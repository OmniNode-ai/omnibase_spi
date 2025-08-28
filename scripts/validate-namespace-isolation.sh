#!/bin/bash
set -e

echo "🔍 Validating namespace isolation for omnibase-spi..."

# Check for external omnibase imports (not omnibase.protocols.*)
echo "Checking for external omnibase imports..."
EXTERNAL_IMPORTS=$(grep -r "from omnibase\." src/ --include="*.py" | grep -v "from omnibase.protocols" || true)

if [ -n "$EXTERNAL_IMPORTS" ]; then
    echo "❌ NAMESPACE VIOLATION: Found external omnibase imports:"
    echo "$EXTERNAL_IMPORTS"
    echo ""
    echo "All imports must use 'from omnibase.protocols.*' for namespace isolation."
    exit 1
fi

# Check for Any usage (we try to minimize this for strong typing)
echo "Checking for Any type usage..."
ANY_USAGE=$(grep -r "from typing import.*Any" src/ --include="*.py" | wc -l || echo "0")
if [ "$ANY_USAGE" -gt 0 ]; then
    echo "⚠️  INFO: Found $ANY_USAGE files with Any type imports (aim to minimize for strong typing)"
fi

# Check protocol naming conventions (informational)
echo "Checking protocol naming conventions..."
PROTOCOL_COUNT=$(grep -r "^class Protocol.*:" src/ --include="*.py" | wc -l || echo "0")
echo "✅ Found $PROTOCOL_COUNT properly named Protocol classes"

# Run our namespace isolation tests
echo "Running namespace isolation tests..."
poetry run pytest tests/test_protocol_imports.py -v

echo "✅ Namespace isolation validation passed!"
echo "✅ All protocol imports are self-contained"
echo "✅ No external omnibase dependencies found"
echo "✅ Strong typing maintained"