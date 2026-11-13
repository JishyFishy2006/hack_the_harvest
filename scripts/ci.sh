#!/usr/bin/env bash
# One command for "is this mergeable?". Used by CI, by agents, and by humans.
# Stack-agnostic: runs whatever exists. Once the stack is picked, make this explicit.
set -euo pipefail
cd "$(dirname "$0")/.."

ran=0

if [ -f package.json ]; then
  if [ -f pnpm-lock.yaml ]; then npx -y pnpm install --frozen-lockfile
  elif [ -f package-lock.json ]; then npm ci
  else npm install; fi
  for s in lint typecheck test build; do
    npm run "$s" --if-present
  done
  ran=1
fi

if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
  [ -f requirements.txt ] && pip install -q -r requirements.txt
  [ -f pyproject.toml ] && pip install -q -e . 2>/dev/null || true
  if command -v ruff >/dev/null || pip install -q ruff; then ruff check .; fi
  if [ -d tests ]; then pip install -q pytest && pytest -q; fi
  ran=1
fi

[ "$ran" = 1 ] || echo "No project files yet; nothing to check."
echo "ci.sh: OK"
