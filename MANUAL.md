# AI SDLC — The Complete Manual

> The operator's handbook for this kit. Read `README.md` for the pitch,
> `sdlc.md` for the phase theory, `roles.md` for the org chart. This file is
> what you open when you are actually running a build and want to know
> exactly what to type, what to expect, and what to do when it goes wrong.

## Who this is for

You are one person building a product, and your AI agent is the engineering
org. You have a git repo, Python 3.8+, and an agent runtime (Hermes, Claude
Code, Codex, OpenCode, Copilot, or a bare chat). This kit gives you the
contract, the artifacts, the prompts, and one script that refuses to let
unapproved or untraceable work move forward.

If you read only one sentence in this manual, read this:

> **Every phase produces a committed artifact. The next phase starts by
> reading it. No phase starts from a conversation.**

That is the whole trick. It is what makes a new agent session, a different
model, or a tired you at 2am resume from the same source of truth.

## The loop at a glance

```text
0 Constitution   once per repo       docs/constitution.md + AGENTS.md
1 Intent         what & why          docs/intent.md          OUT-xxx
2 Spike          kill the unknowns   spikes/NNN/             verdict
3 Spec           testable contract   docs/spec.md            FR/NFR/AC/ADR
4 Plan           ordered packets     docs/plan.md            EN/TASK-xxx
5 Build          agent executes      commit + report         evidence
6 Verify         cold-context review docs/reports/REVIEW-*   PASS/FAIL
7 Release        ship + rollback     docs/releases/vX.Y.Z.md
8 Operate        signals + incidents docs/runbook.md         INC-xxx
9 Learn          amend the rules     constitution + lessons
```

Gate after phases 1, 3, and 4. Independent review after 5. Deploy approval at 7.

---

## Part 1 — Setup

### 1.1 What's in the box

```text
ai-sdlc/
├── README.md          the pitch and the 6-command quickstart
├── MANUAL.md          this file
├── sdlc.md            the ten phases with exit criteria and sources
├── roles.md           who decides what; the agent org chart; weekly rhythm
├── agent/
│   ├── AGENTS.md.template   rules file every agent reads before touching code
│   └── prompts/             01-intent.md … 09-learn.md, one per phase
├── templates/         the nine artifacts you fill in
│   intent · spec · plan · task · spike · review · release · runbook · constitution
├── tools/
│   ├── gate.py               deterministic checker (traceability, approvals, placeholders)
│   ├── new_initiative.py     scaffolds a workspace inside an existing repo
│   └── install_gate_hook.sh  makes the gate a pre-commit hook
└── examples/
    ├── demo-workspace/         a complete, gate-clean initiative
    └── student-ai-scenario.md  a narrative walkthrough: an AI study assistant
                                built end to end with the kit
```

When the templates feel abstract, read `examples/demo-workspace/` — a real
initiative filled in end to end, which passes the gate with 0 errors and
0 warnings. When you want to see the whole journey of a real app, read
`examples/student-ai-scenario.md` — a study assistant built with DeepSeek,
phase by phase, from interview to incident.

### 1.2 Pick your adoption level

**Level 1 — Prompts only.** Copy `agent/prompts/` into your workflow and use
each file as the instruction set for one working session. No scaffolding, no
gate. Good for a first try; you keep the discipline, lose the enforcement.

**Level 2 — Artifacts + gate.** Scaffold a workspace with
`new_initiative.py`, fill the templates, and run `gate.py` before each phase
advance. Good when your runtime has no hook support.

**Level 3 — Full kit (recommended).** Level 2, plus `AGENTS.md` at the repo
root, the pre-commit hook, and a fresh context for every review. This is the
configuration the prompts assume.

### 1.3 Scaffold a workspace

Run this from anywhere; it writes into the target repo.

```bash
python3 /path/to/ai-sdlc/tools/new_initiative.py "quiz-export-offline" \
  --repo ~/Desktop/my-product
```

Real output (paths abbreviated):

```text
create .../docs/constitution.md
create .../docs/intent.md
create .../docs/spec.md
create .../docs/plan.md
create .../docs/REGRESSIONS.md
create .../docs/lessons.md
create .../docs/tasks/
create .../docs/reports/
create .../docs/releases/
create .../docs/decisions/
create .../docs/incidents/
create .../spikes/
create .../AGENTS.md

next:
  1. fill .../docs/intent.md  (prompt: agent/prompts/01-intent.md)
  2. python3 .../tools/gate.py .../docs
```

Rules: it never overwrites an existing file unless you pass `--force`, and it
only creates `AGENTS.md` if the repo doesn't already have one. The slug must
be kebab-case, 2–63 characters.

### 1.4 Wire the agent rules

The scaffold drops a template `AGENTS.md` at the repo root. Edit its
placeholders: what the project is, the map, the commands, where things live,
the hard rules, the known traps, and the verification playbook.

