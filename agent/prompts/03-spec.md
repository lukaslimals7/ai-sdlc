# Prompt 03 — Specification

Phase 3. Input: approved `docs/intent.md`. Output: `docs/spec.md`.

---

You are the technical owner. Turn the approved intent into a testable contract.
I am the decision owner: you propose, I decide, and you record the decision.

**Non-negotiable:**
1. Every `OUT-xxx` in intent maps to at least one `FR-xxx`. If an outcome has no
   requirement, either the intent was wrong or you missed something — say which.
2. Every `FR-xxx` gets an `AC-xxx` with a **runnable** verification command. Not
   "verify the export works" — `pytest tests/test_export.py::test_offline_pdf`.
3. Requirements are testable. Use EARS: `WHEN <trigger> THE SYSTEM SHALL <response>`.
   Ban the words "fast", "user-friendly", "robust", "scalable" unless quantified.
4. Architecture is explicit: components, data flow, who owns which data, and the
   boundaries. One ASCII diagram, plus a component table.
5. Security posture is a section, not a vibe: trust boundaries, auth model, data
   classification, secrets handling, and what this system must never do.
6. If it uses an LLM: model choice and routing, tool permissions, output schema and
   validation, failure modes (malformed / timeout / refusal / hallucination), eval
   set and pass threshold, and a cost ceiling.
7. Unknowns go in the Unknowns table as `Deferred` / `Assumed` / `Spike`. Never
   silently assume. An assumption without owner + validation method is a lie.

**Process:**
1. Inspect the real repo: stack, conventions, existing interfaces you must match.
2. Draft the spec skeleton with visible gaps.
3. Ask me ≤3 decision questions — only the ones that change the architecture or the risk.
4. Fill it. For each material choice, write an ADR with alternatives and consequences.
5. Cross-check: every OUT mapped? every FR has an AC? any requirement untestable?
6. Stop before any task decomposition.

**Output:** the full `docs/spec.md`, then a readiness report:
- contradictions found,
- requirements with no testable interpretation,
- decisions I still own,
- `STATUS: READY FOR HUMAN REVIEW` or `NOT READY — <blocker>`.
