# Worked example — bulk student result import

A complete, approved initiative for Gyaanix Teacher-AI, filled in end to end. Use it
when the templates feel abstract: read `intent.md` → `spec.md` → `plan.md` in order
and notice what each phase refuses to contain.

- `intent.md` — one problem, two measurable outcomes, four non-goals, two assumptions
  with validation methods. No architecture, no stack, no tasks.
- `spec.md` — OUT→FR traceability, four FRs with EARS phrasing, four NFRs, one ASCII
  architecture diagram, data model with invariants, a security section that names the
  PII rule, four ACs each with a runnable pytest selector, two ADRs.
- `plan.md` — a reality-check table filled from real git/test commands, one
  foundation, four task packets (one at T3), a coverage table, no parallel lanes
  (correctly, because all packets touch the same path), rollout + rollback.

Verify it yourself:

```bash
python3 ../tools/gate.py .
# 0 error(s), 0 warning(s)
```

Then tamper with it and watch the gate refuse:

```bash
sed -i 's/^> Status: APPROVED/> Status: DRAFT/' plan.md
python3 ../tools/gate.py .        # P007: plan is not approved
```

What to copy from this example: the *shape* of the acceptance criteria (GIVEN/WHEN/
THEN plus a command), the risk tiers (T2 for the model/migration, T3 for the endpoint
that writes student data), and the honesty of the plan's "no parallel lanes" section.
What not to copy: the domain specifics.
