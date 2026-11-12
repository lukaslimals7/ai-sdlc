# The AI SDLC — Top to Bottom

A one-man-team operating system. You are the whole company; the agent is the whole
engineering org. This document is the spine: ten phases, each with an artifact,
a gate you own, and a prompt you can hand the agent.

Read `README.md` first for the operating model and `roles.md` for who does what.

---

## The loop

```text
0 Constitution → 1 Intent → 2 Spike → 3 Spec → 4 Plan → 5 Build → 6 Verify → 7 Release → 8 Operate → 9 Learn
       ↑                                                                                        │
       └──────────────────────── constitution + specs updated from lessons ─────────────────────┘
```

Phases 0, 3, 4 are where you spend your thinking. Phases 5–8 are where the agent
earns its keep. Phase 9 is the one everybody skips and the one that makes the
fifth feature cheaper than the first.

**The one-sentence law of this system:**

> Every phase produces a committed artifact. The next phase starts by reading it.
> No phase starts from a conversation.

That is the whole trick. It works because it works for humans too — the artifact
is the memory, so a new agent session, a different model, or a tired you at 2am
all resume from the same source of truth.

---

## Phase 0 — Constitution (once per repo)

**Goal:** encode the rules that never change, so you never repeat them and the agent
never guesses them.

**You do once:** pick the principles. 5–9 bullets. No more.

**Agent does:** nothing. This is your file.

**Artifact:** `docs/constitution.md` + repo-root `AGENTS.md` (the file every agent
reads first — see `agent/AGENTS.md.template`).

**Exit criteria:** every rule is a prohibition or a command, not a preference.
"You write readable code" is not a rule. "Every new module has a test" is.

**Gate:** you approve it. Then you stop editing it except through Phase 9.

---

## Phase 1 — Intent (per initiative)

**Goal:** agree on the problem before anyone discusses solutions. One sentence: what
problem, for whom, and what changes if we fix it.

**You do:** answer the agent's questions. The agent asks; you decide. This is the
highest-leverage 20 minutes in the entire cycle — a wrong intent costs 10x more
than a wrong implementation.

**Agent does:** interviews you, challenges vagueness, drafts `intent.md`, flags
what it assumed.

**Artifact:** `docs/intent.md` with stable IDs — `OUT-001`, `OUT-002` for outcomes,
and an explicit Non-goals section.

**Exit criteria:**
- Problem, user, and success signal stated in one paragraph each.
- At least one measurable outcome (`OUT-xxx`).
- Non-goals listed (the thing that kills scope creep).
- No architecture, no stack, no file paths. If the agent puts a library name in
  intent, send it back.

**Gate:** `Approve | Revise | Pause`. Approval is bound to the intent version.

**Agent prompt:** `agent/prompts/01-intent.md`

---

## Phase 2 — Spike (only when a real unknown could kill the build)

**Goal:** retire the risky assumptions *before* you commit architecture to them.

**You do:** say which unknowns worry you. Pick which spikes to run.

**Agent does:** decomposes the unknowns into 2–5 testable questions, builds a
throwaway proof for the highest-risk one, reports VALIDATED / PARTIAL /
INVALIDATED with evidence.

**Artifact:** `spikes/NNN-question/` with a verdict at the top of its README.

**Exit criteria:** the question is answered with observed output, not a claim.
"VALIDATED — curl returns 200 in 340ms" is a verdict. "Looks good" is not.

**Skip this phase when:** the risk is low, or the answer is a 10-minute read of a
library's docs. Spikes are for unknowns that would change the architecture.

**Gate:** you accept the verdict. INVALIDATED is a success — it saved you the build.

**Agent prompt:** `agent/prompts/02-spike.md`

---

## Phase 3 — Specification (per initiative)

**Goal:** turn an approved outcome into a testable contract. This is the document
that makes implementation mechanical instead of improvisational.

