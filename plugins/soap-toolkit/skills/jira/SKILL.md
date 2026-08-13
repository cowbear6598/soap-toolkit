---
name: jira
description: "Set up Jira Cloud access and perform focused issue operations: get an issue's title and description, add a comment, transition an issue, or create a subtask. Use when the user asks to configure Jira, read a Jira ticket, comment on it, change its status, or add a child task."
---

# Jira

Perform one requested Jira operation at a time with the scripts in `<skill-dir>/scripts/`:

```bash
python3 <skill-dir>/scripts/get.py ISSUE-123
python3 <skill-dir>/scripts/comment.py ISSUE-123 "Comment text"
python3 <skill-dir>/scripts/transition.py ISSUE-123 "In Progress"
python3 <skill-dir>/scripts/create_subtask.py ISSUE-123 "Subtask title" --description "Optional description"
python3 <skill-dir>/scripts/create_subtask.py ISSUE-123 "Subtask title" --issue-type "Development Subtask"
```

Return the script's JSON result. Run a write only when the user explicitly requests that exact comment, transition, or subtask; resolve ambiguity in the issue key, content, status, or subtask type first. Do not create follow-up operations or transition a parent automatically. Never inspect or expose credentials.

## Setup

When requested or configuration is missing, ask the user to run:

```bash
python3 <skill-dir>/scripts/setup.py
```

The script securely prompts for the Jira URL, email, and API token, then writes `~/.config/soap-toolkit/jira.json` with owner-only permissions. It does not use token environment variables or require a restart.

Use an appropriately restricted Jira account; its API token retains the account's permissions. Create a token at `https://id.atlassian.com/manage-profile/security/api-tokens`. Never ask the user to paste it into the conversation.