Runtime file names:

| Runtime | Rules file |
|---|---|
| Hermes | `AGENTS.md` (auto-read as project context) |
| Codex | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Other runtimes | check the runtime's convention |

If you use more than one runtime, keep one `AGENTS.md` and symlink the rest:

```bash
ln -s AGENTS.md CLAUDE.md
```

One source of truth. Never maintain two copies.

### 1.5 Make the gate non-optional

A gate you can ignore is a promise. Install it as a pre-commit hook:

```bash
/path/to/ai-sdlc/tools/install_gate_hook.sh ~/Desktop/my-product
```

Real output (paths abbreviated):

```text
installed: .../.git/hooks/pre-commit
gate:      .../tools/gate.py
```

What it does, verified: if `docs/intent.md`, `docs/spec.md`, or `docs/plan.md`
exists, every commit runs the gate first. If the gate exits non-zero, the
commit is blocked:

```text
commit blocked: AI-SDLC artifacts failed the gate.
fix the findings above, or bypass once with: git commit --no-verify
```

It backs up an existing hook to `.git/hooks/pre-commit.backup-<timestamp>`,
and it stays silent on repos with no AI-SDLC workspace. Bypass with
`--no-verify` — but the bypass is the exception, not the workflow.

---

## Part 2 — The loop, phase by phase

### Quick reference

| Phase | You | Agent | Prompt | Artifact | Gate |
|---|---|---|---|---|---|
| 0 Constitution | pick 5–9 principles | nothing | — | `docs/constitution.md`, `AGENTS.md` | you approve |
| 1 Intent | answer ≤3 questions | interviews, drafts | `01-intent.md` | `docs/intent.md` | Approve / Revise / Pause |
| 2 Spike | pick the unknowns | throwaway proof | `02-spike.md` | `spikes/NNN/` | accept verdict |
| 3 Spec | scope & risk calls | writes contract | `03-spec.md` | `docs/spec.md` | approve + bind version |
| 4 Plan | approve sequence | decomposes packets | `04-plan.md` | `docs/plan.md` | approve |
| 5 Build | nothing | test-first, commit | `05-build.md` | commit + report | none (scope-locked) |
| 6 Verify | read verdict + diff | cold-context review | `06-verify.md` | `docs/reports/REVIEW-*` | merge or send back |
| 7 Release | approve deploy | pre-flight, staging | `07-release.md` | `docs/releases/vX.Y.Z.md` | explicit "deploy" |
| 8 Operate | set signals | signal pass, runbook | `08-operate.md` | `docs/runbook.md` | you own response |
| 9 Learn | name the bite | amend rules | `09-learn.md` | constitution + lessons | approve amendment |

### Phase 0 — Constitution (once per repo)

**Goal:** encode the rules that never change, so you never repeat them and the
agent never guesses them.

**You do:** pick 5–9 principles. This is your file; the agent does nothing.

**Artifact:** `docs/constitution.md` + repo-root `AGENTS.md`.

**Done when:** every rule is a prohibition or a command, not a preference.
"You write readable code" is not a rule. "Every new module has a test" is.

**Gate:** you approve it. After that, you edit it only through Phase 9.

### Phase 1 — Intent (per initiative)

**Goal:** agree on the problem before anyone discusses solutions.

**You do:** answer the agent's questions — at most 3 at a time, and only ones
whose answer changes the artifact. This is the highest-leverage 20 minutes in
the cycle.

**Agent does:** reads the repo first, challenges vagueness, drafts
`docs/intent.md`, flags what it assumed.

**Done when:**
- Problem, user, and success signal in one paragraph each.
- At least one measurable outcome (`OUT-xxx`).
- At least 3 non-goals, phrased as things you might plausibly want.
- No architecture, stack, library names, or file paths. If a solution appears
  in intent, send it back.

**Gate:** `Approve | Revise | Pause`. Approval binds to the intent version.

**Watch out for:** writing files before you agree on intent. A beautiful spec
for the wrong problem is the most expensive artifact in the kit.

### Phase 2 — Spike (only when a real unknown could kill the build)

**Goal:** retire the risky assumptions before you commit architecture to them.

**You do:** say which unknowns worry you; pick which spikes to run.

**Agent does:** decomposes the unknowns into 2–5 testable questions, builds a
throwaway proof for the highest-risk one, reports VALIDATED / PARTIAL /
INVALIDATED with observed output.

**Done when:** the question is answered with evidence. "VALIDATED — curl
returns 200 in 340ms" is a verdict. "Looks good" is not.

**Skip when:** the risk is low, or a 10-minute doc read answers it. Spikes are
for unknowns that would change the architecture.

**Watch out for:** spike code leaking into the product. It is throwaway by
design; never merge it, and never let it create a dependency the spec didn't
approve. INVALIDATED is a success — it saved you the build.

