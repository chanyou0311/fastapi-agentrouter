#!/bin/bash
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path')

if [[ "$FILE_PATH" == *.py ]]; then
  if ! out=$(uv run pytest 2>&1); then
    printf 'Python tests failed.\n--- pytest output ---\n%s\n' "$out" >&2
    exit 2
  fi
fi

exit 0
