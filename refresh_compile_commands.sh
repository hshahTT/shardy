#!/bin/bash
# Wrapper script to refresh compile_commands.json and fix include paths automatically
#
# Usage: ./refresh_compile_commands.sh
#   or:  bash refresh_compile_commands.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ">>> Refreshing compile_commands.json with hedron_compile_commands..."
bazel run @hedron_compile_commands//:refresh_all

echo ""
echo ">>> Fixing include paths in compile_commands.json..."
python3 tools/fix_compile_commands.py

echo ""
echo ">>> Done! compile_commands.json has been refreshed and fixed."

