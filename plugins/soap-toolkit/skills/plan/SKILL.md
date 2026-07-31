---
name: plan
description: Inspect the current codebase, discuss every unresolved requirement or technical concern with the user, and create a minimal implementation plan. Use when the user asks to discuss a change, clarify a feature, design an implementation, or create or update a plan before coding.
---

# Plan

Create one persistent plan immediately, ground it in the current implementation, and refine it through discussion. Do not implement the planned code.

## Workflow

### 1. Create the plan

Derive an English kebab-case slug from the requested change.

Write the plan to:

```text
.soap/tasks/<slug>/plan.yaml
```

Create the directory and file before investigating or discussing. Initialize `description` plus the three list fields immediately. Draft the motivation already clear from the request, add known goals, and leave facts not yet verified out until they are confirmed.

Never overwrite an unrelated plan. If the inferred directory already exists:

- Update it only when the user explicitly refers to that existing plan.
- Otherwise use `<slug>-2`, `<slug>-3`, and so on until the directory is unused.

### 2. Inspect the current implementation

Before finalizing any goal:

- Read repository instructions and relevant project configuration.
- Search for the user-facing flow, entry points, call paths, data contracts, tests, and established patterns related to the request.
- Read the relevant implementation instead of inferring it from filenames.
- Record affected files and useful reference files under `related` as repository-relative paths.
- Inspect project configuration and existing test files to identify the real automated test commands relevant to the change.
- Reuse discovered paths during the same planning session instead of searching for them again without cause.

### 3. Discuss uncertainty

Do not guess. Ask the user whenever any unconfirmed assumption, ambiguity, tradeoff, or concern could affect the description, goals, related files, behavior, scope, compatibility, or verification.

Ask one focused question at a time. When alternatives exist, present two or three concrete options, explain the tradeoff, and state a recommendation.

Continue without asking only when the feature, purpose, expected behavior, technical boundary, and verification are all clear from the request and inspected code.

Update `plan.yaml` with facts that have already been established before pausing for an answer. Do not store the conversation or unanswered questions in the YAML.

### 4. Refine the plan

Keep the YAML as a top-level mapping with exactly these four keys. `description` must be a non-empty string; the other three values must be lists:

```yaml
description: >
  The current flow does not support the required user behavior. This feature is
  needed to close that gap while preserving the conventions already used by the
  surrounding implementation.
goal:
  - Add the user-visible outcome.
  - Preserve the established behavior that must not regress.
related:
  - src/path/affected-file.ts
  - src/path/reference-file.ts
verify:
  - npm test -- src/path/feature.spec.ts
  - npm run test:e2e -- feature
```

Apply these rules:

- `description`: Explain the current problem or opportunity, why the change is needed, and the value the feature should provide. Write cohesive context, not implementation steps.
- `goal`: List outcomes, not detailed implementation steps or a procedural checklist. Put each independent outcome in its own list entry.
- `related`: List both files expected to change and files that an implementer should consult, including relevant test files. Use repository-relative paths. Include a planned new path only when existing conventions support it.
- `verify`: List only automated project test commands confirmed from the repository's configuration and test setup. Do not include user flows, acceptance criteria, manual checks, lint, typecheck, or build commands. Never invent a test command.
- Keep `verify: []` when the project has no relevant automated tests, and state that limitation to the user outside the YAML.
- Add no other keys, nested plan items, metadata, IDs, phases, status, approval fields, or progress tracking.

### 5. Validate and hand off

Before reporting completion:

- Read the complete YAML.
- Confirm the document has exactly `description`, `goal`, `related`, and `verify`.
- Confirm `description` is a non-empty string that explains both the motivation and expected value.
- Confirm `goal`, `related`, and `verify` are lists.
- Confirm every goal list entry is an outcome rather than a sequence of steps.
- Confirm related paths come from inspected code or an established path convention.
- Confirm every verification entry is an automated test command supported by the project's configuration.
- Confirm no unresolved concern remains hidden in the plan.

Report the plan path and summarize the resolved goals. Do not paste the whole YAML unless the user asks.