**You do:** make the calls only an owner can make — scope trade-offs, risk
acceptance, "yes we do it in SQLite" / "no, we use Postgres".

**Agent does:** writes testable requirements with stable IDs, designs the
architecture, defines data and interfaces, makes every decision explicit and
reversible, states what is explicitly out of scope.

**Artifact:** `docs/spec.md` with:
- `FR-xxx` functional requirements, `NFR-xxx` non-functional
- `AC-xxx` acceptance criteria, one per requirement group
- `ADR-xxx` decision records inline or in `docs/decisions/`
- explicit security/privacy posture and observability expectations

**Exit criteria:**
- Every `OUT-xxx` from intent maps to at least one `FR-xxx`.
- Every `FR-xxx` has a matching `AC-xxx`.
- Every requirement is testable by something you can run.
- Unknowns are written as `Unknown` / `Deferred` / `Assumed (owner, validation)`.
  Never silently assumed.

**Gate:** you approve the spec and bind it to a version + commit SHA.

**Agent prompt:** `agent/prompts/03-spec.md`

**Toolchain note:** Kiro writes requirements in EARS notation — `WHEN <trigger>
THE SYSTEM SHALL <response>` — which makes a requirement directly translatable
into a test case.[3] BMAD separates the same work across named agents (analyst,
PM, architect) so one context doesn't hold the whole product.[4][5]

---

## Phase 4 — Plan (per initiative)

**Goal:** decide the order of work so that each task is small, independent, and
verifiable — the property that lets you run several agent lanes in parallel.

**You do:** approve the sequence and the risk tier. Nothing else.

**Agent does:** inspects the *real* repository (not your description of it),
identifies foundations that unlock everything else, decomposes into task packets,
maps dependencies, and proposes parallel lanes with disjoint write boundaries.

**Artifact:** `docs/plan.md` with `TASK-xxx` packets, each carrying:
- goal and the `FR-xxx`/`AC-xxx` it satisfies
- files in scope, files explicitly out of scope
- acceptance criteria and the exact verification command
- rollback note

**Exit criteria:**
- Every `FR-xxx` maps to at least one `TASK-xxx`. (Check with `tools/gate.py`.)
- No task depends on another task's unfinished code unless the dependency is stated.
- Each task is small enough that an agent finishes in one focused run (20–60 min).
  If a task says "and also", split it.
- Each task names its verification command: a command that exits non-zero on failure.

**Gate:** you approve. Approval authorizes *implementation of the listed tasks only*.
It never authorizes deploy, prod data, secrets, or external sends.

**Agent prompt:** `agent/prompts/04-plan.md`

---

## Phase 5 — Build (per task packet)

**Goal:** turn an approved task into a committed, tested change.

**You do:** nothing while it runs. This is the phase you delegate hardest.

**Agent does:** reads the real files, writes the failing test first, implements the
minimum to pass, runs the full suite, commits, and reports with real command output.

**Artifact:** a commit + `docs/reports/TASK-xxx.md` (what changed, which files, the
verbatim test output, what it did not do).

**Exit criteria:**
- The verification command from the packet passes, and you can see the output.
- Full suite still green (no regressions).
- New behavior has a test that *failed before* it passed.
- The commit message references the task ID.

**Gate:** none while building — but the agent must not merge, deploy, or touch
files outside its packet.

**Agent prompt:** `agent/prompts/05-build.md`

---

## Phase 6 — Verify (per task, before merge)

**Goal:** catch what the builder couldn't see. The agent that wrote the code is the
worst reviewer of that code.

**You do:** read the review verdict and the diff, not the code line by line. You
are checking that the *decision* was right, not that the syntax is.

