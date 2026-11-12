# REVIEW — TASK-<NNN>

> Reviewer context: cold. This reviewer did not write the code and has no access to
> the builder's reasoning. Verdict is fail-closed.

## 1. What is being reviewed

- Diff: `<git range>`
- Task packet: `docs/tasks/TASK-<NNN>.md`
- Claimed acceptance criteria: AC-<xxx>

## 2. Static security scan (added lines only)

| Check | Result | Detail |
|---|---|---|
| Hardcoded secrets | PASS/FAIL | <line refs> |
| Shell injection (`os.system`, `shell=True`) | PASS/FAIL | |
| `eval` / `exec` on input | PASS/FAIL | |
| SQL string interpolation | PASS/FAIL | |
| Unsafe deserialization (`pickle.loads`) | PASS/FAIL | |
| Path traversal in file ops | PASS/FAIL | |
| Unvalidated external input | PASS/FAIL | |

## 3. Test evidence

| Item | Result |
|---|---|
| Packet verification command | PASS/FAIL — `<cmd>` |
| Full suite | <n passed, n failed> |
| New failures vs baseline | <none | list> |
| New tests actually fail without the fix | <verified | not verified> |

## 4. Spec compliance

| Acceptance criterion | Met? | Evidence |
|---|---|---|
| AC-<xxx> | YES/NO | <file:line or command output> |

Scope check: diff touches only files declared in the packet? **YES / NO** — <if no, list offenders>

## 5. Findings

### Blocking

1. <issue — file:line — why it's wrong — what would fix it>

### Non-blocking suggestions

1. <suggestion>

## 6. Verdict

**PASS / FAIL**

Fail-closed rules applied:
- Any security concern → FAIL
- Any logic error → FAIL
- Cannot parse the diff → FAIL
- Missing test evidence → FAIL
- Scope creep → FAIL

Reviewed by: <reviewer identity / model> · Date: <date>
