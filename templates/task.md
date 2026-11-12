# TASK-<NNN> — <title>

> Packet from `plan.md` v1.0 · Risk tier: T<N> · Builder run: <date/time>
> Instruction to the builder: this is your entire scope. Do not widen it.

## Goal

<One sentence: what is true after this task that wasn't before.>

## Satisfies

- FR-<xxx>, AC-<xxx>

## Files in scope

- `path/one`
- `path/two`

## Files out of scope

Everything else, explicitly including: `path/other`, config files, and the database.

## Constraints from the constitution

- Test first: the new test must fail before the implementation exists.
- No new dependency unless listed here: <none | name@version, because ...>
- Match existing style; do not refactor surrounding code.
- Secrets: names only. Never print, log, or commit a value.

## Acceptance criteria

- [ ] <observable behavior>
- [ ] <observable behavior>
- [ ] Full test suite green (no regressions)

## Verification command

```bash
<exact command>
```

It must exit 0. Paste its verbatim output in the report.

## Report format (builder fills this in)

```markdown
## Report — TASK-<NNN>

### Changed
| File | What changed |
|---|---|

### Evidence
```text
$ <command>
<verbatim output>
```

### Tests added
- `tests/test_<x>.py::test_<behavior>` — failed before: <yes, with this error>

### Not done / deferred
- <anything intentionally left out, and why>

### Surprises
- <anything that will change the plan>
```

## Rollback

`git revert <sha>` — <state to restore, if any>
