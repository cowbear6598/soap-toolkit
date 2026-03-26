import json
import os
import tempfile


def main() -> None:
    script_content = r'''#!/bin/bash
set -e

echo "=== Slack Setup ==="
echo ""

# Ask for profile name
read -p "Profile name (e.g. default, notify): " profile
if [ -z "$profile" ]; then
    echo "Error: profile name cannot be empty"
    exit 1
fi

PROFILE_UPPER=$(echo "$profile" | tr '[:lower:]' '[:upper:]' | tr '-' '_')

echo ""

# Ask for bot token (hidden input)
read -sp "Slack Bot Token (xoxb-...): " token
echo ""
if [ -z "$token" ]; then
    echo "Error: token cannot be empty"
    exit 1
fi

echo ""

# Remove existing entry for this profile (if any)
TOKEN_KEY="SLACK_BOT_TOKEN_${PROFILE_UPPER}"

# Detect shell config file
if [ -n "$ZSH_VERSION" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    # Remove existing entries
    if grep -q "$TOKEN_KEY" "$SHELL_CONFIG" 2>/dev/null; then
        grep -v "export ${TOKEN_KEY}=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp"
        mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
        echo "Removed existing ${PROFILE_UPPER} profile entry."
    fi
    # Append to end
    echo "" >> "$SHELL_CONFIG"
    echo "# Slack profile: ${profile}" >> "$SHELL_CONFIG"
    echo "export ${TOKEN_KEY}=${token}" >> "$SHELL_CONFIG"
else
    SHELL_CONFIG="$HOME/.bashrc"
    # Remove existing entries from bashrc
    if grep -q "$TOKEN_KEY" "$SHELL_CONFIG" 2>/dev/null; then
        grep -v "export ${TOKEN_KEY}=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp"
        mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
        echo "Removed existing ${PROFILE_UPPER} profile entry."
    fi
    # Insert at the TOP of bashrc (before any early return)
    TMPFILE=$(mktemp)
    echo "# Slack profile: ${profile}" > "$TMPFILE"
    echo "export ${TOKEN_KEY}=${token}" >> "$TMPFILE"
    echo "" >> "$TMPFILE"
    cat "$SHELL_CONFIG" >> "$TMPFILE"
    mv "$TMPFILE" "$SHELL_CONFIG"
fi

echo "Written to ${SHELL_CONFIG}:"
echo "  export ${TOKEN_KEY}=****"
echo ""
echo "Done!"
echo ""
echo "Please run:  source ${SHELL_CONFIG}"
echo "Then restart Claude Code to take effect."
'''

    output_path = os.path.join(tempfile.gettempdir(), "setup_slack.sh")
    with open(output_path, "w") as f:
        f.write(script_content)
    os.chmod(output_path, 0o755)

    print(json.dumps({
        "script": output_path,
        "message": f"Setup script generated at {output_path}. User should run: bash {output_path}"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
