import json
import os
import tempfile


def main() -> None:
    script_content = r'''#!/bin/bash
set -e

echo "=== Jira Setup ==="
echo ""

# Ask for Jira URL
read -p "Jira URL (e.g. https://your-domain.atlassian.net): " jira_url
if [ -z "$jira_url" ]; then
    echo "Error: Jira URL cannot be empty"
    exit 1
fi

# Ask for email
read -p "Jira Email: " jira_email
if [ -z "$jira_email" ]; then
    echo "Error: email cannot be empty"
    exit 1
fi

# Ask for API token (hidden input)
read -sp "Jira API Token: " jira_token
echo ""
if [ -z "$jira_token" ]; then
    echo "Error: API token cannot be empty"
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
if [ -f "$HOME/.bashrc" ] && grep -q "JIRA_URL\|JIRA_EMAIL\|JIRA_API_TOKEN" "$HOME/.bashrc" 2>/dev/null; then
    grep -v "export JIRA_URL=\|export JIRA_EMAIL=\|export JIRA_API_TOKEN=" "$HOME/.bashrc" > "$HOME/.bashrc.tmp"
    mv "$HOME/.bashrc.tmp" "$HOME/.bashrc"
    echo "Cleaned up old entries from ~/.bashrc"
fi

# Remove existing entries (if any)
if grep -q "JIRA_URL\|JIRA_EMAIL\|JIRA_API_TOKEN" "$SHELL_CONFIG" 2>/dev/null; then
    grep -v "export JIRA_URL=\|export JIRA_EMAIL=\|export JIRA_API_TOKEN=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp"
    mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
    echo "Removed existing Jira entries."
fi

# Append new entries
echo "" >> "$SHELL_CONFIG"
echo "# Jira credentials" >> "$SHELL_CONFIG"
echo "export JIRA_URL=${jira_url}" >> "$SHELL_CONFIG"
echo "export JIRA_EMAIL=${jira_email}" >> "$SHELL_CONFIG"
echo "export JIRA_API_TOKEN=${jira_token}" >> "$SHELL_CONFIG"

echo "Written to ${SHELL_CONFIG}:"
echo "  export JIRA_URL=${jira_url}"
echo "  export JIRA_EMAIL=${jira_email}"
echo "  export JIRA_API_TOKEN=****"
echo ""
echo "Done! Restart Claude Code to take effect."
'''

    output_path = os.path.join(tempfile.gettempdir(), "setup_jira.sh")
    with open(output_path, "w") as f:
        f.write(script_content)
    os.chmod(output_path, 0o755)

    print(json.dumps({
        "script": output_path,
        "message": f"Setup script generated at {output_path}. User should run: bash {output_path}"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
