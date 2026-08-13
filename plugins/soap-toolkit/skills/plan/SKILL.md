---
name: plan
description: Inspect the current codebase, discuss every unresolved requirement or technical concern with the user, and create a minimal implementation plan. Use when the user asks to discuss a change, clarify a feature, design an implementation, or create or update a plan before coding.
---

# Plan

Create and refine a repository-grounded plan without implementing it.

## Plan file

Derive an English kebab-case slug and immediately create:

```text
.soap/tasks/<slug>/plan.yaml
```

Never overwrite an unrelated plan. Update an existing directory only when the user refers to it; otherwise append `-2`, `-3`, and so on. Initialize the file with exactly these keys:

```yaml
description: >
  Explain the current problem or opportunity, why the change is needed, and
  the value the intended outcome provides.
goal:
  - Add the user-visible outcome.
related:
  - src/path/affected-file.ts
verify:
  - npm test -- src/path/feature.spec.ts
```

`description` must be a non-empty string. `goal`, `related`, and `verify` must be lists; add no other keys or nested task tracking.

## Ground the plan

- Read repository instructions, relevant configuration, entry points, call paths, contracts, tests, and established patterns before finalizing goals.
- Record affected and useful reference files under `related` using repository-relative paths. Include new paths only when existing conventions support them.
- Write outcomes rather than implementation steps under `goal`.
- Put only confirmed, relevant automated test commands under `verify`; exclude manual checks, acceptance criteria, lint, typecheck, and build commands. Use `verify: []` when none exist and tell the user.
- Reuse facts and paths already discovered during the same planning session.

Ask one focused question whenever an unresolved assumption, ambiguity, tradeoff, compatibility concern, or verification gap could change the plan. Explain two or three concrete options and recommend one when alternatives exist. Update the YAML with confirmed facts before pausing; do not store unanswered questions or conversation history in it.

Before handoff, read the complete YAML and confirm its schema, motivation, outcome-oriented goals, grounded paths, supported test commands, and absence of hidden unresolved concerns. Report the path and resolved goals without pasting the whole file unless asked.
