#!/bin/bash
# Validate SPI Purity - Prevent implementation violations in Service Provider Interface
#
# This script ensures the SPI package contains only pure protocol definitions
# and no concrete implementations, enums, or ABC classes.

set -euo pipefail

echo "🔍 Validating SPI purity..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VIOLATIONS_FOUND=0

# Function to report violation
report_violation() {
    local file=$1
    local line=$2
    local violation=$3
    local message=$4
    
    echo -e "${RED}❌ SPI VIOLATION${NC} in ${file}:${line}"
    echo -e "   ${YELLOW}Found:${NC} ${violation}"
    echo -e "   ${YELLOW}Issue:${NC} ${message}"
    echo
    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
}

# Check for concrete class implementations (inheriting from non-Protocol classes)
echo "Checking for concrete class implementations..."
while IFS=: read -r file line content; do
    if [[ $content =~ class.*\(.*[^Protocol][a-zA-Z]*\): ]] && [[ ! $content =~ class.*\(.*Protocol.*\): ]] && [[ ! $content =~ class.*\(str,.*Enum\): ]] && [[ ! $content =~ class.*\(ABC\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain concrete class implementations"
    fi
done < <(grep -rn "^class.*(" src/ --include="*.py" || true)

# Check for Enum classes (should use Literal instead)
echo "Checking for Enum usage..."
while IFS=: read -r file line content; do
    if [[ $content =~ class.*\(.*Enum\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should use Literal types instead of Enums"
    fi
done < <(grep -rn "class.*Enum" src/ --include="*.py" || true)

# Check for ABC classes (should use Protocol instead)  
echo "Checking for ABC usage..."
while IFS=: read -r file line content; do
    if [[ $content =~ class.*\(ABC\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should use Protocol instead of ABC"
    fi
done < <(grep -rn "class.*ABC" src/ --include="*.py" || true)

# Check for concrete method implementations (methods with actual code, not just ...)
echo "Checking for concrete method implementations..."
TEMP_FILE=$(mktemp)
# Find all method definitions and check if they have implementations, excluding docstring examples
python3 -c "
import re
import sys
from pathlib import Path

def is_in_docstring_or_comment(file_path, line_num):
    '''Check if a line is inside a docstring or comment block'''
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        in_triple_quote = False
        quote_char = None
        
        for i, line in enumerate(lines[:line_num], 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Check for triple quote start/end
            if '\"\"\"' in line:
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_char = '\"\"\"'
                elif quote_char == '\"\"\"':
                    in_triple_quote = False
                    quote_char = None
            elif \"'''\" in line:
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_char = \"'''\"
                elif quote_char == \"'''\": 
                    in_triple_quote = False
                    quote_char = None
                    
        return in_triple_quote
    except:
        return False

# Find method definitions outside docstrings
for py_file in Path('src').rglob('*.py'):
    try:
        with open(py_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            if re.match(r'.*def.*\(self.*\):', line.strip()):
                if not is_in_docstring_or_comment(py_file, i):
                    # Check next few lines for implementation
                    next_lines = lines[i:i+5] if i < len(lines) else []
                    impl_found = False
                    
                    for next_line in next_lines:
                        stripped = next_line.strip()
                        if stripped and not stripped.startswith('#'):
                            if not re.match(r'^(\.\.\.|\"\"\"|\'\'\'|pass)$', stripped):
                                if re.search(r'(return [^.]|raise [^N]|if |for |while |try:|except|print|=)', stripped):
                                    impl_found = True
                                    break
                    
                    if impl_found:
                        print(f'{py_file}:{i}:{line.strip()}')
    except:
        continue
" > "$TEMP_FILE" 2>/dev/null || true

while IFS=: read -r file line content; do
    if [[ -n "$content" ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain concrete method implementations"
    fi
done < "$TEMP_FILE"
rm "$TEMP_FILE"

# Check for imports that suggest implementation (not just type definitions)
echo "Checking for implementation imports..."
TEMP_IMPORT_FILE=$(mktemp)

python3 -c "
import re
import sys
from pathlib import Path

def is_in_docstring_or_comment(file_path, line_num):
    '''Check if a line is inside a docstring or comment block'''
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        in_triple_quote = False
        quote_char = None
        
        for i, line in enumerate(lines[:line_num], 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Check for triple quote start/end
            if '\"\"\"' in line:
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_char = '\"\"\"'
                elif quote_char == '\"\"\"':
                    in_triple_quote = False
                    quote_char = None
            elif \"'''\" in line:
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_char = \"'''\"
                elif quote_char == \"'''\": 
                    in_triple_quote = False
                    quote_char = None
                    
        return in_triple_quote
    except:
        return False

import_patterns = [
    r'from abc import ABC',
    r'from enum import Enum',
    r'import asyncio',
    r'from datetime import datetime$',
    r'import logging',
    r'import os',
    r'import sys',
    r'import json',
    r'import yaml',
    r'import requests',
    r'import sqlite3',
    r'import psycopg2',
    r'import redis'
]

# Find implementation imports outside docstrings
for py_file in Path('src').rglob('*.py'):
    try:
        with open(py_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            if not is_in_docstring_or_comment(py_file, i):
                for pattern in import_patterns:
                    if re.search(pattern, line):
                        # Special handling for datetime in core_types.py
                        if pattern == r'from datetime import datetime$' and 'core_types.py' in str(py_file):
                            continue
                        print(f'{py_file}:{i}:{line.strip()}')
                        break
    except:
        continue
" > "$TEMP_IMPORT_FILE" 2>/dev/null || true

while IFS=: read -r file line content; do
    if [[ -n "$content" ]]; then
        report_violation "$file" "$line" "$content" "SPI should not import implementation libraries"
    fi
done < "$TEMP_IMPORT_FILE"
rm "$TEMP_IMPORT_FILE"

# Check for hardcoded values that suggest implementation logic (excluding docstring examples)
echo "Checking for implementation logic patterns..."
TEMP_LOGIC_FILE=$(mktemp)

python3 -c "
import re
import sys
from pathlib import Path

def is_in_docstring_or_comment(file_path, line_num):
    '''Check if a line is inside a docstring or comment block'''
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        in_triple_quote = False
        quote_char = None
        
        for i, line in enumerate(lines[:line_num], 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Check for triple quote start/end
            if '\"\"\"' in line:
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_char = '\"\"\"'
                elif quote_char == '\"\"\"':
                    in_triple_quote = False
                    quote_char = None
            elif \"'''\" in line:
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_char = \"'''\"
                elif quote_char == \"'''\": 
                    in_triple_quote = False
                    quote_char = None
                    
        return in_triple_quote
    except:
        return False

patterns = [
    r'print\(',
    r'logging\.',
    r'log\.',
    r'open\(',
    r'with open',
    r'requests\.',
    r'json\.loads',
    r'yaml\.load',
    r'os\.path',
    r'sys\.',
    r'time\.sleep',
    r'asyncio\.sleep',
    r'threading\.'
]

# Find implementation patterns outside docstrings
for py_file in Path('src').rglob('*.py'):
    try:
        with open(py_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            if not is_in_docstring_or_comment(py_file, i):
                for pattern in patterns:
                    if re.search(pattern, line):
                        print(f'{py_file}:{i}:{line.strip()}')
                        break
    except:
        continue
" > "$TEMP_LOGIC_FILE" 2>/dev/null || true

while IFS=: read -r file line content; do
    if [[ -n "$content" ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain implementation logic"
    fi
done < "$TEMP_LOGIC_FILE"
rm "$TEMP_LOGIC_FILE"

# Summary
echo "----------------------------------------"
if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ SPI purity validation PASSED${NC}"
    echo "All files contain only pure protocol definitions."
else
    echo -e "${RED}❌ SPI purity validation FAILED${NC}"
    echo "Found $VIOLATIONS_FOUND violations."
    echo
    echo "SPI (Service Provider Interface) should contain only:"
    echo "• Protocol definitions using typing.Protocol"
    echo "• Type aliases using typing.Literal"
    echo "• Type unions and generic types"
    echo "• Abstract method signatures with '...' implementation"
    echo
    echo "SPI should NOT contain:"
    echo "• Concrete class implementations"
    echo "• Enum classes (use Literal instead)"
    echo "• ABC classes (use Protocol instead)"
    echo "• Method implementations with actual logic"
    echo "• Implementation library imports"
    echo "• Business logic or concrete behavior"
    exit 1
fi