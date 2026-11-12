# Plan — Bulk student result import

> Status: APPROVED · Version 1.0 · Date: 2026-11-10
> Upstream: `spec.md` v1.0 (approved, bound to commit 4f2a91c)
> Baseline observed at: `git rev-parse HEAD` = 4f2a91c, working tree clean
> Approved by: Lukas

## 1. Repository reality check

| Fact | Observed | Command used |
|---|---|---|
| Default branch | main | `git branch --show-current` |
| Test command | `pytest tests/ -q` | ran it: 58 passed, 0 failed |
| Suite status at baseline | 58 passed, 0 failed | `pytest tests/ -q` |
| Lint / typecheck | `ruff check .` clean | `ruff check .` |
| Files that must change | `app/routers/results.py`, `app/models.py`, `app/db.py` | `rg -l "results"` |
| Files that must NOT change | `app/services/deepseek.py`, `static/js/app.js`, `app/auth/` | — |

## 2. Foundations

| ID | Foundation | Unlocks | Verify by |
|---|---|---|---|
| EN-001 | `ImportLog` table plus idempotent migration hook | TASK-002, TASK-003 | `pytest tests/test_models.py -q` |

## 3. Task packets

### TASK-001 — Add ImportLog model and migration hook

- **Satisfies:** NFR-004
- **Risk tier:** T2
- **Depends on:** none
- **Files in scope:** `app/models.py`, `app/db.py`
- **Files out of scope:** everything else, specifically `app/routers/results.py`
- **Acceptance:**
  - [ ] `ImportLog` exists with the fields in spec section 6
  - [ ] Existing databases gain the table without data loss
- **Verification command:** `pytest tests/test_models.py -q`
- **Rollback:** `git revert` the commit; drop `import_log` if already applied
- **Estimate:** 25 min

### TASK-002 — Pure import service: parse, validate, match

- **Satisfies:** FR-001, FR-003
- **Risk tier:** T2
- **Depends on:** TASK-001
- **Files in scope:** `app/services/import_results.py`, `tests/test_import_results.py`
- **Files out of scope:** routers, templates, `static/`
- **Acceptance:**
  - [ ] Valid rows produce Attempt objects
  - [ ] Invalid rows raise RowError with a row number and reason
  - [ ] No student name or roll number is written to the logger
- **Verification command:** `pytest tests/test_import_results.py -q`
- **Rollback:** `git revert` the commit; remove the module and its tests
- **Estimate:** 45 min

### TASK-003 — Import endpoint with transaction and row cap

- **Satisfies:** FR-002, FR-004, NFR-001, NFR-003
- **Risk tier:** T3
- **Depends on:** TASK-002
- **Files in scope:** `app/routers/results.py`, `tests/test_import_results.py`
- **Files out of scope:** `app/services/import_results.py` except the public functions
- **Acceptance:**
  - [ ] 200 for a valid file, with counts and per-row errors
  - [ ] 413 before any write when rows exceed 60
  - [ ] 404 for a quiz the session user does not own
  - [ ] Re-import is idempotent and reports unchanged rows
  - [ ] A 60-row import completes under 3 seconds in the test
- **Verification command:** `pytest tests/test_import_results.py -q`
- **Rollback:** `git revert` the commit; the route disappears, the table stays
- **Estimate:** 50 min

### TASK-004 — Import panel in Class Progress

- **Satisfies:** FR-003
- **Risk tier:** T1
- **Depends on:** TASK-003
- **Files in scope:** `templates/dashboard.html`, `static/js/app.js`, `static/css/app.css`
- **Files out of scope:** all backend files
- **Acceptance:**
  - [ ] File picker posts to the import endpoint with the selected quiz
  - [ ] Success shows counts; failures list row number and reason
  - [ ] Failures are visually prominent, not a toast that disappears
  - [ ] Keyboard reachable, no layout break at 360px width
- **Verification command:** `node --check static/js/app.js`
- **Rollback:** `git revert` the commit
- **Estimate:** 40 min

## 4. Coverage check

| Requirement | Tasks |
|---|---|
| FR-001 | TASK-002 |
| FR-002 | TASK-003 |
| FR-003 | TASK-002, TASK-004 |
| FR-004 | TASK-003 |
| NFR-001 | TASK-003 |
| NFR-003 | TASK-003 |
| NFR-004 | TASK-001 |

## 5. Parallel lanes

None. All four packets touch the results path or its tests, so they serialise. The
frontend packet cannot start until the endpoint's response shape is frozen, which is
why TASK-003 is a hard dependency rather than a parallel lane.

## 6. Verification strategy

| Layer | Command | When |
|---|---|---|
| Unit | `pytest tests/test_import_results.py -q` | every packet |
| Integration | `pytest tests/ -q` | before merge |
| Security scan | `rg -n "logger\..*(roll|name)" app/` returns nothing | before merge |
| Manual smoke | import a 3-row file in the browser, check the class table | before release |

## 7. Rollout and rollback

- Rollout: deploy to staging, import the sample file, verify counts, then production.
- Rollback command: `git revert` the release commit and redeploy; `import_log` is
  additive and may be left in place.
- Data impact: additive table plus new Attempt rows for a quiz; reverting the code
  leaves imported attempts in place, which is the intended behavior.
- Kill switch: the UI panel can be hidden by reverting TASK-004 alone, leaving the
  endpoint available for direct use.

## 8. Approval

- [x] Every FR has at least one task
- [x] No task depends on unstated work
- [x] Every task names a verification command
- [x] Rollback written and executable
- [x] Approved by Lukas
