#!/usr/bin/env bash
# Creates routing + triage labels. Re-run after adding members to .github/agents.json.
# Usage: scripts/setup-labels.sh [owner/repo]   (defaults to current repo)
set -euo pipefail
cd "$(dirname "$0")/.."
REPO_ARGS=()
[ $# -ge 1 ] && REPO_ARGS=(--repo "$1")

label() { gh label create "$1" --color "$2" --description "$3" --force "${REPO_ARGS[@]}"; }

label "agent:any" "7057ff" "Agent picks this up (round-robin across members)"
for m in $(python3 -c 'import json; print("\n".join(json.load(open(".github/agents.json"))["members"]))'); do
  label "agent:$m" "a371f7" "Agent runs on $m's Claude subscription"
done

label "area:frontend" "1d76db" "UI"
label "area:backend"  "0e8a16" "API / server / DB"
label "area:data"     "fbca04" "Data, ML, integrations"
label "demo-critical" "d93f0b" "Must work for the demo"
label "stretch"       "c5def5" "Only if time allows"
