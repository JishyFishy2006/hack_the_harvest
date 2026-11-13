# hack_the_harvest (template)

A private template for the hackathon repo. It has an issue-to-agent pipeline, CI, and a playbook, but no project code yet.
At kickoff, click **Use this template** on GitHub, give the new repo its real name, and follow **Setup** below.

## How the agent pipeline works

| Do this | What happens |
|---|---|
| Add label `agent:<username>` to an issue | Claude works it on that person's subscription, pushes a branch, and a PR opens assigned to them |
| Add label `agent:any` | Same, round-robin across everyone in `.github/agents.json` |
| Comment `@claude <request>` on an issue or PR | Claude follows up, on the **commenter's** subscription |

- Each person's runs are serialized, so one token never runs two jobs at once.
- **Gotcha:** GitHub keeps only one *pending* run per person. If you queue three `agent:alice` issues quickly, the middle one gets cancelled. Re-label it, or spread work with `agent:any`.
- Agents never merge. Whoever's agent did the work reviews and merges.

## Setup (do this in the new repo at kickoff, about 10 min)

Secrets and app installs **don't copy** from a template, so redo these:

1. **Install the Claude GitHub App** on the new repo: run `/install-github-app` in Claude Code, or go to https://github.com/apps/claude.
   - This app token lets agent PRs trigger CI. A plain `GITHUB_TOKEN` can't.
2. **Every teammate:**
   - Run `claude setup-token` and copy the token.
   - Add it as a repo secret named `CLAUDE_TOKEN_<USERNAME>` (uppercase, non-alphanumerics become `_`), e.g. `JishyFishy2006` gets `CLAUDE_TOKEN_JISHYFISHY2006`:
     `gh secret set CLAUDE_TOKEN_JISHYFISHY2006`
   - Add their GitHub username to `.github/agents.json`.
3. **Create the labels:** run `bash scripts/setup-labels.sh`.
4. **Fill in `CLAUDE.md`:** the project, demo flow, stack, and commands. This matters more than anything else for agent quality.
5. **Make `scripts/ci.sh` explicit** for the chosen stack, and keep it under about 2 minutes.
6. **Smoke test:** open a trivial issue ("add a /health endpoint"), label it `agent:<you>`, and watch the Actions tab.

## Playbook

See [PLAYBOOK.md](PLAYBOOK.md).
