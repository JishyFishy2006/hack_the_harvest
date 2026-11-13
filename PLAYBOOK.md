# Hackathon playbook

## Kickoff (first hour)
- [ ] Pick the idea and write the **demo script** (3–5 steps) into `CLAUDE.md`. Cut anything that isn't in it.
- [ ] Pick a stack everyone knows.
- [ ] Create the repo from this template and do the README **Setup**.
- [ ] Define the contracts: API routes and shapes, shared types, DB schema. Commit them first.
- [ ] Split the work by **area** (frontend / backend / data), so parallel PRs rarely touch the same files.

## Hours 1–3: walking skeleton
- [ ] Get frontend → backend → data → **deployed URL** working end to end with fake data.
- [ ] Set up auto-deploy from `main`.
- [ ] After this point, everything is parallel work against the contracts.

## The build
- Write issues using the **Agent task** template: small, with checkable acceptance criteria and the files involved.
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
