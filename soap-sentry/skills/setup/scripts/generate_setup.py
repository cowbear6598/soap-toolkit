import json
import os
import sys
import tempfile


def main() -> None:
    # Generate the setup script in a temp location
    script_content = r'''#!/bin/bash
set -e

echo "=== Sentry Setup ==="
echo ""

# Ask for token (hidden input)
read -sp "Sentry Auth Token: " token
echo ""
if [ -z "$token" ]; then
    echo "Error: token cannot be empty"
    exit 1
fi

# Ask for org slug
read -p "Sentry Organization slug: " org
if [ -z "$org" ]; then
    echo "Error: org slug cannot be empty"
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
if [ -f "$HOME/.bashrc" ] && grep -q "SENTRY_AUTH_TOKEN\|SENTRY_ORG" "$HOME/.bashrc" 2>/dev/null; then
    grep -v "export SENTRY_AUTH_TOKEN=\|export SENTRY_ORG=" "$HOME/.bashrc" > "$HOME/.bashrc.tmp"
    mv "$HOME/.bashrc.tmp" "$HOME/.bashrc"
    echo "Cleaned up old entries from ~/.bashrc"
fi

# Remove existing entries (if any)
if grep -q "SENTRY_AUTH_TOKEN\|SENTRY_ORG" "$SHELL_CONFIG" 2>/dev/null; then
    # Create temp file without old entries
    grep -v "export SENTRY_AUTH_TOKEN=" "$SHELL_CONFIG" | grep -v "export SENTRY_ORG=" > "${SHELL_CONFIG}.tmp"
    mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
    echo "Removed existing SENTRY_AUTH_TOKEN and SENTRY_ORG entries."
fi

# Append new entries
echo "" >> "$SHELL_CONFIG"
echo "# Sentry credentials" >> "$SHELL_CONFIG"
echo "export SENTRY_AUTH_TOKEN=${token}" >> "$SHELL_CONFIG"
echo "export SENTRY_ORG=${org}" >> "$SHELL_CONFIG"

echo "Written to ${SHELL_CONFIG}:"
echo "  export SENTRY_AUTH_TOKEN=****"
echo "  export SENTRY_ORG=${org}"
echo ""
echo "Done! Restart Claude Code to take effect."
'''

    # Write to a temp file that persists
    output_path = os.path.join(tempfile.gettempdir(), "setup_sentry.sh")
    with open(output_path, "w") as f:
        f.write(script_content)
    os.chmod(output_path, 0o755)

    print(json.dumps({
        "script": output_path,
        "message": f"Setup script generated at {output_path}. User should run: bash {output_path}"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
