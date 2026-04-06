#!/usr/bin/env bash
# Test that running --update-readme produces no changes.
# This verifies the generated scripts in README.md are in sync with the data files.
set -euo pipefail

cp README.md README.md.before
python save_region.py --update-readme
diff README.md.before README.md
rm README.md.before
echo "PASS: update-readme is a noop"
