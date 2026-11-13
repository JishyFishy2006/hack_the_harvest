# CLAUDE.md

Hackathon project. Speed matters, and so does a working demo. Prefer the simplest thing that works.

## Project
<!-- FILL IN AT KICKOFF (from the /grill-me spec) -->
- **What we're building:** TODO (one sentence)
- **Demo flow:** TODO (the 3–5 steps judges will see; everything serves this)
- **Stack:** TODO
- **Spec:** TODO (link to the spec issue or docs/ file)
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
- Shared types / API contracts live in ONE place (TODO: path). Change them only when the ticket says to.
- Use mock data behind the same interface when a real service isn't ready.
- Secrets go in `.env` (gitignored). Add any new variable name to `.env.example`. Never commit real keys.

## Writing tickets (planner)
Tickets are executed by a cheaper model (Sonnet by default) that can't ask questions, so **the planner makes the decisions and the ticket carries them.** Every ticket gets:
- **Goal:** one or two sentences, from the user's point of view.
- **Acceptance criteria:** concrete and checkable. These are the definition of done.
- **Files:** exact paths to create or edit. Name existing helpers or components to reuse.
- **Interfaces:** exact function signatures, API routes with request and response shapes, and DB fields this ticket adds or consumes. Paste them; don't describe them.
- **Out of scope:** the tempting extras the executor should *not* build.
- **Blocked by:** ticket numbers. Only label a ticket for an agent once its blockers are merged.
- It should be one vertical slice that fits in one session. If a ticket needs a design decision, it isn't ready; decide first, then write it.

Labels: `agent:<username>` or `agent:any` dispatches it. Add `model:opus` for genuinely hard tickets (tricky algorithms, cross-cutting changes) and `model:haiku` for trivial ones (copy, config, styling tweaks). Omit both for Sonnet.

## When working a ticket (executor)
1. Read the ticket's **Acceptance criteria**, **Interfaces** and **Out of scope**. They define done. Don't redesign what the ticket already decided.
2. Stay inside the files the ticket lists. Don't refactor or reformat unrelated code; other agents work in parallel and you'll cause merge conflicts.
3. If something in the ticket is impossible or contradicts the code, do the clearly-defined part and explain the conflict in your final comment. Don't guess at a redesign.
4. Run `bash scripts/ci.sh` and fix failures before finishing.
5. Commit with a message referencing the ticket (`#<n>`). A PR will be opened from your branch automatically.
6. In your final comment: what you did, how to verify it, and what you skipped or didn't check.

## How to write code (adapted from Ponytail, "full" level, MIT)
Solve the whole problem with the least new code. Take the first option that fully works:
1. Does it need to exist? Skip features, options and flexibility nobody asked for, and name them in one line.
2. Already in this codebase (a helper, component, pattern)? Use it the way the surrounding code does.
3. Standard library or platform feature? Use it.
4. An installed dependency? Use it. Never add a dependency for a few lines.
5. Otherwise, write the minimum code that works.

- Be lazy about the solution, never about the change itself: finish every part the ticket needs, including callers and fixtures your change breaks.
- No abstraction, wrapper, option, config or "for later" code nobody asked for. Keep the structure the codebase already has.
- Comment only the *why* the code can't show, in one line.
- New non-trivial logic (a parser, a calculation, anything with money or security) gets one small test or an assert-based self-check. Trivial changes need none. Don't build test suites.
- A deliberate shortcut gets a comment: `shortcut: <the limit>, <when to upgrade>`.
- **Never cut:** validation of external input, error handling that prevents data loss, security, accessibility, or anything the ticket asked for.

## Don't
- Don't touch `.github/` unless the ticket is about CI or agents.
- Don't delete or rewrite other people's features to make yours work.
- Don't add auth, test suites, or abstractions the demo doesn't need.
