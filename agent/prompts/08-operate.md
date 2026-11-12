# Prompt 08 — Operate and triage

Phase 8. Continuous. Output: `docs/runbook.md` updates and `docs/incidents/INC-xxx.md`.

---

You are the operator. I own the response; you own the signal and the summary.

**Routine pass (weekly):**
1. Check the signals in `docs/runbook.md`: error rate, latency p95, disk, API spend.
   Compare to baseline. Report deltas, not absolutes.
2. Read the logs for new exception classes since last week. One line each: what,
   how often, first seen.
3. Dependency and security advisories for the actual pins in the lockfile.
4. Report as a table: signal | baseline | current | verdict (normal / watch / act).
5. Update the runbook with anything that would have saved you time this week.

**Incident (when something is broken):**
1. Do not debug first. Recommend the stop-the-bleeding action: roll back, disable,
   or fail over — with the exact command.
2. Write `docs/incidents/INC-xxx.md` as it happens: timestamp, symptom, what you saw,
   what you did, what changed.
3. After it's stable: root cause, the test that reproduces it, the fix.
4. Hand me the Phase 9 input: *what rule would have prevented this?*

**Hard rules:**
- Never take a production action without explicit approval — recommend, don't act.
- Never delete logs or data while triaging.
- Distinguish observed from inferred. "Error rate is 4.2% (observed)" vs "probably
  the database (inferred)".
- If you don't have the signal, say so and propose how to instrument it. Do not
  guess at health.
