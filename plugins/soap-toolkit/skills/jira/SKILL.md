---
name: jira
description: "Set up Jira Cloud access and perform focused issue operations: get an issue's title and description, add a comment, transition an issue, or create a subtask. Use when the user asks to configure Jira, read a Jira ticket, comment on it, change its status, or add a child task."
---

# Jira

Perform one explicit Jira operation at a time. Do not combine these scripts into automatic subtasks, checklist, review, or status-change flows.

## Operations

Replace `<skill-dir>` with this skill's absolute directory.

```bash
# Get title and description
python3 <skill-dir>/scripts/get.py ISSUE-123

# Add one comment
python3 <skill-dir>/scripts/comment.py ISSUE-123 "Comment text"

# Transition by transition name or target status
python3 <skill-dir>/scripts/transition.py ISSUE-123 "In Progress"

# Create one subtask
python3 <skill-dir>/scripts/create_subtask.py ISSUE-123 "Subtask title" \
  --description "Optional description"

# Select a type when the project has multiple subtask types
python3 <skill-dir>/scripts/create_subtask.py ISSUE-123 "Subtask title" \
  --issue-type "Development Subtask"
```

Return the script's JSON result. Never inspect, print, or echo the credential file.

Run a write operation only when the user explicitly requests that exact comment, transition, or subtask. Resolve any ambiguity in the issue key, content, target status, or subtask type before executing it. Do not transition a parent automatically after creating or commenting on an issue.

## Set up access

When setup is requested or any operation reports that configuration is missing, tell the user to run this in their own terminal:

```bash
python3 <skill-dir>/scripts/setup.py
```

The script prompts for the Jira URL, email, and API token, hides the token input, and writes:

```text
~/.config/soap-toolkit/jira.json
```

It applies owner-only permissions and does not modify shell profiles. No Codex restart is required; retry the requested operation after setup.

The API token retains the permissions of its Jira account. Store it securely and use an appropriately restricted account.

Create an API token at:

```text
https://id.atlassian.com/manage-profile/security/api-tokens
```

Never ask the user to paste a token into the conversation.
