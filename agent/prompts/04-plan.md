# Prompt 04 — Plan and task packets

Phase 4. Input: approved `docs/spec.md` + the real repo. Output: `docs/plan.md`.

---

You are the planning owner. Produce an execution order where every task is small,
independent, and verifiable. Do not write feature code.

**Step 0 — Reality check, before planning anything.**
Fill the "Repository reality check" table from actual commands:
`git rev-parse HEAD`, `git status --short`, the real test command, and its current
pass/fail counts. If the suite is already failing, say so and stop — planning on a
red baseline is fiction.

**Step 1 — Foundations.** What must exist before anything else (schema, interface,
scaffold)? Those are `EN-xxx` and they are serial.

**Step 2 — Task packets.** Decompose the remaining work into `TASK-xxx`. Each must have:
- the `FR-xxx` / `AC-xxx` it satisfies,
- a risk tier (T0 docs → T3 auth/money/PII/migrations),
- files **in** scope and files explicitly **out** of scope,
- observable acceptance criteria,
- **one** verification command that exits non-zero on failure,
- a rollback note,
- an estimate of 20–60 minutes.

Rules for splitting:
- If a task says "and also", split it.
- If two tasks write the same file, they are serial, not parallel.
- If a task cannot be verified by a command, the requirement is underspecified —
  send it back to the spec instead of inventing a task.

**Step 3 — Coverage table.** Every `FR-xxx` maps to at least one task. List any
requirement with no work, and any work with no requirement.

**Step 4 — Parallel lanes.** Only disjoint write boundaries. Propose lanes, worktree
names, merge order. Serial merge, rebase before merge.

**Step 5 — Rollout and rollback.** For the whole initiative: the deploy path, the
rollback command, data impact, and a kill switch if applicable.

**Output:** the full `docs/plan.md`, then:
- requirements with no task,
- tasks with hidden dependencies,
- the two or three tasks you're least sure about and why,
- `STATUS: READY FOR HUMAN REVIEW`.

Approval authorizes implementation of these packets only — never deploy, prod data,
or external actions.
