#!/bin/bash

# Read JSON from stdin
input="$(cat)"

# Extract file_path using jq
file_path="$(echo "$input" | jq -r '.input.file_path // empty' 2>/dev/null)"

# If file_path is empty or extraction failed, allow (exit 0)
if [[ -z "$file_path" ]]; then
  exit 0
fi

# Get project directory
project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Resolve both paths to absolute canonical form (handles ".." etc.)
# Use realpath if the file doesn't exist yet: resolve the parent directory
resolved_file_path="$(cd "$(dirname "$file_path")" 2>/dev/null && echo "$(pwd -P)/$(basename "$file_path")")"

# If resolution failed (parent dir doesn't exist), try resolving what we can
if [[ -z "$resolved_file_path" ]]; then
  # Fallback: use Python or manual resolution for non-existent paths
  resolved_file_path="$(python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$file_path" 2>/dev/null)"
fi

# If still empty, allow to avoid false blocking
if [[ -z "$resolved_file_path" ]]; then
  exit 0
fi

resolved_project_dir="$(cd "$project_dir" 2>/dev/null && pwd -P)"

# If project dir resolution failed, allow
if [[ -z "$resolved_project_dir" ]]; then
  exit 0
fi

# Check if file_path starts with project directory
if [[ "$resolved_file_path" == "$resolved_project_dir"/* || "$resolved_file_path" == "$resolved_project_dir" ]]; then
  # Inside project directory — allow
  exit 0
else
  # Outside project directory — deny
  cat <<EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "🚫 [FREEZE] 不允許編輯專案目錄外的檔案: $file_path"
  }
}
EOF
  exit 2
fi
