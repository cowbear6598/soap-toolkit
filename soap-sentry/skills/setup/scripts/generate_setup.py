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

# Ask for profile name
read -p "Profile name (e.g. work, personal): " profile
if [ -z "$profile" ]; then
    echo "Error: profile name cannot be empty"
    exit 1
fi

PROFILE_UPPER=$(echo "$profile" | tr '[:lower:]' '[:upper:]')

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
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.zshrc"
fi

# Remove existing entries for this profile (if any)
TOKEN_KEY="SENTRY_AUTH_TOKEN_${PROFILE_UPPER}"
ORG_KEY="SENTRY_ORG_${PROFILE_UPPER}"

if grep -q "$TOKEN_KEY\|$ORG_KEY" "$SHELL_CONFIG" 2>/dev/null; then
    # Create temp file without old entries
    grep -v "export ${TOKEN_KEY}=" "$SHELL_CONFIG" | grep -v "export ${ORG_KEY}=" > "${SHELL_CONFIG}.tmp"
    mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
    echo "Removed existing ${PROFILE_UPPER} profile entries."
fi

# Append new entries
echo "" >> "$SHELL_CONFIG"
echo "# Sentry profile: ${profile}" >> "$SHELL_CONFIG"
echo "export ${TOKEN_KEY}=${token}" >> "$SHELL_CONFIG"
echo "export ${ORG_KEY}=${org}" >> "$SHELL_CONFIG"

echo "Written to ${SHELL_CONFIG}:"
echo "  export ${TOKEN_KEY}=****"
echo "  export ${ORG_KEY}=${org}"
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
