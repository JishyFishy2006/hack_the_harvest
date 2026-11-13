# Hackathon playbook

## Kickoff (first hour)
- [ ] **Ideate** as a team. Pick the idea and the **demo script** (3–5 steps). Cut anything that isn't in the demo.
- [ ] Create the repo from this template and do the README **Setup**. Run `/setup-matt-pocock-skills` once in it.
- [ ] **Plan on Opus** (`/model opus`, optionally `/ponytail ultra` so every feature gets challenged):
  1. `/grill-me` on the idea until the scope, stack, demo flow and data model are settled.
  2. `/to-spec` posts the tech spec as an issue. Fill the **Project** section of `CLAUDE.md` from it.
  3. Commit the contracts first: API routes and shapes, shared types, DB schema.
  4. `/to-tickets` breaks the spec into vertical-slice tickets with blockers. Each ticket follows "Writing tickets" in `CLAUDE.md`.
- [ ] Set `/ponytail full` again for building.
- [ ] **Divide and conquer:** label the unblocked tickets `agent:<person>` (split by area so PRs rarely touch the same files) or `agent:any`. Add `model:opus` or `model:haiku` where it fits.

## Hours 1–3: walking skeleton
- [ ] Get frontend → backend → data → **deployed URL** working end to end with fake data.
- [ ] Set up auto-deploy from `main`.
- [ ] After this point, everything is parallel work against the contracts.

## The build
- As tickets merge, label the next unblocked ones. You're the dependency scheduler; the pipeline doesn't read blockers.
- New work mid-build: use the **Agent task** template, or have Opus write the ticket.
- Review agent PRs with `/ponytail-review` before merging.
- Don't dispatch two agents into the same files at the same time.
- Keep PRs small and merge often. `main` must always be demoable.
- Tag a known-good commit every few hours: `git tag demo-ok-<time> && git push --tags`.
- Label `demo-critical` vs `stretch`, and work `demo-critical` first.

## Endgame
- [ ] **Feature freeze 2–3 hours before the deadline.** After that, only bug fixes and polish.
- [ ] Rehearse the demo on the deployed URL, not localhost.
- [ ] Record a backup demo video.
- [ ] Prepare a README for judges: the problem, what it does, screenshots, the stack, and how to run it.
- [ ] Make sure seed data is loaded and demo accounts exist.

## Rules check
- [ ] Confirm what the hackathon allows to be built before it starts. Tooling and templates are usually fine; project code usually isn't.
- [ ] Confirm the repo needs to be public for judging, and when.
