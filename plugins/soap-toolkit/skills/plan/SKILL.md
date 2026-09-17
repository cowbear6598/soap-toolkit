---
name: plan
description: Create a minimal, repository-grounded implementation plan when explicitly invoked. Do not use for general discussion or implementation.
---

# Plan

Inspect the current implementation and write a persistent plan directly. Do not implement the planned change.

## Create the plan

Derive an English kebab-case slug and immediately create:

```text
.soap/tasks/<slug>/plan.yaml
```

Never overwrite an unrelated plan. Update an existing directory only when the user refers to it; otherwise append `-2`, `-3`, and so on.

Use these required keys:

```yaml
description: >
  Explain the current problem or opportunity, why the change is needed, and
  the value the intended outcome provides.
goal:
  - Add the user-visible outcome.
constraints: []
related:
  - src/path/affected-file.ts
verify:
  - npm test -- src/path/feature.spec.ts
```

When supplied by the user, add either or both company metadata fields before `description` and preserve their values as strings:

```yaml
branch: "feature/PROJ-123-change"
issue-number: "PROJ-123"
```

Do not request, infer, or add these metadata fields when they are absent. `description` must be a non-empty string. `goal`, `constraints`, `related`, and `verify` must be lists. Add no other keys or nested task tracking.

## Ground the plan

- Read repository instructions, relevant configuration, entry points, call paths, contracts, tests, and established patterns before finalizing the plan.
- Write outcomes rather than implementation steps under `goal`. For frontend changes, describe the rendered state, user interaction, and observable result when they matter to the feature.
- Record only confirmed implementation boundaries under `constraints`; do not invent preferences or exclusions. Use `constraints: []` when none are known.
- Record affected and useful reference files under `related` using repository-relative paths. Include new paths only when existing conventions support them.
- Put only confirmed, relevant automated test commands under `verify`; exclude manual checks, acceptance criteria, lint, typecheck, and build commands.
- Reuse facts and paths already discovered during the same planning session.

For frontend end-to-end verification, choose the smallest command scoped to the affected feature, such as a single spec, test title, tag, or project. Never substitute the full frontend end-to-end suite unless the user explicitly requests it. If no targeted frontend command can be confirmed, omit it; use `verify: []` and tell the user only when no other relevant automated test command exists.

When the user supplies a reference image and viewport for frontend verification:

- Save the image under `.soap/tasks/<slug>/assets/` with a stable descriptive filename.
- Add the saved repository-relative image path to `related`.
- Record the exact viewport under `constraints`.
- Use the targeted frontend end-to-end command in `verify` to cover both the relevant interaction result and visual comparison. A screenshot comparison does not replace assertions for the post-interaction state.

Do not ask for a reference image or viewport merely because a task touches the frontend.

## Resolve only blocking uncertainty

Discussion is not a required phase. When the request and repository provide enough information, finish the plan without asking questions.

Ask one focused question only when an unresolved issue would materially change the scope or user-visible outcome, or would prevent an accurate plan. Explain two or three concrete options and recommend one when alternatives exist. Update the YAML with confirmed facts before pausing; do not store unanswered questions or conversation history in it.

## Validate and hand off

Before handoff, read the complete YAML and confirm:

- It contains the five required keys and only the optional `branch` and `issue-number` metadata when supplied.
- Its description explains the motivation and intended value.
- Its goals are outcomes, its constraints are confirmed, and its paths are grounded in the repository.
- Every verification entry is a supported, relevant automated test command, with frontend end-to-end commands scoped to the affected feature.
- No unresolved concern remains hidden in the plan.

Report the plan path and resolved goals without pasting the whole file unless asked. State when `verify` is empty.
