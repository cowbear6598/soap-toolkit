import json
import os
import tempfile


def main() -> None:
    script_content = r'''#!/bin/bash
set -e

echo "=== Threads Setup ==="
echo ""

# Ask for session ID (hidden input)
read -sp "Threads Session ID: " session_id
echo ""
if [ -z "$session_id" ]; then
    echo "Error: session ID cannot be empty"
    exit 1
fi

echo ""

# Detect shell config file
if [ -n "$ZSH_VERSION" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# Clean up old entries from ~/.bashrc if any
if [ -f "$HOME/.bashrc" ] && grep -q "THREADS_SESSION_ID" "$HOME/.bashrc" 2>/dev/null; then
    grep -v "export THREADS_SESSION_ID=" "$HOME/.bashrc" > "$HOME/.bashrc.tmp"
    mv "$HOME/.bashrc.tmp" "$HOME/.bashrc"
    echo "Cleaned up old entries from ~/.bashrc"
fi

# Remove existing entry (if any)
if grep -q "THREADS_SESSION_ID" "$SHELL_CONFIG" 2>/dev/null; then
    grep -v "export THREADS_SESSION_ID=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp"
    mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
    echo "Removed existing THREADS_SESSION_ID entry."
fi

# Append new entry
echo "" >> "$SHELL_CONFIG"
echo "# Threads Session ID" >> "$SHELL_CONFIG"
echo "export THREADS_SESSION_ID=${session_id}" >> "$SHELL_CONFIG"

echo "Written to ${SHELL_CONFIG}:"
echo "  export THREADS_SESSION_ID=****"
echo ""
echo "Done! Restart Claude Code to take effect."
'''

    output_path = os.path.join(tempfile.gettempdir(), "setup_threads.sh")
    with open(output_path, "w") as f:
        f.write(script_content)
    os.chmod(output_path, 0o755)

    print(json.dumps({
        "script": output_path,
        "message": f"Setup script generated at {output_path}. User should run: bash {output_path}"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