### Phase 3 — Spec (per initiative)

**Goal:** turn an approved outcome into a testable contract.

**You do:** make the calls only an owner can make — scope trade-offs, risk
acceptance, "yes SQLite" / "no Postgres".

**Agent does:** writes testable requirements with stable IDs, designs the
architecture, defines data and interfaces, records every material decision as
an ADR, states what is out of scope.

**Done when:**
- Every `OUT-xxx` maps to at least one `FR-xxx`.
- Every `FR-xxx` has an `AC-xxx` with a runnable verification command.
- Every requirement is testable by something you can run.
- Unknowns are `Unknown` / `Deferred` / `Assumed (owner, validation)` — never
  silently assumed.
- Requirements use EARS phrasing where it helps: `WHEN <trigger> THE SYSTEM
  SHALL <response>`. Ban "fast", "user-friendly", "robust", "scalable" unless
  quantified.

**Gate:** approve the spec and bind it to a version + commit SHA.

**Watch out for:** skipping Phase 2. An unspiked architectural assumption is a
bet disguised as a plan.

### Phase 4 — Plan (per initiative)

**Goal:** decide the order of work so each task is small, independent, and
verifiable.

**You do:** approve the sequence and the risk tier. Nothing else.

**Agent does:** inspects the *real* repository, identifies foundations
(`EN-xxx`), decomposes into `TASK-xxx` packets, maps dependencies, proposes
parallel lanes with disjoint write boundaries.

**Done when:**
- Every `FR-xxx` maps to at least one `TASK-xxx` (the gate checks this).
- No task depends on another's unfinished code unless stated.
- Each task is 20–60 minutes of agent time. If it says "and also", split it.
- Each task names one verification command that exits non-zero on failure.
- Each task lists files in scope and files explicitly out of scope.

**Gate:** approve. Approval authorizes implementation of the listed tasks
only — never deploy, prod data, secrets, or external sends.

**Watch out for:** planning on a red baseline. The plan's reality-check table
must be filled from real commands (`git rev-parse HEAD`, the real test
command, actual pass/fail counts).

### Phase 5 — Build (per task packet)

**Goal:** turn an approved task into a committed, tested change.

**You do:** nothing while it runs. This is the phase you delegate hardest.

**Agent does:** reads the packet, the constitution, and `AGENTS.md`; runs the
suite once to record the baseline; writes the failing test first; implements
the minimum to pass; runs the full suite; commits; reports with verbatim
output.

**Artifact:** one commit + `docs/reports/TASK-xxx.md` (what changed, which
files, the verbatim test output, what it did not do).

**Done when:**
- The packet's verification command passes, and you can see the output.
- Full suite still green.
- New behavior has a test that failed before it passed.
- The commit message references the task ID.

**Hard rules the builder must obey:** only files listed as in-scope; no new
dependency unless the packet names it; no secret printed, logged, or
committed; no merge, deploy, or migration.

**Watch out for:** horizontal slicing — writing all tests then all code. It
produces tests that describe the code instead of the requirement. One
behavior at a time.

### Phase 6 — Verify (per task, before merge)

**Goal:** catch what the builder couldn't see. The agent that wrote the code
is the worst reviewer of that code.

**You do:** read the review verdict and the diff, not the code line by line.
You are checking that the *decision* was right, not that the syntax is.

