---
name: simplify
description: Simplify recently changed code and comments while preserving exact behavior, then run the project's relevant automated tests. Use when the user asks to simplify, clean up, reduce complexity, improve readability, remove duplication or redundant comments, or refine the current implementation without changing requirements.
---

# Simplify

Improve the selected changes without altering observable behavior or creating planning or review artifacts.

## Scope

- Read repository instructions, conventions, test setup, the changed implementation, and only the related code needed to prove equivalence.
- Use a user-specified commit, ref, file, or scope; otherwise use tracked and untracked working-tree changes.
- When using a commit, edit current file versions without reverting later changes. Leave code unchanged when the commit no longer maps safely.
- If no scope or changes exist, ask what to simplify.
- Preserve unrelated user changes and avoid repository-wide refactors.

## Simplify

- Reuse established local helpers instead of duplicating logic.
- Remove unnecessary branching, state, wrappers, indirection, dead code, and provably redundant work.
- Remove comments that restate code. Keep or improve comments only when they explain a non-obvious reason, constraint, tradeoff, or logic that cannot be made self-explanatory safely.
- Keep functions at a coherent abstraction level and improve names or structure when intent becomes clearer.

Preserve public contracts, business rules, outputs, errors, side effects, ordering, timing dependencies, and state transitions. Do not add features, speculative abstractions, or bug fixes. Skip any edit whose equivalence cannot be proven.

## Verify

Review the final diff and run existing automated tests relevant to the changed behavior. Do not invent commands. Fix or revert only simplifications that cause failures; report unavailable coverage clearly.

```markdown
## Simplified

- [Behavior-preserving cleanup.]

## Tests

- `[test command]` — [result]
```

If no safe simplification exists, leave files unchanged and say so.
