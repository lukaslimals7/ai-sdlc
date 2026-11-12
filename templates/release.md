# Release v<X.Y.Z> — <initiative name>

> Date: <date> · Commit: <SHA> · Approved by: Lukas
> This document is the record. If it isn't here, it didn't ship.

## 1. Scope

What is in this release, in one line each, with the task IDs.

| Task | Change | Risk tier |
|---|---|---|
| TASK-001 | <change> | T1 |

## 2. Pre-flight

| Check | Command | Result |
|---|---|---|
| Full suite green | `<cmd>` | <n passed> |
| Build / compile | `<cmd>` | PASS |
| Security scan clean | `<cmd>` | PASS |
| Migrations dry-run | `<cmd>` | PASS / n/a |
| Secrets not in diff | `<cmd>` | PASS |
| Version bumped | `grep version <file>` | <value> |

## 3. Deploy

```bash
# exact commands, in order
```

Target: <staging | production> · Window: <time> · Expected downtime: <none | n>

## 4. Post-release verification

```bash
# smoke tests that prove it's alive
curl -fsS <url>/health
```

- [ ] Health endpoint returns 200
- [ ] <critical user path works>
- [ ] Error rate unchanged for 15 minutes
- [ ] Logs clean of new exception classes

## 5. Rollback

```bash
# exact commands. You must be able to run this blind at 3am.
git revert <sha> && <deploy command>
```

- Data rollback: <none | migration down + how>
- Time to roll back: <minutes>
- Trigger for rolling back: <error rate > x, or <specific failure>>

## 6. Release notes (human-facing)

### Added
- <user-visible change>

### Fixed
- <bug>

### Changed
- <behavior change, and what users will notice>

## 7. Sign-off

- [ ] Pre-flight green on the released commit
- [ ] Smoke tests passed
- [ ] Rollback rehearsed or trivially safe
- [ ] Approved by Lukas
