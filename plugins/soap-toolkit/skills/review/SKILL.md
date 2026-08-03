---
name: review
description: Review current code changes for high-confidence correctness defects, regressions, security risks, and missing critical test coverage without modifying files. Use when the user asks for a code review, change review, diff review, pre-merge check, or an assessment of whether an implementation is safe and correct.
---

# Review

Review the requested changes and report only issues that need correction. Do not modify project files or create review artifacts.

## Scope

1. Read repository instructions and identify the relevant application, package, and project conventions.
2. Use the user-specified files, commit, branch, or diff when provided.
3. Otherwise review the current working tree:
   - Tracked changes from `git diff HEAD`.
   - Untracked files from `git ls-files --others --exclude-standard`.
4. If there are no changes and no explicit scope, ask the user what should be reviewed.
5. Start from the diff, then read only the callers, callees, contracts, schemas, configuration, and tests needed to understand its behavior and impact.

Related files provide context. Do not report unrelated or pre-existing issues unless the current change introduces them, makes them reachable, or materially worsens them.

## Findings

Report an issue only when concrete evidence shows that the change can cause one of the following:

- Incorrect behavior, a broken contract, data loss, or a regression.
- A security or privacy vulnerability.
- Incorrect error, state, concurrency, transaction, or resource handling.
- A material performance regression.
- Missing or ineffective automated coverage for critical behavior when that creates a credible regression risk.

Exclude style preferences, naming improvements, readability cleanup, duplication, abstraction preferences, and behavior-preserving refactors. Those belong to `simplify`.

Keep findings high-confidence and actionable:

- Verify that the affected path is actually reachable.
- Cite the smallest useful repository-relative `file:line`.
- Explain the evidence and user or system impact.
- Run an existing targeted test only when it helps confirm or reject a finding; do not invent test commands.

Sub-agents are optional. Use them only when the scope materially benefits from parallel independent investigation. Never require them or refuse a review because they are unavailable.

## Output

Order findings by impact. Do not add a severity matrix or general summary.

```markdown
## Findings

### `path/to/file.ts:42`
- Issue: [What is wrong.]
- Evidence/Impact: [Why the changed code causes a real problem.]
```

If there are no findings, output:

```markdown
## Findings

No issues requiring correction were found.
```
