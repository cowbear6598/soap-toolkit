---
name: bug
description: Investigate unexpected software behavior, identify the root cause, and support the conclusion with concrete evidence. Use when the user asks to diagnose, investigate, trace, or explain a bug, error, regression, failing test, or incorrect UI or system behavior.
---

# Bug

Find the root cause and prove it with evidence. Investigate only: do not modify project files or create investigation artifacts.

## Investigate

1. Establish the observed symptom and expected behavior from the request, available runtime data, and existing tests.
2. Read repository instructions and identify the relevant application, service, or package before narrowing the search.
3. Start from the user action, failing test, error boundary, or other entry point tied to the symptom.
4. Follow the execution, data, and state path until locating where actual behavior first diverges from expected behavior.
5. Check UI state, render conditions, validation, disabled or loading guards, styling, overlays, focus behavior, and stale cache when the data path alone does not explain a UI symptom.
6. Ask one focused question only when a missing runtime fact or reproduction condition prevents further investigation.

## Evidence standard

- Treat a cause as confirmed only when the evidence connects the symptom, execution path, divergence, and cause.
- Cite concrete evidence such as repository-relative `file:line` locations, failing tests, logs, stack traces, network responses, state values, or reproducible behavior.
- Verify search results belong to the execution path that produces the reported symptom.
- Do not present assumptions or a list of possible causes as the root cause.
- If the available evidence is insufficient, state that the root cause is not confirmed. Report what is proven and what evidence is still missing.

## Output

```markdown
## Root cause

[State the confirmed cause, or state that the root cause is not confirmed.]

## Evidence

- [Concrete evidence with its source and how it proves or constrains the conclusion.]
```

Do not add implementation steps, remediation guidance, planning suggestions, or unrelated findings.
