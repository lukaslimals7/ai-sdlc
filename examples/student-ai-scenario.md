# Scenario — building "Vidya", an AI study assistant, with ai-sdlc

A full walkthrough of the kit in action. The app is real-shaped but illustrative;
the numbers are examples, not benchmarks. Read it after `MANUAL.md` Part 2, and
read `examples/demo-workspace/` for the artifact-level example this one
narrates.

## The cast

- Arjun — solo developer, one-person company
- Vidya — an AI study companion for students in classes 6–10: answers
  questions, explains concepts, generates practice questions
- Stack — Python + FastAPI, SQLite, Frontier model  API for the model
- Kit — Level 3 (full adoption): scaffolding, gate, pre-commit hook,
  `AGENTS.md`, cold-context review

---

## Step 0 — Get the kit and scaffold

```bash
git clone https://github.com/lukaslimals7/ai-sdlc.git ~/Desktop/ai-sdlc

mkdir ~/Desktop/vidya && cd ~/Desktop/vidya
git init
python3 ~/Desktop/ai-sdlc/tools/new_initiative.py "vidya-mvp" --repo .
```

Then he edits the generated `AGENTS.md` — what Vidya is, the map, the commands,
the hard rules, the traps, the verification playbook — and installs the gate as
a pre-commit hook:

```bash
~/Desktop/ai-sdlc/tools/install_gate_hook.sh .
```

From here on, every commit is gated. An unfilled artifact cannot be committed.

---

## Step 1 — Phase 1 Intent: the interview

He pastes `agent/prompts/01-intent.md` into his agent. The agent reads the repo
first, then asks — at most three at a time:

    Q1. What is the problem, in one paragraph, without naming a solution?
    Q2. Who exactly? "Students" is too broad — which students, where, doing what?
    Q3. If this works, what number changes, and how do you measure it?

Arjun's answers sharpen the idea:

- Problem: students in classes 6–10 get stuck on homework and there is no
  patient explainer at home at 9pm. Searching YouTube returns 20-minute videos,
  not an answer to their exact question.
- Who: class 6–10 students, mostly on phones, on cheap data.
- Success: a student gets a clear, correct explanation in under 30 seconds and
  comes back the next day.

The resulting `docs/intent.md`:

```markdown
## 3. Outcome
- **OUT-001** — A student gets an explanation for their exact question in under
  30 seconds, on a phone, without human help.
- **OUT-002** — The system rejects or safely handles questions it cannot answer
  well, instead of guessing.
- **OUT-003** — Monthly model spend stays under ₹2,000 while serving 100 students.

## 6. Non-goals
Out — and we will say no to these even when they're easy:
- No video, audio, or image generation. Text only.
- No live tutoring or human-in-the-loop.
- No content beyond the class 6–10 curriculum.
- No account system in v1 (anonymous sessions only).

## 7. Constraints
| Type | Constraint |
|---|---|
| Tech | FastAPI + SQLite; Frontier model  API; must run on a 2 vCPU VM in India |
| Money | ₹2,000/month model budget |
| Legal | Students may be minors: no PII stored, no personal data in prompts |
```

Gate: `python3 ~/Desktop/ai-sdlc/tools/gate.py docs` → `0 error(s), 0 warning(s)`.
Arjun replies `Approve`.

**Key moment:** the non-goals section kills three ideas he would have drifted
into — video, tutoring, accounts. That section earns its keep more than any
other.

---

## Step 2 — Phase 2 Spike: kill the Frontier model  unknowns

He pastes `agent/prompts/02-spike.md`. The agent decomposes the risks into a
table, ordered by what is most likely to kill the idea:

| # | Question | Risk if wrong | Est. |
|---|---|---|---|
| 1 | Given a student's question, when we call Frontier model , then does it return a valid JSON explanation in under 10 s? | architecture: we need a parser and a retry policy | 2 h |
| 2 | What does an explanation actually cost at our volume? | the budget dies | 30 min |
| 3 | Can a student break it with prompt injection ("ignore previous instructions")? | safety + trust | 1 h |
| 4 | Does the model explain well in the languages these students speak? | core value | 1 h |

Arjun picks 1 and 3 — the ones that would change the architecture. Number 2 is
skipped after reading the pricing docs, exactly as the kit tells him to.

**Spike 001 — JSON contract.** A throwaway script in `spikes/001-Frontier model -json/`.
Hardcoded prompt, prints the raw response:

