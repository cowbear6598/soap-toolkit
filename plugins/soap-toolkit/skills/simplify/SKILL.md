---
name: simplify
description: Simplify recently changed code while preserving its exact behavior, then run the project's relevant automated tests. Use when the user asks to simplify, clean up, reduce complexity, improve readability, remove duplication, or refine the current implementation without changing requirements.
---

# Simplify

Improve the current changes directly while preserving their observable behavior. Do not create planning or review artifacts.

## Scope

1. Read repository instructions and identify the relevant application, package, conventions, and test setup.
2. When the user provides a commit or ref, inspect that commit's patch and use its changed code as the scope.
3. Otherwise use other user-specified files or changes when explicitly provided.
4. If there is no explicit scope, use the current working tree diff:
   - Tracked changes from `git diff HEAD`.
   - Untracked files from `git ls-files --others --exclude-standard`.
5. If there are no changes and no explicit scope, ask the user what should be simplified.
6. Read the changed implementation plus the smallest useful set of related callers, contracts, helpers, and tests before editing.

Preserve unrelated user changes. Do not expand the task into a repository-wide refactor.

When a commit is the scope, apply simplifications to the current file versions without reverting changes made after that commit. If the commit's code can no longer be mapped safely to the current tree, leave it unchanged and report the limitation.

## Simplify

Apply only high-confidence, behavior-preserving improvements through these lenses:

- **Reuse:** Prefer an existing local helper or abstraction over newly duplicated logic.
- **Simplification:** Remove unnecessary branching, state, wrappers, indirection, dead code, and noise comments.
- **Efficiency:** Avoid provably redundant work only when execution order, side effects, and error semantics remain unchanged.
- **Altitude:** Keep each function at a coherent abstraction level; move low-level mechanics out of orchestration code only when an established project boundary supports it.

Improve names and structure when they make intent clearer, but optimize for clarity rather than the fewest lines.

## Guardrails

- Preserve public contracts, business rules, output, errors, side effects, ordering, timing dependencies, and state transitions.
- Do not add features or speculative abstractions.
- Do not turn the task into bug fixing. If a possible defect prevents a safe cleanup, leave that code unchanged and report the concern.
- Skip any edit whose behavior cannot be proven equivalent from the implementation and tests.
- Do not overwrite or revert changes outside the selected scope.

## Verify

After editing:

1. Review the resulting diff and confirm every edit belongs to the cleanup.
2. Discover and run the existing automated tests relevant to the changed behavior.
3. Do not invent a test command. If no relevant automated test exists or a test cannot run, state that clearly.
4. If verification fails because of the simplification, fix or revert only the failing simplification before handing off.

## Output

```markdown
## Simplified

- [Behavior-preserving cleanup that was applied.]

## Tests

- `[test command]` — [result]
```

If no safe simplification is available, do not modify files and say so.
