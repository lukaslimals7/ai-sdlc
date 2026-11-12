# Specification — <initiative name>

> Status: DRAFT | APPROVED · Version 1.0 · Date: <date>
> Upstream: `intent.md` v1.0 (approved <date>)
> Approved by: Lukas · Bound to: <commit SHA>

## 1. Summary

<Two or three sentences: what this builds, and the shape of the solution.>

## 2. Traceability

Every intent outcome must appear here, or the spec is incomplete.

| Intent outcome | Requirements | Acceptance criteria |
|---|---|---|
| OUT-001 | FR-001, NFR-001 | AC-001 |
| OUT-002 | FR-002 | AC-002 |

## 3. Functional requirements

Each requirement is testable. Use EARS phrasing where it helps:
`WHEN <trigger> THE SYSTEM SHALL <response>`.

- **FR-001** — WHEN <condition> THE SYSTEM SHALL <observable behavior>.
- **FR-002** — WHEN <condition> THE SYSTEM SHALL <observable behavior>.
- **FR-003** — The system SHALL <behavior>.

## 4. Non-functional requirements

- **NFR-001** — Performance: <budget, measured how, on what hardware>
- **NFR-002** — Security: <posture; what is out of bounds>
- **NFR-003** — Reliability: <failure behavior; what the user sees>
- **NFR-004** — Operability: <logs, metrics, runbook needs>

## 5. Architecture

```text
<paste an ASCII diagram: components, data flow, boundaries>
```

| Component | Responsibility | Owns data | Talks to |
|---|---|---|---|
| <name> | <job> | <tables/files> | <other components> |

## 6. Data model

| Entity | Fields | Invariants | Retention |
|---|---|---|---|
| <name> | <fields with types> | <what must always be true> | <policy> |

Migration note: <how schema changes are applied; is it reversible>

## 7. Interfaces

### Internal / API

| Endpoint or function | Input | Output | Errors |
|---|---|---|---|
| <signature> | <shape> | <shape> | <codes and meaning> |

### External dependencies

| Dependency | Version | Why | Fallback if it fails |
|---|---|---|---|
| <name> | <pin> | <reason> | <behavior> |

## 8. Security & privacy

- Trust boundaries: <where untrusted input enters>
- Auth model: <who can do what>
- Data classification: <what is sensitive, where it lives, how it's protected>
- Prompt / input validation: <how untrusted content is handled>
- Secrets: <names only, never values; where they live>
- Out-of-bounds: <what this system must never do>

## 9. AI behavior (if this system uses a model)

- Model(s) and routing: <which model for what, and why>
- Tools available to the model: <list, with permission boundaries>
- Structured output contract: <schema, validation, retry policy>
- Failure modes: <malformed output, timeout, refusal, hallucination — and the response>
- Evaluation: <the test set and the pass threshold>
- Cost ceiling: <per request / per month>

## 10. Acceptance criteria

- **AC-001** — GIVEN <state> WHEN <action> THEN <observable result>. Verified by: `<command>`
- **AC-002** — GIVEN <state> WHEN <action> THEN <observable result>. Verified by: `<command>`

## 11. Decisions (ADR)

### ADR-001 — <decision title>
- **Context:** <what forced a choice>
- **Decision:** <what we chose>
- **Alternatives:** <what we rejected, and why>
- **Consequences:** <what becomes harder>

## 12. Out of scope

- <explicitly not building>
- <explicitly not building>

## 13. Unknowns

| # | Unknown | Handling | Owner | Revisit |
|---|---|---|---|---|
| U-001 | <unknown> | Deferred / Spike / Assumed | <who> | <when> |

## 14. Approval

- [ ] Every OUT mapped to at least one FR
- [ ] Every FR has an AC with a verification command
- [ ] Approved by Lukas, bound to version + commit
