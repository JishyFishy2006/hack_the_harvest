# CLAUDE.md

Hackathon project. Speed matters, and so does a working demo. Prefer the simplest thing that works.

## Project
<!-- FILL IN AT KICKOFF -->
- **What we're building:** TODO (one sentence)
- **Demo flow:** TODO (the 3–5 steps judges will see; everything serves this)
- **Stack:** TODO
- **Deployed at:** TODO

## Commands
<!-- FILL IN once the stack exists -->
- Install: TODO
- Run locally: TODO
- Check everything: `bash scripts/ci.sh` (must pass before you finish)

## Layout
<!-- FILL IN: where things live, e.g. -->
<!-- - `web/` frontend, `api/` backend, `shared/` types shared by both -->

## Conventions
- Shared types / API contracts live in ONE place (TODO: path). Change them only when the issue says to.
- Use mock data behind the same interface when a real service isn't ready.
- Secrets go in `.env` (gitignored). Add any new variable name to `.env.example`. Never commit real keys.
- No new dependencies unless they clearly save time. Note any you add in the PR.

## When working an issue (agents)
1. Read the issue's **Acceptance criteria** and **Out of scope**. They define done.
2. Stay inside the files/areas the issue lists. Don't refactor or reformat unrelated code; other agents work in parallel and you'll cause merge conflicts.
3. Keep the change small. If the issue is too big or unclear, do the clearly-defined part and say what's left in your final comment.
4. Run `bash scripts/ci.sh` and fix failures before finishing.
5. Commit with a message referencing the issue (`#<n>`). A PR will be opened from your branch automatically.
6. In your final comment: what you did, how to verify it, anything you weren't sure about.

## Don't
- Don't touch `.github/` unless the issue is about CI/agents.
- Don't delete or rewrite other people's features to make yours work.
- Don't add auth, tests suites, or abstractions the demo doesn't need.
