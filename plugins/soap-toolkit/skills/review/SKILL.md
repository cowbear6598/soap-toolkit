---
name: review
description: Review current code changes for high-confidence correctness defects, regressions, security risks, and missing critical test coverage without modifying files. Use when the user asks for a code review, change review, diff review, pre-merge check, or an assessment of whether an implementation is safe and correct.
---

# Review

Report only issues that require correction. Do not modify files or create review artifacts.

## Scope

- Read repository instructions and relevant project conventions.
- Use the requested files, commit, branch, or diff; otherwise review tracked and untracked working-tree changes.
- If no scope or changes exist, ask what to review.
- Start from the diff and read only the callers, callees, contracts, configuration, and tests needed to determine impact.

Do not report unrelated pre-existing issues unless the change introduces, exposes, or worsens them.

## Findings

Report a finding only when concrete evidence shows reachable incorrect behavior, contract breakage, data loss, regression, security or privacy risk, incorrect state or resource handling, material performance regression, or a critical coverage gap with credible regression risk. Exclude style, naming, readability, duplication, and behavior-preserving cleanup; those belong to `simplify`.

For each finding, cite the smallest useful repository-relative `file:line`, explain the evidence and impact, and run an existing targeted test only when it helps confirm or reject the issue. Order findings by impact.

```markdown
## Findings

### `path/to/file.ts:42`
- Issue: [What is wrong.]
- Evidence/Impact: [Why it causes a real problem.]
```

If none qualify, output `## Findings` followed by `No issues requiring correction were found.`
