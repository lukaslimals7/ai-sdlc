# AI SDLC — one-man-team kit

You are the whole company. The agent is the whole engineering org. This kit is the
contract between you and it: ten phases, nine templates, nine phase prompts, and a
script that refuses to let an unapproved or untraceable artifact move forward.

It is vendor-neutral. It works with Hermes, Claude Code, Codex, OpenCode, Copilot,
or a bare `hermes chat -q`. The artifacts are markdown; the runtime is replaceable.

---

## Read in this order

| File | What it is | Read when |
|---|---|---|
| `sdlc.md` | The ten phases, top to bottom, with exit criteria and gates | First, fully. ~20 min |
| `MANUAL.md` | The operator's handbook: setup, phase-by-phase playbook, gate reference, troubleshooting | When you start running a real build |
| `roles.md` | Who decides what; the agent org chart; your weekly rhythm | Second |
| `templates/` | The nine artifacts you actually fill in | When starting an initiative |
| `agent/AGENTS.md.template` | The rules file every agent reads before touching code | Once per repo |
| `agent/prompts/` | Copy-paste prompts, one per phase | During each phase |
| `tools/gate.py` | Deterministic checker: traceability, approvals, placeholders | Before every phase advance |
| `tools/new_initiative.py` | Scaffolds `docs/`, `spikes/`, `AGENTS.md` in an existing repo | Once per initiative |
| `tools/install_gate_hook.sh` | Makes the gate a pre-commit hook | Once per repo |
| `examples/demo-workspace/` | A small real initiative, filled in end to end | When the templates feel abstract |
| `examples/student-ai-scenario.md` | A narrative walkthrough: an AI study assistant built with DeepSeek, phase by phase | When you want to see the whole journey |

---

## The 10 phases in one screen

```text
0  Constitution   once per repo        docs/constitution.md + AGENTS.md
1  Intent         what & why           docs/intent.md          OUT-xxx
2  Spike          kill the unknowns    spikes/NNN/             verdict
3  Spec           testable contract    docs/spec.md            FR-xxx AC-xxx
4  Plan           ordered packets      docs/plan.md            TASK-xxx
5  Build          agent executes       commit + report         evidence
6  Verify         cold-context review  docs/reports/REVIEW-*   PASS/FAIL
7  Release        ship + rollback      docs/releases/vX.Y.Z.md
8  Operate        signals + incidents  docs/runbook.md         INC-xxx
9  Learn          amend the rules      constitution + lessons
```

**The law:** every phase produces committed markdown; the next phase starts by
reading it. No phase starts from a conversation.

---

## Start an initiative in 6 commands

```bash
# 1. scaffold a workspace for a new initiative (creates docs/, spikes/, reports/)
python3 tools/new_initiative.py "quiz-export-offline" --repo ~/Desktop/quiz-maker

# 2. fill docs/intent.md with the agent (prompt: agent/prompts/01-intent.md)
# 3. gate it
python3 tools/gate.py ~/Desktop/gyaanix-teacher-ai/docs/intent.md

# 4. spec, plan, task packets...
python3 tools/gate.py ~/Desktop/gyaanix-teacher-ai/docs --stage plan

# 5. build one packet at a time (prompt: agent/prompts/05-build.md)
# 6. verify with a cold-context reviewer (prompt: agent/prompts/06-verify.md)
```

`gate.py` exits non-zero on: missing IDs, an `OUT` with no `FR`, an `FR` with no
`AC` or no `TASK`, an unfilled placeholder (`<like this>`, `TODO`, `TBD`), or a missing
approval block. Wire it into `pre-commit` and the gate stops being a promise.

---

## Add it to a repo (5 minutes)

```bash
cp agent/AGENTS.md.template <repo>/AGENTS.md     # then edit the 6 placeholders
mkdir -p <repo>/docs
cp templates/constitution.md <repo>/docs/

# make the gate non-optional for this repo
./tools/install_gate_hook.sh <repo>
```

For Hermes specifically, `AGENTS.md` at the repo root is auto-read as project
context. For Claude Code it's `CLAUDE.md`; for Codex, `AGENTS.md` too. If you use
more than one runtime, keep one `AGENTS.md` and symlink the rest — one source of truth.

---

## The rules that actually matter

1. **One packet, one commit, one review.** If the diff isn't reviewable in 10
   minutes, the packet was too big.
2. **The reviewer is never the builder.** Fresh context or it's theatre.
3. **Deterministic checks beat model opinion.** A failing test is a fact; "looks
   good" is a mood.
4. **Approval binds to a version.** Change the artifact materially, reopen the gate.
5. **Autonomy scales with reversibility.** Deploy, delete, migrate, and send
   always need you.
6. **Every fix leaves a test and a line in `docs/REGRESSIONS.md`.**
7. **Phase 9 is not optional.** A system that doesn't amend itself gets more
   expensive every month.

---

## What this kit deliberately does not do

- It does not pick your architecture. That's Phase 3, and it's yours.
- It does not run your agent. Use Hermes `delegate_task`, a `hermes chat -q` run,
  or your editor's agent — the prompts are written to be runtime-agnostic.
- It does not replace tests. It sits above them: tests prove code works, gates
  prove work was authorized.

See `sdlc.md` for the sourced comparison of Spec Kit, Kiro, and BMAD if you want to
borrow one of their shapes.
