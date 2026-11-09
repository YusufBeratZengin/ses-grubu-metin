#!/usr/bin/env bash
# scripts/check.sh - Run all quality checks
# Usage: bash scripts/check.sh

set -euo pipefail

echo "=== Running Ruff (lint) ==="
ruff check src tests

echo "=== Running Ruff (format check) ==="
ruff format --check src tests

echo "=== Running MyPy (type check) ==="
mypy src/ses_grubu

echo "=== Running Tests with Coverage ==="
pytest -q --cov=ses_grubu --cov-report=term-missing --cov-report=xml

echo "=== Checking Coverage Threshold (>= 85%) ==="
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('coverage.xml')
root = tree.getroot()
line_rate = float(root.attrib.get('line-rate', 0))
if line_rate < 0.85:
    print(f'FAIL: Coverage {line_rate:.1%} below 85% threshold')
    exit(1)
print(f'OK: Coverage {line_rate:.1%} meets 85% threshold')
"

echo "=== All checks passed! ==="
