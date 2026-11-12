#!/usr/bin/env python3
"""gate.py — deterministic checker for AI-SDLC artifacts.

Checks traceability, approvals, verification commands, and unfilled placeholders
across docs/intent.md -> docs/spec.md -> docs/plan.md.

    python3 gate.py <file-or-docs-dir> [--stage intent|spec|plan|all] [--json]

Exit codes: 0 = pass (warnings allowed), 1 = errors, 2 = usage/IO problem.

Escape hatch: put `gate:allow-placeholder` on a line to skip placeholder checks
for that line (use sparingly, never in an approved artifact).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict

ID_RE = {
    "OUT": re.compile(r"\bOUT-\d{3}\b"),
    "FR": re.compile(r"\bFR-\d{3}\b"),
    "NFR": re.compile(r"\bNFR-\d{3}\b"),
    "AC": re.compile(r"\bAC-\d{3}\b"),
    "TASK": re.compile(r"\bTASK-\d{3}\b"),
    "EN": re.compile(r"\bEN-\d{3}\b"),
}
PLACEHOLDER_RE = re.compile(r"<[^<>\n]{1,80}>|\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b")
ALLOW = "gate:allow-placeholder"


@dataclass
class Finding:
    level: str  # ERROR | WARN
    code: str
    message: str
    detail: list = field(default_factory=list)


def ids(text: str, kind: str) -> list:
    seen, out = set(), []
    for m in ID_RE[kind].finditer(text):
        if m.group(0) not in seen:
            seen.add(m.group(0))
            out.append(m.group(0))
    return out


def placeholders(text: str) -> list:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if ALLOW in line:
            continue
        for m in PLACEHOLDER_RE.finditer(line):
            hits.append((i, m.group(0), line.strip()[:100]))
    return hits


def section(text: str, pattern: str) -> str:
    """Return text of the heading matching pattern until the next heading of same or higher level."""
    lines = text.splitlines()
    rx = re.compile(pattern, re.I)
    start = level = None
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m and rx.search(m.group(2)):
            start, level = i, len(m.group(1))
            break
    if start is None:
        return ""
    body = []
    for ln in lines[start + 1:]:
        m = re.match(r"^(#{1,6})\s+", ln)
        if m and len(m.group(1)) <= level:
            break
        body.append(ln)
    return "\n".join(body)


def approval_state(text: str) -> tuple:
    """Return (approved: bool, reason: str) based on Status/Approved by lines."""
    status = re.search(r"^\s*>?\s*Status:\s*(.+)$", text, re.M | re.I)
    approver = re.search(r"Approved by:\s*(.+)$", text, re.M | re.I)
    st = (status.group(1).strip() if status else "").upper()
    ap = (approver.group(1).strip() if approver else "")
    approved_status = "APPROVED" in st and "NOT APPROVED" not in st
    approver_ok = bool(ap) and "<" not in ap and ap.lower() not in {"", "pending", "n/a"}
    if approved_status and approver_ok:
        return True, f"Status={status.group(1).strip()}, Approved by {ap}"
    bits = []
    if not status:
        bits.append("no 'Status:' line")
    elif not approved_status:
        bits.append(f"Status is '{status.group(1).strip()}'")
    if not approver:
        bits.append("no 'Approved by:' line")
    elif not approver_ok:
        bits.append(f"approver unresolved ('{ap}')")
    return False, "; ".join(bits)


# ---------------------------------------------------------------- intent

def check_intent(text: str) -> list:
    f = []
    outs = ids(text, "OUT")
    if not outs:
        f.append(Finding("ERROR", "I001", "intent has no OUT-xxx outcomes; outcomes must be identifiable"))
    ng = section(text, r"non[- ]goals?")
    if not ng.strip():
        f.append(Finding("ERROR", "I002", "missing Non-goals section (the anti-scope-creep control)"))
    elif not re.search(r"^\s*[-*]\s+\S", ng, re.M):
        f.append(Finding("ERROR", "I003", "Non-goals section has no bullet items"))
    ph = placeholders(text)
    if ph:
        f.append(Finding("ERROR", "I004", f"{len(ph)} unfilled placeholder(s) in intent",
                         [f"line {l}: {s} -- {t}" for l, s, t in ph[:8]]))
    ok, why = approval_state(text)
    if not ok:
        f.append(Finding("ERROR", "I005", f"intent is not approved ({why})"))
    return f


# ---------------------------------------------------------------- spec

def check_spec(text: str, intent_text: str) -> list:
    f = []
    outs = ids(intent_text, "OUT") if intent_text else []
    frs = ids(text, "FR")
    acs = ids(text, "AC")

    if not frs:
        f.append(Finding("ERROR", "S001", "spec has no FR-xxx requirements"))

    missing = [o for o in outs if o not in text]
    if missing:
        f.append(Finding("ERROR", "S002", f"intent outcomes not carried into spec: {', '.join(missing)}",
                         ["every OUT-xxx must map to at least one FR-xxx"]))

    # each FR must appear on a line that also references an AC (traceability row or 'Verified by')
    unmapped = []
    for fr in frs:
        if not any(fr in ln and re.search(r"\bAC-\d{3}\b", ln) for ln in text.splitlines()):
            unmapped.append(fr)
    if unmapped:
        f.append(Finding("ERROR", "S003", f"requirements with no acceptance criterion: {', '.join(unmapped)}",
                         ["add an AC-xxx, or a traceability row pairing FR with AC"]))

    # each AC needs a runnable verification; ACs legitimately wrap across lines,
    # so evaluate per-AC block (from one AC id to the next), not per line.
    bad_ac = []
    for m in re.finditer(r"\bAC-\d{3}\b", text):
        start = m.start()
        nxt = re.search(r"\bAC-\d{3}\b", text[m.end():])
        block = text[start: m.end() + (nxt.start() if nxt else 400)]
        block = block.split("\n## ")[0]
        if re.search(r"\bGIVEN\b", block, re.I):
            if not (re.search(r"verified by:?", block, re.I) or "`" in block):
                bad_ac.append(" ".join(block.split())[:110])
    if bad_ac:
        f.append(Finding("ERROR", "S004", f"{len(bad_ac)} acceptance criterion/criteria have no verification command",
                         bad_ac[:6]))

    if not re.search(r"out of scope", text, re.I):
        f.append(Finding("WARN", "S005", "no 'Out of scope' section; scope boundaries are implicit"))

    if not ids(text, "NFR"):
        f.append(Finding("WARN", "S006", "no NFR-xxx non-functional requirements"))

    if not re.search(r"\bADR-\d{3}\b|## .*decisions", text, re.I):
        f.append(Finding("WARN", "S007", "no decision records (ADR); material choices are unrecorded"))

    ph = placeholders(text)
    if ph:
        f.append(Finding("ERROR", "S008", f"{len(ph)} unfilled placeholder(s) in spec",
                         [f"line {l}: {s} -- {t}" for l, s, t in ph[:8]]))

    ok, why = approval_state(text)
    if not ok:
        f.append(Finding("ERROR", "S009", f"spec is not approved ({why})"))
    return f


# ---------------------------------------------------------------- plan

def task_blocks(text: str) -> dict:
    blocks, cur, buf = {}, None, []
    for ln in text.splitlines():
        m = re.match(r"^#{2,6}\s+(TASK-\d{3})\b", ln)
        if m:
            if cur:
                blocks[cur] = "\n".join(buf)
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(ln)
    if cur:
        blocks[cur] = "\n".join(buf)
    return blocks


def check_plan(text: str, spec_text: str) -> list:
    f = []
    frs = ids(spec_text, "FR") if spec_text else []
    tasks = task_blocks(text)

    if not tasks:
        f.append(Finding("ERROR", "P001", "plan has no TASK-xxx packets"))

    unplanned = [fr for fr in frs if fr not in text]
    if unplanned:
        f.append(Finding("ERROR", "P002", f"requirements with no planned work: {', '.join(unplanned)}"))

    no_verify, no_satisfy, no_rollback = [], [], []
    for tid, body in tasks.items():
        if not re.search(r"verification command", body, re.I):
            no_verify.append(tid)
        elif PLACEHOLDER_RE.search(re.sub(r"```.*?```", "", body, flags=re.S)) and not re.search(
                r"verification command\s*\**\s*:?\s*\**\s*`[^`<]+`", body, re.I):
            no_verify.append(tid)
        if not re.search(r"satisfies", body, re.I) or not re.search(r"\b(FR|NFR)-\d{3}\b", body):
            no_satisfy.append(tid)
        if not re.search(r"rollback", body, re.I):
            no_rollback.append(tid)

    if no_verify:
        f.append(Finding("ERROR", "P003", f"tasks without a verification command: {', '.join(no_verify)}"))
    if no_satisfy:
        f.append(Finding("ERROR", "P004", f"tasks not tied to an FR/NFR: {', '.join(no_satisfy)}"))
    if no_rollback:
        f.append(Finding("WARN", "P005", f"tasks without a rollback note: {', '.join(no_rollback)}"))

    ph = placeholders(text)
    if ph:
        f.append(Finding("ERROR", "P006", f"{len(ph)} unfilled placeholder(s) in plan",
                         [f"line {l}: {s} -- {t}" for l, s, t in ph[:8]]))

    ok, why = approval_state(text)
    if not ok:
        f.append(Finding("ERROR", "P007", f"plan is not approved ({why})"))
    return f


# ---------------------------------------------------------------- driver

def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def resolve(arg: str) -> dict:
    if os.path.isdir(arg):
        base = arg
    else:
        base = os.path.dirname(os.path.abspath(arg))
    out = {}
    for name in ("intent", "spec", "plan"):
        for cand in (os.path.join(base, f"{name}.md"),):
            if os.path.isfile(cand):
                out[name] = cand
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Check AI-SDLC artifacts for traceability and approval.")
    ap.add_argument("path", help="docs directory, or a single artifact file")
    ap.add_argument("--stage", default="all", choices=["intent", "spec", "plan", "all"])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if not os.path.exists(args.path):
        print(f"gate: path not found: {args.path}", file=sys.stderr)
        return 2

    found = resolve(args.path)
    if not found:
        print(f"gate: no intent.md/spec.md/plan.md under {args.path}", file=sys.stderr)
        return 2

    texts = {k: read(v) for k, v in found.items()}
    findings, checked = [], []

    stages = ["intent", "spec", "plan"] if args.stage == "all" else [args.stage]
    for st in stages:
        if st not in texts:
            findings.append(Finding("ERROR", "X001", f"{st}.md not found (required for --stage {args.stage})"))
            continue
        checked.append(found[st])
        if st == "intent":
            findings += check_intent(texts[st])
        elif st == "spec":
            findings += check_spec(texts[st], texts.get("intent", ""))
        else:
            findings += check_plan(texts[st], texts.get("spec", ""))

    errors = [x for x in findings if x.level == "ERROR"]
    warns = [x for x in findings if x.level == "WARN"]

    if args.json:
        print(json.dumps({
            "checked": checked,
            "passed": not errors,
            "errors": [asdict(x) for x in errors],
            "warnings": [asdict(x) for x in warns],
        }, indent=2))
    else:
        print("AI-SDLC gate")
        print("-" * 62)
        for p in checked:
            print(f"  checked: {p}")
        if not findings:
            print("\n  no findings. traceability complete, artifacts approved.")
        for x in errors:
            print(f"\n  ERROR {x.code}  {x.message}")
            for d in x.detail:
                print(f"        {d}")
        for x in warns:
            print(f"\n  WARN  {x.code}  {x.message}")
            for d in x.detail:
                print(f"        {d}")
        print("-" * 62)
        print(f"  {len(errors)} error(s), {len(warns)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
