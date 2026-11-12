#!/usr/bin/env python3
"""new_initiative.py — scaffold an AI-SDLC workspace inside an existing repo.

    python3 new_initiative.py "quiz-export-offline" --repo ~/Desktop/gyaanix-teacher-ai
    python3 new_initiative.py "my-thing" --name "My Thing" --repo . --force

Creates (never overwrites unless --force):
    <repo>/docs/{constitution,intent,spec,plan,REGRESSIONS,lessons}.md
    <repo>/docs/{tasks,reports,releases,decisions,incidents}/
    <repo>/spikes/
    <repo>/AGENTS.md          (only if absent)

Placeholders are substituted with the initiative name; everything else stays a
template for the agent to fill in Phase 1.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
TPL = os.path.join(KIT, "templates")


def substitute(text: str, slug: str, name: str) -> str:
    # Only replace the obvious bracket placeholders; leave <date>/<cmd> etc. for a human.
    text = text.replace("<initiative name>", name).replace("<project name>", name)
    text = re.sub(r"<initiative>", slug, text)
    return text


def write(path: str, content: str, force: bool) -> str:
    if os.path.exists(path) and not force:
        return f"skip   {path} (exists)"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return f"create {path}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="short kebab-case name, e.g. quiz-export-offline")
    ap.add_argument("--repo", default=".", help="path to the target repository")
    ap.add_argument("--name", default=None, help="human title (defaults to title-cased slug)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    repo = os.path.abspath(os.path.expanduser(args.repo))
    if not os.path.isdir(repo):
        print(f"error: repo not found: {repo}", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", args.slug):
        print("error: slug must be kebab-case, 2-63 chars", file=sys.stderr)
        return 2

    name = args.name or args.slug.replace("-", " ").title()
    docs = os.path.join(repo, "docs")

    plan = [
        ("constitution.md", "constitution.md"),
        ("intent.md", "intent.md"),
        ("spec.md", "spec.md"),
        ("plan.md", "plan.md"),
        (None, "REGRESSIONS.md"),
        (None, "lessons.md"),
    ]
    for src, dst in plan:
        target = os.path.join(docs, dst)
        if src and os.path.isfile(os.path.join(TPL, src)):
            body = substitute(open(os.path.join(TPL, src), encoding="utf-8").read(), args.slug, name)
        elif dst == "REGRESSIONS.md":
            body = ("# Regressions\n\nEvery fixed bug gets a line here. "
                    "Format: symptom -> root cause -> fix -> standing rule.\n\n"
                    "| Date | Symptom | Root cause | Fix | Rule |\n|---|---|---|---|---|\n")
        else:
            body = (f"# Lessons — {name}\n\nOne paragraph per lesson. "
                    "Each lesson produces a constitution amendment or it isn't a lesson.\n")
        print(write(target, body, args.force))

    for sub in ("tasks", "reports", "releases", "decisions", "incidents"):
        d = os.path.join(docs, sub)
        if os.path.isdir(d):
            print(f"skip   {d}/ (exists)")
        else:
            os.makedirs(d, exist_ok=True)
            print(f"create {d}/")

    spikes = os.path.join(repo, "spikes")
    if os.path.isdir(spikes):
        print(f"skip   {spikes}/ (exists)")
    else:
        os.makedirs(spikes, exist_ok=True)
        print(f"create {spikes}/")

    agents_src = os.path.join(KIT, "agent", "AGENTS.md.template")
    agents_dst = os.path.join(repo, "AGENTS.md")
    if os.path.isfile(agents_src):
        print(write(agents_dst, substitute(open(agents_src, encoding="utf-8").read(), args.slug, name),
                    force=False))

    print("\nnext:")
    print(f"  1. fill {os.path.join(docs, 'intent.md')}  (prompt: agent/prompts/01-intent.md)")
    print(f"  2. python3 {os.path.join(HERE, 'gate.py')} {docs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
