# Intent — Bulk student result import

> Status: APPROVED · Version 1.0 · Owner: Lukas · Date: 2026-11-09
> Approved by: Lukas · Approved at: commit 4f2a91c

## 1. Problem

Teachers currently enter quiz results one attempt at a time through the report card
form. A class of 40 students with 3 quizzes each is 120 manual entries, and teachers
report abandoning the Class Progress feature after the first quiz because the entry
cost exceeds the value of the analysis. The data exists in the student HTML reports
already; it is the transfer into the app that is expensive.

## 2. Who it's for

The teacher who already generated quizzes through Gyaanix and now wants class-level
analysis without retyping scores.

## 3. Outcome

- **OUT-001** — A teacher can import one class's results for one quiz in under 2
  minutes, for a class of up to 60 students, without retyping any score.
- **OUT-002** — Import rejects malformed rows with a per-row message instead of
  partially importing silently, so the class table never contains corrupted scores.

## 4. Success signal

Measured on the next 5 real class imports: median time from file selection to
completed import under 120 seconds, and zero support reports of a score appearing
against the wrong student. Both measured from the import log (timestamp pairs) and
the incident log.

## 5. Scope

In:
- A CSV import path for one quiz and one class.
- Row-level validation with a readable error report.
- Idempotent re-import of the same file.

## 6. Non-goals

Out — and we will say no to these even when they are easy:

- No Excel, Google Sheets, or PDF parsing. CSV only, in this version.
- No import of question banks or lesson plans. Results only.
- No automatic student account matching by fuzzy name. Exact roll number or email only.
- No editing of imported scores inside the import screen; that stays in the existing
  report view.

## 7. Constraints

| Type | Constraint |
|---|---|
| Time | 3 working days of agent time, 2 hours of Lukas time |
| Tech | Must run inside the existing FastAPI + SQLModel app; SQLite only; no new service |
| Money | No new paid dependency |
| Legal / policy | Student names and roll numbers are minor PII: no logging of row contents |

## 8. Assumptions (with owner + validation)

| # | Assumption | Impact if wrong | How we'll validate | Owner |
|---|---|---|---|---|
| A-001 | Teachers can produce a CSV with roll number and score columns | Feature has no input path | Ask 3 teachers to export from their existing marks sheet | Lukas |
| A-002 | Roll numbers are unique within a class in practice | Wrong-student attribution, the worst failure mode | Check 2 real class lists for duplicates | Lukas |

## 9. Open questions

- [x] Which column identifies a student — roll number or email? Decided: roll number,
  with email accepted as a fallback column.
- [ ] Does the school year boundary create duplicate roll numbers? Deferred to Phase 3
  (spec must state the uniqueness scope).

## 10. Approval

- [x] Approved by decision owner (Lukas)
- [x] Bound to version 1.0