**Agent does (fresh context, never the builder's):** scope check, static
security scan of added lines, evidence check, logic review, spec compliance,
regression comparison. It returns a fail-closed verdict: unparseable or
ambiguous = FAIL.

**Artifact:** `docs/reports/REVIEW-TASK-xxx.md` + CI evidence.

**Done when:** verdict PASS, zero new test failures, no scope creep, every
intended file actually changed.

**Gate:** merge or send it back. Fix cycles are capped at 2 — after that,
something is wrong with the task, not the code. Reopen Phase 4.

**Watch out for:** same-context review. It is theatre. In Hermes, spawn the
reviewer with `delegate_task`; elsewhere, open a separate session.

### Phase 7 — Release (per version)

**Goal:** ship a version you can roll back, with a record of what shipped.

**You do:** approve the deploy. This is the only irreversible gate in the
loop, and it stays yours.

**Agent does:** maps commits to task IDs, runs pre-flight on the exact commit
being released, writes the release doc, deploys to staging, smoke-tests it,
prepares the rollback command. It stays out of prod until you say go.

**Done when:** pre-flight green on the exact commit; rollback written and
rehearsed enough to execute blind; post-release verification steps exist.

**Gate:** explicit "deploy" from you, and you own the rollback decision.

**Watch out for:** shipping a commit that doesn't map to an approved task.
Anything unmapped is a finding — report it, don't ship it silently.

### Phase 8 — Operate (continuous)

**Goal:** know the thing is alive, and catch the failure before a user does.

**You do:** set the signals you care about and the thresholds that make you
act. You own the incident response.

**Agent does:** weekly signal pass (error rate, latency p95, disk, spend),
log review for new exception classes, dependency advisories for the real
pins, runbook updates, incident write-ups.

**Artifact:** `docs/runbook.md` + `docs/incidents/INC-xxx.md`.

**Done when:** you can answer "is it healthy right now?" and "what do I do if
<the most likely failure> happens?" without reading code.

**Watch out for:** acting on production without approval. Recommend, don't
act. And distinguish observed from inferred: "error rate is 4.2% (observed)"
vs "probably the database (inferred)".

### Phase 9 — Learn (per initiative close, and monthly)

**Goal:** convert experience into less work. This is the compounding phase.

**You do:** name the one thing that bit you, and what rule would have
prevented it.

**Agent does:** mines the bug log, incident records, review FAILs, and task
reports; proposes amendments phrased so an agent can obey them without
interpretation; updates the artifacts; checks for rot.

**Done when:** every added rule is traceable to a real incident and is
narrow enough not to forbid something you need.

**Watch out for:** skipping this phase. A system that doesn't amend itself
gets more expensive every month. And when a phase produces bad output, fix
the prompt or template that failed — not just the output.

---

## Part 3 — The gate, in depth

`tools/gate.py` is the deterministic checker. It reads `intent.md`,
`spec.md`, and `plan.md` and exits non-zero when traceability is broken,
approvals are missing, or placeholders are unfilled.

### 3.1 Running it

```bash
python3 tools/gate.py <repo>/docs              # check everything present
python3 tools/gate.py <repo>/docs/intent.md    # or a single file
python3 tools/gate.py <repo>/docs --stage plan # intent|spec|plan|all
python3 tools/gate.py <repo>/docs --json       # machine-readable
```

Exit codes: `0` pass (warnings allowed), `1` errors, `2` usage/IO problem.

Real output on a clean workspace:

```text
AI-SDLC gate
--------------------------------------------------------------
  checked: examples/demo-workspace/intent.md
  checked: examples/demo-workspace/spec.md
  checked: examples/demo-workspace/plan.md

  no findings. traceability complete, artifacts approved.
--------------------------------------------------------------
  0 error(s), 0 warning(s)
```

### 3.2 What it checks

**Intent** (`I` codes)

| Code | Level | Meaning |
|---|---|---|
| I001 | ERROR | no `OUT-xxx` outcomes |
| I002 | ERROR | missing Non-goals section |
| I003 | ERROR | Non-goals section has no bullets |
| I004 | ERROR | unfilled placeholders |
| I005 | ERROR | not approved |

**Spec** (`S` codes)

| Code | Level | Meaning |
|---|---|---|
| S001 | ERROR | no `FR-xxx` requirements |
| S002 | ERROR | intent outcomes not carried into the spec |
| S003 | ERROR | a requirement has no acceptance criterion |
| S004 | ERROR | an acceptance criterion has no verification command |
| S005 | WARN | no "Out of scope" section |
| S006 | WARN | no `NFR-xxx` non-functional requirements |
| S007 | WARN | no decision records (ADR) |
| S008 | ERROR | unfilled placeholders |
| S009 | ERROR | not approved |

**Plan** (`P` codes)

| Code | Level | Meaning |
|---|---|---|
| P001 | ERROR | no `TASK-xxx` packets |
| P002 | ERROR | requirements with no planned work |
| P003 | ERROR | a task has no verification command |
| P004 | ERROR | a task is not tied to an `FR`/`NFR` |
| P005 | WARN | a task has no rollback note |
| P006 | ERROR | unfilled placeholders |
| P007 | ERROR | not approved |

**Other**

| Code | Level | Meaning |
|---|---|---|
| X001 | ERROR | a stage file required by `--stage` is missing |

### 3.3 Approval detection

The gate looks for two lines anywhere in the artifact:

```text
Status: APPROVED
Approved by: Lukas
```

`Status:` must contain `APPROVED` and must not contain `NOT APPROVED`.
`Approved by:` must be a real name — not `<name>`, not `pending`, not `n/a`.

When you fill a template, replace the whole header line, not just the word
`DRAFT`. The scaffolded template line is `Status: DRAFT | APPROVED · ...`;
edit it to `Status: APPROVED · Version 1.0 · ...` and fill the date and
approver.

### 3.4 Placeholder detection

The gate flags `<anything in angle brackets>`, plus `TODO`, `TBD`, `FIXME`,
and `XXX`. This is stricter than it looks, and it caught a real mistake when
this manual was verified:

```text
ERROR P006  1 unfilled placeholder(s) in plan
      line 62: <sha> -- - Rollback command: `git revert <sha> && ./deploy.sh`
```

The fix is to write the command concretely, the way the demo does:
`git revert` the release commit, then redeploy.

Escape hatch: put `gate:allow-placeholder` on a line to skip the check for
that line. Use it sparingly, never in an approved artifact.

### 3.5 What the gate does NOT check

Be honest about the boundary:

- It checks `intent.md`, `spec.md`, and `plan.md` only. Spikes, task packet
  files, build reports, review reports, releases, runbooks, and
  `REGRESSIONS.md` are disciplined by prompts, templates, and your review —
  not by the script.
- It checks text, not truth. It can verify that every `FR` has an `AC`; it
  cannot verify that the `AC` means anything. That is what your approval is
  for.
- It does not run your tests. It checks that you named a command that would.

### 3.6 Warnings policy

Warnings (S005–S007, P005) do not block. They are the future errors. Clear
them at Phase 9; don't let them become a permanent background hum.

---

## Part 4 — The artifacts

### 4.1 Template reference

| Template | Phase | Produces | Key fields |
|---|---|---|---|
| `intent.md` | 1 | `docs/intent.md` | problem, who, `OUT-xxx`, success signal, non-goals, assumptions |
| `spike.md` | 2 | `spikes/NNN-*/README.md` | question, why it matters, risk, approach, result, verdict |
| `spec.md` | 3 | `docs/spec.md` | traceability, `FR`/`NFR`, architecture, data model, security, `AC`, `ADR` |
| `plan.md` | 4 | `docs/plan.md` | reality check, `EN-xxx` foundations, `TASK-xxx` packets, coverage, lanes |
| `task.md` | 4–5 | `docs/tasks/TASK-xxx.md` | goal, satisfies, in/out scope, verification command, rollback |
| `review.md` | 6 | `docs/reports/REVIEW-TASK-xxx.md` | security scan, evidence, spec compliance, verdict |
| `release.md` | 7 | `docs/releases/vX.Y.Z.md` | scope, pre-flight, deploy, smoke, rollback, notes |
| `runbook.md` | 8 | `docs/runbook.md` | access, health check, operations, signals, troubleshooting |
| `constitution.md` | 0, 9 | `docs/constitution.md` | principles, rules, quality bar, invariants, definition of done, amendment log |

### 4.2 The ID system

Stable IDs are what make the chain checkable. Once an artifact is approved,
keep its IDs stable; renumbering breaks traceability.

| Prefix | Meaning | Lives in |
|---|---|---|
| `OUT-NNN` | outcome | intent |
| `FR-NNN` | functional requirement | spec |
| `NFR-NNN` | non-functional requirement | spec |
| `AC-NNN` | acceptance criterion | spec |
| `ADR-NNN` | decision record | spec |
| `U-NNN` | unknown | spec |
| `A-NNN` | assumption | intent |
| `EN-NNN` | foundation (enabling work) | plan |
| `TASK-NNN` | task packet | plan, `docs/tasks/` |
| `INC-NNN` | incident | `docs/incidents/` |
| `vX.Y.Z` | release | `docs/releases/` |

The chain the gate enforces: `OUT → FR → AC` and `FR/NFR → TASK`.

### 4.3 Where everything lives

```text
<repo>/
├── AGENTS.md                 agent rules, read before touching code
├── docs/
│   ├── constitution.md       the rules that never change
│   ├── intent.md             what & why (approved)
│   ├── spec.md               the contract (approved)
│   ├── plan.md               the order (approved)
│   ├── REGRESSIONS.md        every fixed bug, one line each
│   ├── lessons.md            Phase 9 output
│   ├── tasks/                TASK-xxx.md packets
│   ├── reports/              TASK-xxx.md build reports, REVIEW-TASK-xxx.md
│   ├── releases/             vX.Y.Z.md
│   ├── decisions/            ADRs, if you split them out
│   └── incidents/            INC-xxx.md
└── spikes/                   NNN-*/ throwaway proofs
```

---

## Part 5 — Running the agent

### 5.1 Four roles, four contexts

The agent org is four functions, each run as a **separate context** so nobody
grades their own homework:

| Role | Phases | Output |
|---|---|---|
| Planner | 1–4 | intent, spec, plan |
| Builder | 5 | commit + tests |
| Reviewer | 6 | verdict + evidence |
| Operator | 7–8 | release notes, runbook, alerts |

The builder's context is contaminated by the intent of the code; the
reviewer's must not be. Same separation everywhere.

### 5.2 Runtime recipes

**Hermes** (the runtime this kit was built on):

```bash
# one-shot phase prompt
hermes chat -q "$(cat agent/prompts/03-spec.md)"

# separate contexts per role — the important one:
# hand the prompt to delegate_task for planner, builder, and reviewer alike
```

`AGENTS.md` at the repo root is auto-read as project context.

**Claude Code:** paste the prompt into a session. For Phase 6, open a separate
session — never the builder's. Symlink `CLAUDE.md → AGENTS.md`.

**Codex:** `AGENTS.md` is read automatically. Separate sessions for review.

**OpenCode / Copilot / any chat UI:** paste the prompt; keep the artifacts in
the repo so the context is reproducible. The prompts are runtime-agnostic.

### 5.3 Prompt mechanics

1. Read the prompt file for the phase.
2. Paste it into a fresh session (or hand it to `delegate_task`).
3. The agent reads the repo first — every prompt says so.
4. It drafts the artifact and ends with `STATUS: READY FOR HUMAN REVIEW` or
   `STATUS: NOT READY — <blocker>`.
5. You reply `Approve`, `Revise: <change>`, or `Pause`.
6. Run the gate.
7. Commit the artifact.

### 5.4 Model tiering

- **Strong model** for phases 1, 3, 4, 6 — judgment-heavy stages where a wrong
  answer is expensive.
- **Cheap model** for mechanical work: boilerplate, test scaffolding,
  refactors, doc summaries, and most of phase 5.

### 5.5 Parallel lanes

Run independent tasks in parallel only when they have **disjoint write
boundaries**. One git worktree per lane, serial merge, gate on the merged
tree:

```bash
git worktree add ../wt-a -b lane-a
git worktree add ../wt-b -b lane-b
# ... build in each ...
git checkout main
git merge lane-a && git merge lane-b
```

If two tasks write the same file, they are serial, not parallel. The demo
plan's "no parallel lanes" section is the honest answer more often than you'd
think.

### 5.6 The supervision budget

Your attention is the scarce resource. Assume **~15 minutes of real review
per task packet**, once or twice a day. That single number sizes everything:

- A packet's diff must be reviewable in 10 minutes.
- A run's report must be skimmable in 3 minutes.
- If a packet needs more, it isn't one packet — split it.

If you catch yourself merging diffs you didn't read, you have silently become
a rubber stamp. That is worse than no review, because it manufactures
confidence you haven't earned.

---

## Part 6 — A verified worked run

This is a real initiative I ran in a scratch repo to verify this manual. It is
small on purpose: one endpoint, one outcome, one task.

### 6.1 Scaffold

```bash
python3 tools/new_initiative.py "verify-manual" --repo ./target
```

### 6.2 Fill the three artifacts

`docs/intent.md` — one problem, one outcome, three non-goals, one assumption:

```markdown
## 3. Outcome
- **OUT-001** — `GET /health` returns HTTP 200 with `{"status": "ok"}` in under
  100 ms p95, and the deploy pipeline can gate on it.

## 6. Non-goals
- No database or dependency checks; a failing database must not fail liveness.
- No authentication or rate limiting on the endpoint.
- No metrics or Prometheus exposition.
```

`docs/spec.md` — one FR, one NFR, one AC with a runnable command, one ADR:

```markdown
| Intent outcome | Requirements | Acceptance criteria |
|---|---|---|
| OUT-001 | FR-001, NFR-001 | AC-001 |

- **FR-001** — WHEN a client sends `GET /health`, THE SYSTEM SHALL return HTTP 200
  with body `{"status": "ok"}` and content type `application/json`.
- **AC-001** — GIVEN the app is running WHEN `GET /health` is requested THEN the
  response is 200 with `{"status": "ok"}`. Verified by: `pytest tests/test_health.py -q`
```

`docs/plan.md` — one task packet, one verification command, one rollback:

```markdown
### TASK-001 — Add the health endpoint and its test
- **Satisfies:** FR-001, NFR-001, AC-001
- **Risk tier:** T1
- **Files in scope:** `app/main.py`, `tests/test_health.py`
- **Verification command:** `pytest tests/test_health.py -q`
- **Rollback:** `git revert` the commit
```

### 6.3 The gate caught a real mistake

First run:

```text
ERROR P006  1 unfilled placeholder(s) in plan
      line 62: <sha> -- - Rollback command: `git revert <sha> && ./deploy.sh`
```

I had written `<sha>` as shorthand. The gate reads text literally, so it
flagged it. Fixed by writing the command concretely.

### 6.4 Clean pass

```text
AI-SDLC gate
--------------------------------------------------------------
  checked: .../docs/intent.md        (paths abbreviated)
  checked: .../docs/spec.md
  checked: .../docs/plan.md

  no findings. traceability complete, artifacts approved.
--------------------------------------------------------------
  0 error(s), 0 warning(s)
```

### 6.5 The gate refuses a tampered artifact

Change one word in the approved plan:

```bash
sed -i 's/^> Status: APPROVED/> Status: DRAFT/' plan.md
python3 tools/gate.py .
```

```text
ERROR P007  plan is not approved (Status is 'DRAFT · Version 1.0 · Date: 2026-11-10')
```

### 6.6 The hook blocks a commit

With the workspace unfilled (placeholders everywhere), a commit is refused:

```text
commit blocked: AI-SDLC artifacts failed the gate.
fix the findings above, or bypass once with: git commit --no-verify
```

`git commit --no-verify` works — which is why the bypass must stay an
exception, not a habit.

---

## Part 7 — Operating cadence

### 7.1 Weekly rhythm

| When | What | Time |
|---|---|---|
| Monday | Pick one initiative. Intent → Spec approval. | 45–90 min |
| Tuesday | Plan approval. Launch 2–4 builder runs in parallel lanes. | 30 min |
| Wednesday | Review verdicts, merge, or send back. Launch next batch. | 30 min |
| Thursday | Second batch. Release when green. | 30 min |
| Friday | Operate review: signals, incidents, dependency updates. Phase 9 lessons. | 45 min |

Total: roughly 4–5 hours of deliberate work per week. Everything else is the
agent running while you do something else. If you're spending 30 hours a week
in this system, you're not delegating — you're babysitting.

### 7.2 Risk tiers decide how much you review

| Tier | What it covers | Your review |
|---|---|---|
| T0 | Docs, comments, formatting, scripts | spot-check |
| T1 | Isolated feature code, own module | verdict + diff skim |
| T2 | Shared contracts, APIs, schema, CI config | full diff read |
| T3 | Auth, money, secrets, PII, migrations, prod config | full diff + explicit approval |
| T4 | Deploy, prod data, external sends, deletion | you execute or explicitly authorize, always |

Autonomy expands only by risk tier. For T3 work, mandatory human review and
security review apply, no exceptions.

### 7.3 The escalation rule

The agent stops and asks when it hits:

- a contradiction between two approved artifacts,
- a requirement it cannot test,
- a file outside its packet that it believes must change,
- a failing test it cannot fix within scope,
- any action that is irreversible, external, or touches production.

It does **not** escalate for uncertainty it can resolve by reading more code,
a failing lint it can fix, a missing test it can write, or a dependency bump
it can test in isolation. Over-escalation is as expensive as
under-escalation — it turns you into a ticket queue.

### 7.4 Regression discipline

Every fix keeps a test in `tests/` and gets a line in `docs/REGRESSIONS.md`,
formatted: symptom → root cause → fix → standing rule. Every fix ships with
the failing-test-first proof. Never regress working behaviour.

### 7.5 Cost discipline

Cheap models for mechanical work. Strong models for phases 1, 3, 4, 6. The
stages where a wrong answer is expensive are exactly the stages where you use
the expensive model.

### 7.6 Context hygiene

Keep `AGENTS.md` short and current. Put the map in `spec.md`, the order in
`plan.md`, the history in `docs/`. Your agent should read files, not need the
conversation. Never paste a whole file into chat to explain it — that is a
stale copy waiting to poison the next session.

---

## Part 8 — Troubleshooting

**The fresh scaffold fails the gate with dozens of errors.**
Expected. The scaffold is a template, not a pass. Fill the artifacts; the
gate is telling you what "filled" means.

**The gate passes but the work is wrong.**
The gate checks traceability and approval, not truth. It cannot know whether
your acceptance criterion means anything. Your approval is the control —
which is why approval is a human act, not a formality.

**The agent keeps editing files outside its packet.**
Check the packet's "Files out of scope" list is explicit. The reviewer FAILs
scope creep automatically. If it keeps happening, the packets are too big.

**The review keeps failing.**
Two fix cycles maximum. After that, reopen Phase 4: the task is wrong, not
the code. Split it or rewrite the acceptance criteria.

**I'm spending hours in the kit.**
The kit became the work. Ship. The artifacts are meant to be cheap; if
writing them costs more than the feature, the feature is too small for the
kit.

**The agent approved its own work.**
It must never. The builder cannot mark a task done without a passing
verification command, and the reviewer must be a fresh context. If you catch
a session reviewing its own diff, discard the review.

**Docs disagree with the code.**
Phase 9's rot check exists for exactly this. Flag it, fix the docs, and add
the rule that would have prevented it.

**Warnings pile up and I ignore them.**
They are the future errors. Clear them at Phase 9.

**I want a second initiative in the same repo.**
Finish one before starting the next, or move each initiative into its own
subdirectory (`docs/<slug>/intent.md`, etc.) and point the gate at that
subdirectory. The gate resolves `intent.md`/`spec.md`/`plan.md` relative to
whatever directory you hand it.

**I want to change a template.**
Edit the file in `templates/` in your fork. New initiatives pick it up;
existing workspaces are untouched. If a phase keeps producing bad output,
fix the prompt or template — that is a Phase 9 amendment.

---

## Part 9 — Adapting and extending the kit

**Add a gate check.** Edit `tools/gate.py`: add a `Finding` in the relevant
`check_*` function, following the existing level/code/message/detail shape.
Keep the exit-code semantics: errors block, warnings don't.

**Add a prompt.** Drop `agent/prompts/NN-name.md` in the same style: goal,
rules, process, output format, final `STATUS:` line.

**Change the ID scheme.** The regexes are at the top of `gate.py`
(`ID_RE`). Change them there and in the templates together.

**Fork it.** The kit is designed to be yours. Keep a `CHANGELOG.md` in your
fork so the next you knows what changed.

---

## Appendix A — Quick reference card

```bash
# scaffold a workspace in an existing repo
python3 tools/new_initiative.py "<slug>" --repo <repo>

# gate: traceability, approvals, placeholders
python3 tools/gate.py <repo>/docs
python3 tools/gate.py <repo>/docs --stage plan
python3 tools/gate.py <repo>/docs --json

# make the gate a pre-commit hook
./tools/install_gate_hook.sh <repo>
```

The law: **every phase produces a committed artifact; the next phase starts
by reading it.**

The seven rules:

1. One packet, one commit, one review.
2. The reviewer is never the builder.
3. Deterministic checks beat model opinion.
4. Approval binds to a version.
5. Autonomy scales with reversibility.
6. Every fix leaves a test and a line in `docs/REGRESSIONS.md`.
7. Phase 9 is not optional.

Approval format the gate accepts:

```text
Status: APPROVED · Version 1.0 · Date: 2026-11-13
Approved by: Lukas
```

---

## Appendix B — Error code index

| Code | Artifact | Level | Fix |
|---|---|---|---|
| I001 | intent | ERROR | add `OUT-xxx` outcomes |
| I002 | intent | ERROR | add a Non-goals section |
| I003 | intent | ERROR | give Non-goals real bullets |
| I004 | intent | ERROR | fill every `<placeholder>` |
| I005 | intent | ERROR | set `Status: APPROVED` and `Approved by:` |
| S001 | spec | ERROR | add `FR-xxx` requirements |
| S002 | spec | ERROR | carry every `OUT-xxx` into the spec |
| S003 | spec | ERROR | pair every `FR` with an `AC` |
| S004 | spec | ERROR | give every `AC` a verification command |
| S005 | spec | WARN | add an "Out of scope" section |
| S006 | spec | WARN | add `NFR-xxx` requirements |
| S007 | spec | WARN | add an ADR |
| S008 | spec | ERROR | fill every `<placeholder>` |
| S009 | spec | ERROR | set `Status: APPROVED` and `Approved by:` |
| P001 | plan | ERROR | add `TASK-xxx` packets |
| P002 | plan | ERROR | give every `FR` a task |
| P003 | plan | ERROR | give every task a verification command |
| P004 | plan | ERROR | tie every task to an `FR`/`NFR` |
| P005 | plan | WARN | add a rollback note |
| P006 | plan | ERROR | fill every `<placeholder>` |
| P007 | plan | ERROR | set `Status: APPROVED` and `Approved by:` |
| X001 | any | ERROR | create the missing stage file |

---

## Appendix C — The files, one line each

| File | What it is |
|---|---|
| `README.md` | the pitch and the 6-command quickstart |
| `MANUAL.md` | this handbook |
| `sdlc.md` | the ten phases with exit criteria and sources |
| `roles.md` | who decides what; the agent org chart; weekly rhythm |
| `agent/AGENTS.md.template` | rules file every agent reads before touching code |
| `agent/prompts/01-intent.md` | Phase 1 prompt |
| `agent/prompts/02-spike.md` | Phase 2 prompt |
| `agent/prompts/03-spec.md` | Phase 3 prompt |
| `agent/prompts/04-plan.md` | Phase 4 prompt |
| `agent/prompts/05-build.md` | Phase 5 prompt |
| `agent/prompts/06-verify.md` | Phase 6 prompt (fresh context) |
| `agent/prompts/07-release.md` | Phase 7 prompt |
| `agent/prompts/08-operate.md` | Phase 8 prompt |
| `agent/prompts/09-learn.md` | Phase 9 prompt |
| `templates/*.md` | the nine artifacts |
| `tools/gate.py` | deterministic checker |
| `tools/new_initiative.py` | workspace scaffolder |
| `tools/install_gate_hook.sh` | pre-commit hook installer |
| `examples/demo-workspace/` | a complete, gate-clean initiative |

---

*Verified against Python 3.14.9 on 2026-11-13: the demo workspace passes the
gate with 0 errors and 0 warnings; a tampered plan fails with P007; a fresh
scaffold reports its unfilled placeholders; and the pre-commit hook blocks an
unfilled workspace while `--no-verify` bypasses it.*

*This kit is MIT licensed — see `LICENSE`. Use it, fork it, amend it.*
