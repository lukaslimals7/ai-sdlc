# Roles — one human, one agent org

You are not "just the developer". You hold every role at once. The failure mode is
not that you lack a team; it's that you inherit every team's handoff cost and none
of their parallelism, while the agent generates code faster than you can supervise it.

So: keep the roles distinct, but let the agent play most of them — in separate
contexts, with separate jobs.

---

## The role map

| Role | Who plays it | Accountable for | Time cost to you |
|---|---|---|---|
| Decision owner | **You** | Scope, architecture exceptions, risk, release | The real cost — protect it |
| Facilitating agent | Agent | Interviews, challenges, drafts, evaluates | 0 |
| Subject expert | You | Users, market, ops reality, policy truth | Concentrated |
| Technical owner | You + agent | Architecture, feasibility, security, operability | Split |
| Planning owner | Agent (you approve) | Sequence, dependencies, allocation | Approval only |
| Execution agent | Agent | Implementation + verification inside a packet | 0 |
| Reviewer / integrator | Agent (fresh context) + you | Independent review, merge readiness | Verdict review |

**You never stop being the decision owner.** That is the point of a one-person
company: you own the consequences, so you own the calls.

---

## What only you may decide

These are the decisions an agent must not make silently, because they change the
product's direction, cost, or blast radius:

- What problem we're solving and who it's for (Phase 1).
- Scope trade-offs and non-goals.
- Anything touching money, auth, personal data, or customer-visible behaviour.
- Production deploys, data migrations, deletions, external sends.
- Risk acceptance when the evidence is incomplete.
- "This is good enough to ship."

Everything else is delegated. If you find yourself making a call the agent could
have made from the spec, the spec is missing something — fix the spec, don't
become the bottleneck.

---

## What the agent may do without asking

- Read, search, and analyse the repository.
- Draft and revise any artifact in `docs/` that is not yet approved.
- Write tests, run them, run linters, run scanners, run your build.
- Build and modify code inside an approved task packet's file scope.
- Create branches and worktrees.
- Write release notes, changelog entries, and runbook drafts.
- Propose dependency updates with a tested PR.
- Report a blocked task with the exact blocker and what it tried.

---

## What the agent may never do

- Approve its own work, or mark a task complete without a passing verification command.
- Merge to the default branch.
- Deploy to production, touch prod data, or run migrations.
- Read, print, log, or commit secrets and API keys.
- Expand a task's file scope, or add features not in the packet.
- Delete a file, drop a table, or force-push without explicit authorization.
- Rewrite an approved artifact (intent/spec/plan) without reopening its gate.

---

## The agent org chart

You are the CTO. The agent org is four functions, each run as a **separate
context** so it doesn't grade its own homework:

```text
                        ┌─────────────────────────┐
                        │   YOU — Decision owner   │
                        │ approve / revise / pause │
                        └────────────┬────────────┘
                                     │
        ┌───────────────┬────────────┴────────────┬────────────────┐
        ▼               ▼                         ▼                ▼
  ┌──────────┐   ┌────────────┐           ┌────────────┐   ┌────────────┐
  │ Planner  │   │  Builder   │           │  Reviewer  │   │  Operator  │
  │ phases   │   │  phase 5   │           │  phase 6   │   │ phases 7-8 │
  │ 2,3,4    │   │            │           │ (cold ctx) │   │            │
  └──────────┘   └────────────┘           └────────────┘   └────────────┘
        │               │                         │                │
   intent.md         commit                 review verdict      release notes
   spec.md         + tests                 + evidence           runbook, alerts
   plan.md
```

In Hermes, `delegate_task` gives you the separate contexts (planner, builder,
reviewer, operator). In Claude Code / Codex / OpenCode, use separate sessions or
subagents. Same separation, same reason: the builder's context is contaminated by
the intent of the code, the reviewer's must not be.

---

## The supervision budget (why batching matters)

Your attention is the scarcest resource in this company. Assume you can give
**~15 minutes of real review per task packet**, once a day or twice.

That single number determines everything:

- A task packet must be sized so its diff is reviewable in 10 minutes.
- A run must be sized so its report is skimmable in 3 minutes.
- If a packet needs more than that, it isn't one packet — split it.

If you find yourself merging diffs you didn't read, you have silently converted
yourself into a rubber stamp. That's worse than having no review: it manufactures
confidence you haven't earned.

---

## Weekly operating rhythm

| When | What | Time |
|---|---|---|
| Monday | Pick one initiative. Intent → Spec approval. | 45–90 min |
| Tuesday | Plan approval. Launch 2–4 builder runs in parallel lanes. | 30 min |
| Wednesday | Review verdicts, merge, or send back. Launch next batch. | 30 min |
| Thursday | Second batch. Release when green. | 30 min |
| Friday | Operate review: signals, incidents, dependency updates. Phase 9 lessons. | 45 min |

Total: roughly 4–5 hours of deliberate work per week. Everything else is the agent
running while you do something else. If you're spending 30 hours a week in this
system, you're not delegating — you're babysitting.

---

## The escalation rule

The agent stops and asks when it hits:
- a contradiction between two approved artifacts,
- a requirement it cannot test,
- a file outside its packet that it believes must change,
- a failing test it cannot fix within scope,
- any action that is irreversible, external, or touches production.

It does **not** escalate for: uncertainty it can resolve by reading more code,
a failing lint it can fix, a missing test it can write, or a dependency bump it
can test in isolation. Over-escalation is as expensive as under-escalation — it
turns you into a ticket queue.
