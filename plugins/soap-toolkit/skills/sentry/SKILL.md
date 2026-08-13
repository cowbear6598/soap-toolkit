---
name: sentry
description: Set up read-only Sentry credentials and retrieve an issue plus its latest event evidence by shortId. Use when the user asks to configure Sentry access, inspect a Sentry issue, fetch error details or stack traces, or provides a Sentry shortId to investigate.
---

# Sentry

Retrieve one issue and its latest event without searching broadly or modifying Sentry:

```bash
python3 <skill-dir>/scripts/get.py PROJECT-123
```

Use returned issue metadata, exceptions, stack frames, source context, request details, environment, release, transaction, and tags as evidence. Never inspect or expose credentials or a full event user object.

## Setup

When requested or configuration is missing, ask the user to run:

```bash
python3 <skill-dir>/scripts/setup.py
```

The script securely prompts for an auth token and organization slug, accepts `--base-url` for regional or self-hosted installations, and writes `~/.config/soap-toolkit/sentry.json` with owner-only permissions. It does not use token environment variables or require a restart.

Use a token with `event:read` access; see `https://docs.sentry.io/api/auth/`. Never ask the user to paste it into the conversation.
