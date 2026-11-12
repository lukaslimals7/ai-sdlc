# Constitution — <project name>

> Ratified <date> · Version 1.0 · Owner: Lukas
> Amended only through Phase 9 (Learn). Every amendment cites the incident that caused it.

## 1. Principles (why we build the way we build)

1. <Principle — one sentence, a trade-off you're willing to pay for>
2. <Principle>
3. <Principle>

## 2. Non-negotiable rules (agents must obey verbatim)

Each rule is a prohibition or an imperative. No adjectives, no aspirations.

- Every new behavior ships with a test that failed before it passed.
- No secret, token, or key is ever printed, logged, or committed.
- No change is marked done without a verbatim passing command in the report.
- No file outside the task packet's declared scope is edited.
- No dependency is added without a stated reason and a lockfile diff.
- No production, migration, deletion, or external send without explicit approval.
- <Add project-specific ones: tenancy, PII handling, offline behavior, ...>

## 3. Quality bar

| Dimension | Bar | Enforced by |
|---|---|---|
| Tests | <coverage or behavior rule> | <command> |
| Lint / types | clean | <command> |
| Security | no new findings | <command / review> |
| Performance | <budget, e.g. p95 < 400ms> | <measurement> |
| Accessibility | <e.g. keyboard + contrast> | <check> |

## 4. Architecture invariants

Things that must remain true, or the system has changed shape without permission.

- <e.g. The app is single-tenant; one SQLite file per deployment.>
- <e.g. All AI calls go through services/<x>.py; no router calls a provider directly.>
- <e.g. The frontend is vanilla JS with no build step.>

## 5. Definition of done (any task)

- [ ] Acceptance criteria in the packet are satisfied
- [ ] The packet's verification command passes (output pasted in the report)
- [ ] Full suite still green; no regressions
- [ ] Reviewer verdict PASS (cold context)
- [ ] Regression entry added if a bug was fixed
- [ ] Docs updated if behavior or setup changed

## 6. Amendment log

| Date | Change | Trigger (incident / lesson) |
|---|---|---|
| <date> | v1.0 ratified | initial |
