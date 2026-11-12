# Specification — Bulk student result import

> Status: APPROVED · Version 1.0 · Date: 2026-11-10
> Upstream: `intent.md` v1.0 (approved 2026-11-09)
> Approved by: Lukas · Bound to: commit 4f2a91c

## 1. Summary

Adds a CSV import path to the Class Progress module. The teacher uploads one file for
one quiz; the server validates every row, matches students by roll number, writes
attempt records, and returns a per-row report. Re-importing the same file is
idempotent.

## 2. Traceability

| Intent outcome | Requirements | Acceptance criteria |
|---|---|---|
| OUT-001 | FR-001, FR-002, NFR-001 | AC-001, AC-002 |
| OUT-002 | FR-003, FR-004 | AC-003, AC-004 |

## 3. Functional requirements

- **FR-001** — WHEN a teacher uploads a CSV with a header row containing `roll_no` and
  `score`, THE SYSTEM SHALL create one attempt record per valid row for the selected
  quiz.
- **FR-002** — WHEN an uploaded file has more than 60 data rows, THE SYSTEM SHALL
  reject the file before writing any record.
- **FR-003** — WHEN a row is invalid (missing roll number, non-numeric score, score
  outside 0 to 100, unknown roll number), THE SYSTEM SHALL skip that row, continue
  processing the rest, and return the row number with a reason.
- **FR-004** — WHEN the same file is uploaded twice for the same quiz, THE SYSTEM SHALL
  produce the same final state and report the rows as unchanged.

## 4. Non-functional requirements

- **NFR-001** — Performance: a 60-row file completes in under 3 seconds on the
  existing 2 vCPU VM, measured by a timing assertion in the integration test.
- **NFR-002** — Security: student names and roll numbers never appear in application
  logs; only counts and row numbers are logged.
- **NFR-003** — Reliability: a failure mid-import leaves the database unchanged
  (single transaction).
- **NFR-004** — Operability: the import result is written to `docs/REGRESSIONS.md`-style
  audit table `import_log` with timestamp, quiz id, row counts, and outcome.

## 5. Architecture

```text
Browser (Class Progress view)
  |  multipart POST /api/classes/{class_id}/import?quiz_id=...
  v
FastAPI router: app/routers/results.py::import_results
  |  validate header -> stream rows -> build Attempt objects
  v
services/import_results.py   (pure functions: parse_row, validate_row, match_student)
  |
  v
SQLModel session (one transaction) -> Attempt rows + ImportLog row
```

| Component | Responsibility | Owns data | Talks to |
|---|---|---|---|
| results router | HTTP surface, auth, response shaping | none | service, db |
| import service | parse, validate, match, dedupe | none | db session |
| `attempts` table | one row per student per quiz | attempt data | — |
| `import_log` table | audit of each import run | audit data | — |

## 6. Data model

| Entity | Fields | Invariants | Retention |
|---|---|---|---|
| `Attempt` (existing) | id, quiz_id, student_id, score, taken_at | one row per (quiz_id, student_id) | existing policy |
| `ImportLog` (new) | id, class_id, quiz_id, filename_hash, rows_total, rows_ok, rows_failed, created_at | append-only | 12 months |
| `Student` (existing) | id, class_id, roll_no, email | roll_no unique per class | existing policy |

Migration note: additive table only, via `_run_light_migrations()`. No column changes,
so `create_all` plus the idempotent ALTER helper is sufficient and reversible by
dropping `import_log`.

## 7. Interfaces

### Internal / API

| Endpoint or function | Input | Output | Errors |
|---|---|---|---|
| `POST /api/classes/{class_id}/import` | multipart file + `quiz_id` | 200 with `{rows_total, rows_ok, rows_failed, errors:[{row, reason}]}` | 400 bad header, 404 unknown quiz, 413 over 60 rows, 422 no valid rows |
| `parse_row(line: str) -> dict` | raw CSV line | normalized dict | raises `RowError(reason)` |
| `validate_row(row, students) -> Attempt` | normalized dict | Attempt | raises `RowError` |

### External dependencies

| Dependency | Version | Why | Fallback if it fails |
|---|---|---|---|
| stdlib `csv` | Python 3.11+ | no new dependency for parsing | not applicable |

## 8. Security & privacy

- Trust boundaries: the uploaded file is untrusted input; the CSV header and every
  cell are validated before use.
- Auth model: only an authenticated teacher may import into a class they own; the
  class id is checked against the session user, not trusted from the form.
- Data classification: student names and roll numbers are minor PII. Stored as
  today; never logged, never included in error messages returned to the browser.
- Prompt / input validation: no LLM in this path.
- Secrets: none introduced. Existing `DEEPSEEK_API_KEY` is untouched by this feature.
- Out-of-bounds: this feature must never send student data to an external service,
  and must never accept a file larger than 1 MB.

## 9. AI behavior

Not applicable: this feature performs no model calls. The existing AI analysis of
class performance is unchanged and reads the same `Attempt` rows.

## 10. Acceptance criteria

- **AC-001** — GIVEN a 40-row CSV for a quiz with 40 enrolled students WHEN the teacher
  imports it THEN 40 attempts exist and the response reports 40 ok, 0 failed.
  Verified by: `pytest tests/test_import_results.py::test_happy_path_40_rows`
- **AC-002** — GIVEN a 61-row CSV WHEN imported THEN the response is 413 and no
  Attempt row is created. Verified by: `pytest tests/test_import_results.py::test_rejects_over_60`
- **AC-003** — GIVEN a CSV with 3 malformed rows among 10 valid ones WHEN imported
  THEN 10 attempts are created and the response lists the 3 row numbers with reasons.
  Verified by: `pytest tests/test_import_results.py::test_partial_invalid_rows`
- **AC-004** — GIVEN the same valid file imported twice WHEN the second import runs
  THEN the attempt count is unchanged and the response reports rows as unchanged.
  Verified by: `pytest tests/test_import_results.py::test_idempotent_reimport`

## 11. Decisions (ADR)

### ADR-001 — Row-level partial import instead of all-or-nothing
- **Context:** Teachers' real marks sheets contain a few bad rows; rejecting the whole
  file forces manual cleanup before any value is delivered.
- **Decision:** Import valid rows, report invalid ones, never fail silently.
- **Alternatives:** all-or-nothing (safer, but blocks the feature on data hygiene the
  teacher cannot fix quickly).
- **Consequences:** the response must be explicit about what was written; the UI must
  show failures prominently or a teacher will assume everything imported.

### ADR-002 — Match on roll number only, no fuzzy name matching
- **Context:** Wrong-student attribution is the worst failure mode and is invisible
  in aggregate numbers.
- **Decision:** Exact roll number within class; email accepted as an explicit
  alternative column; no fuzzy matching, ever.
- **Alternatives:** fuzzy name match (convenient, unacceptable risk).
- **Consequences:** some files will fail to match and require a corrected export.

## 12. Out of scope

- Excel, Sheets, PDF inputs.
- Importing question banks, lesson plans, or quiz definitions.
- Editing imported scores in the import view.
- Cross-class or cross-year imports.

## 13. Unknowns

| # | Unknown | Handling | Owner | Revisit |
|---|---|---|---|---|
| U-001 | Roll numbers repeating across school years | Assumed unique per class; validation rejects duplicates within a file | Lukas | after 5 real imports |

## 14. Approval

- [x] Every OUT mapped to at least one FR
- [x] Every FR has an AC with a verification command
- [x] Approved by Lukas, bound to version + commit
