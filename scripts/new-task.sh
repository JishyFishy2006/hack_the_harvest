#!/usr/bin/env bash
# Create an agent task issue matching .github/ISSUE_TEMPLATE/agent-task.yml.
# Usage: scripts/new-task.sh "<title>" "<goal>" "<acceptance criteria>" [label]
set -euo pipefail

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  echo "Usage: $0 \"<title>\" \"<goal>\" \"<acceptance criteria>\" [label]" >&2
  exit 1
fi

title="$1"
goal="$2"
acceptance="$3"
label="${4:-}"

body="### Goal
${goal}

### Acceptance criteria
${acceptance}"

args=(--title "[task] ${title}" --body "$body")
if [ -n "$label" ]; then
  args+=(--label "$label")
fi

# gh prints the new issue URL on success
gh issue create "${args[@]}"