```markdown
## Verdict: PARTIAL

### What worked
- JSON mode returns a parseable object in most runs; 1.8 s median on an Indian network.

### What didn't
- A fifth of responses wrap the JSON in markdown fences; some add trailing commentary.
- R1 (the reasoning model) is slow (6–9 s) and ignores JSON mode — not usable for
  the explanation path.

### Surprises
- The fence-wrapping is intermittent, not constant. A single happy path would have
  missed it entirely.

### Recommendation for the real build
- Use Frontier model -chat, not R1, for explanations. Strip fences, validate against a
  schema, retry once on parse failure, then fall back to a plain-text answer.
```

**Spike 002 — prompt injection.** A script that feeds injection attempts and logs
the outputs. Verdict: PARTIAL — the model follows injected instructions when the
prompt is unguarded, so a system-prompt boundary and an output filter are
mandatory, not optional.

Two unknowns that would have bitten him at week 3 were settled for two hours of
throwaway code. The spike verdicts will now be cited in the spec as the reason
for the retry policy and the R1 exclusion.

---

## Step 3 — Phase 3 Spec: the testable contract

He pastes `agent/prompts/03-spec.md`. The agent inspects the repo, drafts a
skeleton, and asks only the decisions Arjun owns:

    1. Do we store anything about the student, or is v1 anonymous?
    2. What is the cost ceiling per student per month?
    3. If the model fails, do we show an error or a fallback explanation?

Arjun decides: anonymous v1, ₹20 per student per month ceiling, and a fallback
text — never a silent failure, never a raw error.

The resulting `docs/spec.md`:

```markdown
## 2. Traceability
| Intent outcome | Requirements | Acceptance criteria |
|---|---|---|
| OUT-001 | FR-001, FR-002, NFR-001 | AC-001, AC-002 |
| OUT-002 | FR-003, FR-004 | AC-003 |
| OUT-003 | NFR-002 | AC-004 |

## 3. Functional requirements
- **FR-001** — WHEN a student submits a question, THE SYSTEM SHALL return one
  explanation in under 30 seconds.
- **FR-002** — WHEN a student asks for practice questions, THE SYSTEM SHALL return
  five questions with answers, tagged by topic.
- **FR-003** — WHEN the model returns malformed output, THE SYSTEM SHALL retry
  once and then return a safe fallback explanation.
- **FR-004** — WHEN a prompt contains instructions directed at the system, THE
  SYSTEM SHALL refuse to follow them and explain why.

## 4. Non-functional requirements
- **NFR-001** — Performance: p95 explanation latency under 10 s on the India VM.
- **NFR-002** — Cost: under ₹20 per student per month, measured by the spend log.
- **NFR-003** — Reliability: a model failure never returns a raw error to the
  student; always a fallback.

## 8. Security & privacy
- Students may be minors. No names, no school, no contact data.
- Question text is transient: logged only as a hash, never in full.
- Prompts carry no PII. The system prompt is fixed; student input is treated as
  data, never as instructions.

## 9. AI behavior
- Model: Frontier model -chat. R1 excluded for the explanation path (spike 001).
- Tools: none in v1 — the model answers from its own knowledge.
- Output contract: JSON {explanation, topic, confidence}. Schema-validated,
  one retry, then fallback.
- Failure modes: malformed → retry then fallback; timeout → fallback; refusal →
  fallback; hallucination → confidence below 0.6 adds a "check this" disclaimer.
- Evaluation: 50 hand-written questions with a rubric; pass threshold 90%.
- Cost ceiling: ₹20/student/month, enforced by a spend logger and an alert.

## 10. Acceptance criteria
- **AC-001** — GIVEN a valid question WHEN submitted THEN an explanation arrives
  under 30 s. Verified by: `pytest tests/test_explain.py::test_latency`
- **AC-002** — GIVEN a question outside the curriculum WHEN submitted THEN the
  response says it cannot help. Verified by: `pytest tests/test_scope.py::test_out_of_scope`
- **AC-003** — GIVEN malformed model output WHEN parsed THEN the retry path runs
  and the fallback is returned. Verified by: `pytest tests/test_fallback.py::test_malformed`
- **AC-004** — GIVEN a month of 100 students WHEN spend is measured THEN it is
  under ₹2,000. Verified by: `python3 scripts/spend_report.py`
```

Gate: `0 error(s), 0 warning(s)`. Approved and bound to a commit SHA.

**Key moment:** the minors/PII question becomes a *requirement with a test*, not
a vague intention. And the spike verdicts are cited as the reason for the retry
policy and the R1 exclusion — the spec is traceable all the way back to
throwaway code.

---

## Step 4 — Phase 4 Plan: ordered packets

He pastes `agent/prompts/04-plan.md`. The agent reality-checks the repo (real
`git rev-parse HEAD`, real test run: 12 passed), identifies one foundation, and
decomposes the rest:

