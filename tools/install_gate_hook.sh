#!/usr/bin/env bash
# install_gate_hook.sh — make the AI-SDLC gate non-optional in a repo.
#
#   ./install_gate_hook.sh ~/Desktop/gyaanix-teacher-ai
#
# Writes .git/hooks/pre-commit, which blocks a commit when docs/intent.md,
# docs/spec.md and docs/plan.md fail the gate. Skips silently when the repo has
# no AI-SDLC workspace yet, so it is safe to install on every project.

set -euo pipefail

REPO="${1:?usage: install_gate_hook.sh <repo>}"
REPO="$(cd "$REPO" && pwd)"
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE="$KIT/tools/gate.py"

if [ ! -d "$REPO/.git" ]; then
  echo "error: $REPO is not a git repository" >&2
  exit 2
fi
if [ ! -f "$GATE" ]; then
  echo "error: gate.py not found at $GATE" >&2
  exit 2
fi

HOOK="$REPO/.git/hooks/pre-commit"
if [ -f "$HOOK" ] && ! grep -q "AI-SDLC gate" "$HOOK"; then
  cp "$HOOK" "$HOOK.backup-$(date +%s)"
  echo "note: existing pre-commit backed up"
fi

cat > "$HOOK" <<EOF
#!/usr/bin/env bash
# AI-SDLC gate — installed by ai-sdlc/tools/install_gate_hook.sh
# Blocks commits whose docs intent/spec/plan fail traceability or approval checks.
set -e
ROOT="\$(git rev-parse --show-toplevel)"
DOCS="\$ROOT/docs"
if [ -f "\$DOCS/intent.md" ] || [ -f "\$DOCS/spec.md" ] || [ -f "\$DOCS/plan.md" ]; then
  python3 "$GATE" "\$DOCS" || {
    echo ""
    echo "commit blocked: AI-SDLC artifacts failed the gate."
    echo "fix the findings above, or bypass once with: git commit --no-verify"
    exit 1
  }
fi
EOF
chmod +x "$HOOK"
echo "installed: $HOOK"
echo "gate:      $GATE"
