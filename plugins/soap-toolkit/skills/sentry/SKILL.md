---
name: sentry
description: Set up read-only Sentry credentials and retrieve an issue plus its latest event evidence by shortId. Use when the user asks to configure Sentry access, inspect a Sentry issue, fetch error details or stack traces, or provides a Sentry shortId to investigate.
---

# Sentry

Retrieve one Sentry issue and its latest event by shortId. Do not search broadly, resolve, assign, comment on, or otherwise modify issues.

## Get an issue

Run:

```bash
python3 <skill-dir>/scripts/get.py PROJECT-123
```

Replace `<skill-dir>` with this skill's absolute directory. Use the returned issue metadata, exception mechanism, stack frames, source context, request method and URL, environment, release, transaction, and tags as investigation evidence.

Do not inspect, print, or echo the credential file. Do not expose a Sentry event's full user object.

## Set up access

When setup is requested or `get.py` reports that configuration is missing, tell the user to run this in their own terminal:

```bash
python3 <skill-dir>/scripts/setup.py
```

The script prompts for an auth token and organization slug. It hides the token input and accepts `--base-url` for regional or self-hosted Sentry installations. It writes:

```text
~/.config/soap-toolkit/sentry.json
```

It applies owner-only permissions and does not modify shell profiles. No Codex restart is required; retry `get.py` after setup.

Use a token with `event:read` access. See:

```text
https://docs.sentry.io/api/auth/
```

Never ask the user to paste a token into the conversation.