```markdown
## 2. Foundations
| ID | Foundation | Unlocks | Verify by |
|---|---|---|---|
| EN-001 | Config + Frontier model  client wrapper (retry, fence stripping, spend log) | TASK-001..005 | `pytest tests/test_client.py -q` |

## 3. Task packets
### TASK-001 — /explain endpoint + tests
- **Satisfies:** FR-001, AC-001
- **Risk tier:** T2
- **Files in scope:** `app/routers/explain.py`, `tests/test_explain.py`
- **Verification command:** `pytest tests/test_explain.py -q`
- **Rollback:** `git revert` the commit

### TASK-002 — Output schema validation + fallback
### TASK-003 — Prompt-injection guard            (T3 — safety)
### TASK-004 — Practice-question endpoint + tests (T1)
### TASK-005 — Eval harness + spend report script (T2)
```

Coverage table: every FR/NFR mapped to at least one task. No parallel lanes —
all five packets touch the same router, so they serialise. Each packet names
its verification command and a rollback.

Gate: `0 error(s), 0 warning(s)`. Arjun approves. That approval authorizes
implementation of these five packets only.

---

## Step 5 — Phase 5 Build: one packet

He pastes `agent/prompts/05-build.md` and points it at TASK-001. The builder:

1. reads the packet, the constitution, and `AGENTS.md`
2. runs the suite: `12 passed, 0 failed` (baseline)
3. writes `tests/test_explain.py::test_happy_path` — it fails
4. implements the endpoint — it passes
5. runs the full suite — `14 passed, 0 failed`
6. commits, and writes `docs/reports/TASK-001.md`

```markdown
## Report — TASK-001
### Changed
| File | What changed |
|---|---|
| app/routers/explain.py | POST /explain, calls the client, returns the schema |

### Evidence
$ pytest tests/test_explain.py::test_happy_path -q
1 passed in 0.42s
$ pytest tests/ -q
14 passed, 0 failed

### Tests added
- test_happy_path — failed before: yes, "ModuleNotFoundError: app.routers.explain"

### Not done / deferred
- rate limiting (TASK-003)
```

---

## Step 6 — Phase 6 Verify: cold context

He spawns a fresh context with `agent/prompts/06-verify.md` — a separate session
or `delegate_task`. The reviewer has no memory of the build and treats the diff
as untrusted. It returns:

```json
{
  "passed": true,
  "scope_violations": [],
  "security_concerns": [],
  "logic_errors": [],
  "evidence_gaps": [],
  "suggestions": ["put a request timeout at the router, not just in the client"],
  "summary": "Scope clean, evidence real, fallback path verified."
}
```

One non-blocking suggestion. Arjun merges.

---

## Step 7 — Phase 7 Release

He pastes `agent/prompts/07-release.md`. Pre-flight on the exact release commit:
suite green, build clean, secrets scan clean, version bumped. Staging deploy and
smoke test:

```bash
$ curl -fsS localhost:8000/health
{"status": "ok"}
$ curl -fsS -X POST localhost:8000/explain -d '{"question":"why is the sky blue"}'
{"explanation": "...", "topic": "physics", "confidence": 0.83}
```

Release doc `docs/releases/v0.1.0.md` written, rollback command rehearsed.
Arjun types `deploy`; production gets it. Post-release: error rate unchanged,
zero new exception classes.

---

## Step 8 — Phase 8 Operate

The runbook carries the signals: p95 latency, error rate, spend, fallback rate.
A week in, the spend alert fires — ₹2,300, over the ceiling. The operator prompt
finds the cause: a spike in out-of-scope questions burning tokens. Arjun adds a
cheap out-of-scope classifier in front of the model. It becomes incident
`INC-001`, and then a rule.

---

## Step 9 — Phase 9 Learn

At close, the retrospective mines the incidents, the review findings, and the
task reports. The amendments it proposes:

- "Every model call logs its token cost to `spend_log`; the weekly report alerts
  above 80% of the ceiling."
- "No student input is ever concatenated into the system prompt."

And it fixes the thing that actually failed: the spike template gets a
"failure modes" checklist, because the first spike missed the fence-stripping
case until a second run.

---

## What this scenario shows

- The kit's job is not to write code for Arjun. It is to make sure the questions
  he would skip — PII, cost, injection, fallback, evaluation — get answered
  before they become bugs.
- The gate keeps the chain honest: every task traces to a requirement, every
  requirement traces to an outcome, and nothing moves without approval.
- The cost is bounded: a few hours of Arjun's week, not a process tax.
- The artifacts are the memory. A new agent session, a different model, or
  Arjun at 2am can resume from `docs/` — no conversation required.
