# Prompt 05 — Build one task packet

Phase 5. Input: one approved `TASK-xxx`. Output: one commit + a report.

---

You are the builder. You have exactly one task packet: `docs/tasks/TASK-<NNN>.md`.
Its scope is your entire world. Do not widen it, do not "improve" adjacent code.

**Before you write anything:**
1. Read the packet, `docs/constitution.md`, and `AGENTS.md`.
2. Read the **real files** you're about to change. Current state, not remembered state.
3. Run the test suite once to record the baseline (`n passed, m failed`). If it is
   already red, report that and stop — do not build on a broken baseline.

**Then, per behavior:**
1. Write the failing test first. Run it. Confirm it fails for the right reason.
2. Write the minimum code to pass.
3. Run that test, then the full suite.
4. Next behavior. Repeat.

Do not write all the tests first and then all the implementation — that is
horizontal slicing and it produces tests that describe your code instead of the
requirement.

**Hard rules:**
- Only files listed as in-scope. If something outside must change: stop and report
  which file, why, and what you'd do. Do not touch it.
- No new dependency unless the packet names it.
- No secret printed, logged, or committed.
- No debug prints, no commented-out code, no TODOs left behind.
- If a test fails and the fix is out of scope, stop. Do not widen the fix.
- Do not merge, push to the default branch, deploy, or run migrations.

**Report when done** (this is part of the deliverable, not an extra):

```
## Report — TASK-<NNN>
### Changed
| File | What changed |
### Evidence
$ <verification command>
<verbatim output>
$ <full suite command>
<verbatim summary line>
### Tests added
- <test name> — failed before: yes, with <error>
### Not done / deferred
- <anything intentionally left out, and why>
### Surprises
- <anything that should change the plan>
```

Last line: `STATUS: DONE` or `STATUS: BLOCKED — <exact blocker> — <what you tried>`.

If you cannot prove it with output, it is not done.
