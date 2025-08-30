#!/bin/bash

# Pre-commit hook to prevent any use of the word "simple" in the codebase
# This ensures that "simple" terminology is completely eliminated

set -e

echo "🔍 Checking for forbidden 'simple' terminology..."

# Search for "simple" case-insensitively in source files, ignoring cache and binary files
SIMPLE_FOUND=$(grep -r -i "simple" src/ tests/ \
    --exclude-dir="__pycache__" \
    --exclude-dir=".pytest_cache" \
    --exclude-dir=".mypy_cache" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude="*.pyd" \
    --include="*.py" \
    --include="*.md" \
    --include="*.txt" \
    --include="*.yaml" \
    --include="*.yml" \
    2>/dev/null || true)

if [ -n "$SIMPLE_FOUND" ]; then
    echo "❌ FORBIDDEN: Found 'simple' terminology in codebase:"
    echo "$SIMPLE_FOUND"
    echo ""
    echo "The word 'simple' is forbidden in this codebase."
    echo "Please use alternatives like 'basic', 'minimal', 'core', or 'fundamental'."
    exit 1
fi

echo "✅ No 'simple' terminology found - validation passed!"