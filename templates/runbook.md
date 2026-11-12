# Runbook — <project name>

> The document you read at 2am. If a step requires thinking, it's not a runbook.

## 1. What this is

<One paragraph: what the system does, who uses it, what breaks users first.>

## 2. Access

| Thing | Where | Notes |
|---|---|---|
| Repo | `<url / path>` | |
| Server | `<host>` | `<ssh command>` |
| Logs | `<path or command>` | |
| DB | `<path>` | Back up before touching |
| Secrets | `<env file — names only>` | Never printed |

## 3. Health check

```bash
<command that returns healthy / unhealthy>
```

Expected: <output>. If it fails: see §6.

## 4. Common operations

### Restart

```bash
<exact commands>
```

### Deploy a version

```bash
<exact commands>   # or: see docs/releases/vX.Y.Z.md
```

### Roll back

```bash
<exact commands>
```

### Back up the database

```bash
<exact commands>
```

## 5. Signals

| Signal | Where | Healthy | Act when |
|---|---|---|---|
| Error rate | <where> | <baseline> | > <threshold> |
| Latency p95 | <where> | <baseline> | > <threshold> |
| Disk | <where> | <baseline> | > 80% |
| API spend | <where> | <budget> | > 80% of budget |

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| <symptom> | <cause> | <command> |
| <symptom> | <cause> | <command> |

## 7. Incident checklist

1. Stop the bleeding (roll back or disable — don't debug first).
2. Write the timestamp and what you saw in `docs/incidents/INC-xxx.md`.
3. Tell affected users, if any.
4. Fix forward, with a test that reproduces it.
5. Phase 9: what rule would have prevented this?

## 8. Known limits

- <thing this system does not handle, and what to do instead>
