---
name: update-dependencies
description: Update the root dependencies of this repo (CDK, pnpm and tooling). Applies minor and patch updates directly, upgrades major versions one step at a time after checking the release notes for breaking changes, and reverts the package and records it in a log when unsure. Does not touch app/. Runs without asking questions, so it can be scheduled. Use when the user asks to update, upgrade, bump or refresh dependencies, packages or libraries, or says the repo is out of date.
---

The instructions for this skill live in `.ai/skills/update-dependencies/SKILL.md`.
Read that file in full and follow it exactly. Paths mentioned in it are relative to the
repository root.