**Agent does (fresh context, never the builder's):**
- static security scan of added lines (secrets, injection, unsafe deserialization)
- runs the test suite and reports new failures vs. baseline
- checks spec compliance: does the diff satisfy the task's `AC-xxx` and nothing more?
- returns a fail-closed verdict — unparseable or ambiguous = fail

**Artifact:** `docs/reports/REVIEW-TASK-xxx.md` + CI evidence.

**Exit criteria:**
- Reviewer verdict is PASS (no security concerns, no logic errors).
- Zero new test failures vs. baseline.
- No scope creep: the diff touches only files named in the packet.
- Every file you intended to change is actually changed.

**Gate:** you merge or you send it back. Fix cycles are capped at 2 — after that
something is wrong with the task, not the code. Reopen Phase 4.

**Agent prompt:** `agent/prompts/06-verify.md`

**Why a separate reviewer:** reviewing each line by hand made sense when a person
wrote the diff; it cannot keep up once agents write most of it. The human-speed
steps — plan, review, test, deploy — are the actual constraint now, so the process
has to move to match them.[6] Treat agent output as untrusted until it passes
automated checks and human review.[7]

---

## Phase 7 — Release (per version)

**Goal:** ship a version you can roll back, with a record of what shipped.

**You do:** approve the deploy. This is the only irreversible gate in the loop, and
in a one-person team it stays yours.

**Agent does:** drafts release notes from the commit range, verifies the version and
migrations, runs pre-flight checks, deploys to staging and smoke-tests it, prepares
the rollback command, and stays out of prod until you say go.

**Artifact:** `docs/releases/vX.Y.Z.md` (scope, pre-flight results, deploy steps,
rollback, post-release verification, release notes).

**Exit criteria:**
- Pre-flight checks green on the exact commit being released.
- Rollback is written and rehearsed enough that you could execute it blind.
- Post-release verification steps exist and are executable.

**Gate:** you approve deploy *and* you own the rollback decision.[7]

**Agent prompt:** `agent/prompts/07-release.md`

---

## Phase 8 — Operate (continuous)

**Goal:** know the thing is alive, and catch the failure before a user does.

**You do:** set the signals you care about and the thresholds that make you act.
You own the incident response; the agent summarizes.

**Agent does:** watches logs, error rates, and usage; drafts alerts; writes the runbook;
triages incoming issues into intent-sized items; keeps dependency and secret-rotation
cadence.

**Artifact:** `docs/runbook.md` + `docs/incidents/INC-xxx.md` per incident.

**Exit criteria:** you can answer "is it healthy right now?" and "what do I do if
<the most likely failure> happens?" without reading code.

**Gate:** the human owns the response; the agent summarizes the signal.[7]

---

## Phase 9 — Learn (per initiative close, and monthly)

**Goal:** convert experience into less work. This is the compounding phase.

**You do:** name the one thing that bit you, and what rule would have prevented it.

**Agent does:** mines the incident/bug log, proposes constitution amendments and
spec/plan corrections, updates the agent rules file, and opens the next initiative's
intent from what you learned.

**Artifact:** updated `docs/constitution.md`, `docs/lessons.md`, and `AGENTS.md`.

**Exit criteria:** every rule you add is phrased so an agent can obey it without
interpretation, and it is traceable to a real incident.

**Gate:** you approve the amendment.

**Agent prompt:** `agent/prompts/09-learn.md`

---

## The mechanics that make it work

### 1. Batch size: one task packet per agent run

An agent run should be 20–60 minutes and produce one reviewable commit. Bigger
batches produce bigger diffs, and a bigger diff gets a rubber-stamp review — which
is worse than no review, because it manufactures false confidence.

### 2. Fresh context for review

The reviewer must not be the builder. In Hermes, spawn it with `delegate_task` so
it has its own context and reads the diff cold. In Claude Code / Codex / OpenCode,
open a separate session. Same rule everywhere.

### 3. Deterministic checks beat model opinion

Tests, linters, type checkers, secret scanners, and the `tools/gate.py` script
below are the ground truth. A model's opinion of whether code is good is a
suggestion. A failing test is a fact.

### 4. Risk tiers decide how much you review

| Tier | What it covers | Your review |
|---|---|---|
| T0 | Docs, comments, formatting, scripts | spot-check |
| T1 | Isolated feature code, own module | verdict + diff skim |
| T2 | Shared contracts, APIs, schema, CI config | full diff read |
| T3 | Auth, money, secrets, PII, migrations, prod config | full diff + explicit approval |
| T4 | Deploy, prod data, external sends, deletion | you execute or explicitly authorize, always |

An agentic lifecycle has explicit gates with named approvers and exit criteria,
and autonomy expands only by risk tier.[7] For higher-risk work — auth, payments,
data migrations, anything touching customer PII — mandatory human code review and
security review apply, no exceptions.[7]

### 5. Context hygiene

Keep `AGENTS.md` short and current; put the map in `spec.md`, the order in
`plan.md`, the history in `docs/`. Your agent should read files, not need the
conversation. Never paste a whole file into chat to explain it — that's a stale
copy waiting to poison the next session.

### 6. Regression discipline (your existing rule, kept)

Every fix keeps a test in `tests/` and is logged in `docs/REGRESSIONS.md`. Every
fix ships with the failing-test-first proof. Never regress working behaviour.

### 7. Parallel lanes

Run independent tasks in parallel only when they have disjoint write boundaries.
Give each lane its own git worktree, merge serially, and let the gate script be the
merge gate. Parallelise known work; serialise anything shared.

### 8. Cost discipline

Cheap models for mechanical work (boilerplate, test scaffolding, refactors, doc
summaries). Strong models for Phase 1, 3, 4, 6 — judgment-heavy stages. The stages
where a wrong answer is expensive are exactly the stages where you use the
expensive model.

---

## Toolchain options (pick one, don't collect all)

| Tool | Shape | Best when |
|---|---|---|
| **GitHub Spec Kit** | `specify init` then in-agent commands: constitution → specify → plan → tasks → implement. Ships as open-source templates + processes for feature work, bug fixing, and idea assessment.[1] | You want the lightest, most portable spec-first skeleton. Invoke per agent: Copilot uses `/speckit.specify`, Codex uses `$speckit-specify` (Command Code / ZCode skills).[2] |
| **AWS Kiro** | Feature Specs: requirements.md → design.md → tasks.md, Requirements-First or Design-First, EARS requirement notation, plus bugfix specs and steering files.[3] | You want requirements and design generated together and tracked as tasks; strong on non-functional constraints. |
| **BMAD Method** | Named agents + workflow skills: clarify → plan → build → review, with project-context files, multi-agent discussion, and an eval runner.[4][5] | You want a full multi-persona method — analyst, PM, architect, dev, QA — closest to "I am the whole team". |
| **This kit** | Artifact contract + gates + prompts + a deterministic gate script | You want it vendor-neutral and wired to your own agent runtime (Hermes, Claude Code, Codex, OpenCode). |

Recommendation for you: **start with this kit's artifact contract, and borrow one
tool's template style if you like its output shape.** The contract is the asset;
the tool is replaceable. Everything here stays yours.

---

## Sources

1. GitHub Spec Kit — README, https://github.com/github/spec-kit
2. Spec Kit Integration CLI Reference — https://github.github.io/spec-kit/integrations/cli.html
3. Kiro Feature Specs docs — https://kiro.dev/docs/specs/feature-specs
4. BMAD Method docs — https://docs.bmad-method.org
5. BMAD Method — https://www.bmadcode.com/method
6. "The AI-native SDLC playbook", Anthropic — https://claude.com/resources/articles/the-ai-native-sdlc-playbook
7. "Beyond Prompt Engineering: Building an Agentic SDLC in 2026", Appiqa — https://www.appiqa.com/resources/blog/building-an-agentic-sdlc-in-2026
8. Sonar "Agent Centric Development Cycle (AC/DC)" — https://www.sonarsource.com/resources/library/enterprise-agent-centric-development-cycle/
