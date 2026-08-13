---
name: bug
description: Investigate unexpected software behavior, identify the root cause, and support the conclusion with concrete evidence. Use when the user asks to diagnose, investigate, trace, or explain a bug, error, regression, failing test, or incorrect UI or system behavior.
---

# Bug

Find and prove the root cause without modifying project files or creating investigation artifacts.

## Investigation

- Establish the observed and expected behavior from the request, runtime evidence, and tests.
- Read repository instructions and identify the relevant application or package.
- Trace from the failing action, test, or error through execution, data, and state until actual behavior first diverges from expected behavior.
- For UI symptoms, also inspect render conditions, guards, styling, overlays, focus, and stale state when relevant.
- Ask one focused question only when a missing runtime fact prevents further progress.

Treat a cause as confirmed only when evidence connects the symptom, execution path, divergence, and cause. Cite repository-relative `file:line` locations, tests, logs, stack traces, responses, state values, or reproduction evidence. Verify that searched code is on the affected path; do not present assumptions or possibilities as the root cause.

## Output

```markdown
## Root cause

[Confirmed cause, or state that it is not confirmed.]

## Evidence

- [Evidence and how it supports or limits the conclusion.]
```

If evidence is insufficient, report what is proven and what remains missing. Do not add fixes, plans, or unrelated findings.
