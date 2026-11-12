# Plan — <initiative name>

> Status: DRAFT | APPROVED · Version 1.0 · Date: <date>
> Upstream: `spec.md` v1.0 (approved, bound to <commit SHA>)
> Baseline observed at: `git rev-parse HEAD` = <SHA>, working tree <clean/dirty>
> Approved by: Lukas

## 1. Repository reality check (agent fills this from the real repo, not memory)

| Fact | Observed | Command used |
|---|---|---|
| Default branch | <branch> | `git branch --show-current` |
| Test command | `<cmd>` | <ran it? output summary> |
| Suite status at baseline | <x passed, y failed> | `<cmd>` |
| Lint / typecheck | `<cmd>` or none | <status> |
| Files that must change | <paths> | `rg -l <pattern>` |
| Files that must NOT change | <paths> | — |

## 2. Foundations (what must exist first)

Work that unlocks other work. Nothing in this list is parallelizable; it's the spine.

| ID | Foundation | Unlocks | Verify by |
|---|---|---|---|
| EN-001 | <schema / interface / scaffold> | TASK-002, TASK-003 | `<command>` |

## 3. Task packets

One packet = one commit = one review = 20–60 minutes of agent time.

### TASK-001 — <short imperative title>

- **Satisfies:** FR-001, AC-001
- **Risk tier:** T0 | T1 | T2 | T3
- **Depends on:** none | TASK-000
- **Files in scope:** `path/a.py`, `path/b.js`
- **Files out of scope (must not change):** everything else, specifically `path/c.py`
- **Acceptance:**
  - [ ] <observable behavior 1>
  - [ ] <observable behavior 2>
- **Verification command:** `<exact command that exits non-zero on failure>`
- **Rollback:** `git revert <sha>` — <any state to restore>
- **Estimate:** <20–60 min>

### TASK-002 — <title>

- **Satisfies:** FR-002, AC-002
- **Risk tier:** T1
- **Depends on:** TASK-001
- **Files in scope:** `<paths>`
- **Files out of scope:** —
- **Acceptance:**
  - [ ] <behavior>
- **Verification command:** `<exact command>`
- **Rollback:** `git revert <sha>`
- **Estimate:** <min>

## 4. Coverage check

Every FR must appear in at least one packet.

| Requirement | Tasks |
|---|---|
| FR-001 | TASK-001 |
| FR-002 | TASK-002 |
| NFR-001 | TASK-003 (measured) |

## 5. Parallel lanes (optional)

Only lanes with disjoint write boundaries. Each lane gets its own worktree.

| Lane | Tasks | Worktree | Write boundary | Merge order |
|---|---|---|---|---|
| A | TASK-001 | `../wt-a` | `app/a/` | 1 |
| B | TASK-002 | `../wt-b` | `static/b/` | 2 |

Serial merge. Rebase before merge. Gate script runs on the merged tree.

## 6. Verification strategy

| Layer | Command | When |
|---|---|---|
| Unit | `<cmd>` | every packet |
| Integration | `<cmd>` | before merge |
| Security scan | `<cmd>` | before merge |
| Manual smoke | <steps> | before release |

## 7. Rollout & rollback

- Rollout: <staging → prod, feature flag, canary, or straight swap>
- Rollback command: `<exact command>`
- Data impact: <none | migration X, reversible by Y>
- Kill switch: <how to disable without a deploy, if applicable>

## 8. Approval

- [ ] Every FR has at least one task
- [ ] No task depends on unstated work
- [ ] Every task names a verification command
- [ ] Rollback written and executable
- [ ] Approved by Lukas (authorizes implementation of these tasks only)
